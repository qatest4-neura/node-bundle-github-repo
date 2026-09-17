"""Core MockRunner engine — shared by CLI and Web UI."""

import importlib
import queue
import time
import traceback
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

from google.protobuf.json_format import MessageToDict
from neuraverse.models.v1.gen.business.node_graph_pb2 import ExecutionState, NodeConfigEntry
from neuraverse_sdk.node_base import NodeBase
from neuraverse_sdk.state_machine import IdleState, StateMachine

from mock_runner.mock_dataflow import MockDataFlow
from mock_runner.mock_trigger import MockTrigger
from mock_runner.node_loader import discover_nodes
from mock_runner.proto_builder import build_node_from_schema
from mock_runner.ros_types import build_mock_message, get_type_schema


# Human-readable state names
_STATE_NAMES = {
    ExecutionState.EXECUTION_STATE_IDLE: "IDLE",
    ExecutionState.EXECUTION_STATE_CONFIGURED: "CONFIGURED",
    ExecutionState.EXECUTION_STATE_RUNNING: "RUNNING",
    ExecutionState.EXECUTION_STATE_PAUSED: "PAUSED",
    ExecutionState.EXECUTION_STATE_ERROR: "ERROR",
    ExecutionState.EXECUTION_STATE_STOPPED: "STOPPED",
}


def _state_name(state: int) -> str:
    return _STATE_NAMES.get(state, f"UNKNOWN({state})")


def _create_mock_service_config() -> MagicMock:
    """Create a minimal mock NodeServiceConfig that satisfies node.initialize()."""
    config = MagicMock()
    config.mqtt = MagicMock()
    config.registry_config = MagicMock()
    config.registry_config.registry_endpoint = ""
    config.registry_config.node_cluster_target = ""
    config.registry_config.node_external_target = ""
    config.grpc = MagicMock()
    config.grpc.address = "0.0.0.0"
    config.grpc.port = 50051
    return config


class MockRunner:
    """Core engine for configuring, executing, and inspecting nodes locally."""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.available_nodes: dict[str, dict] = {}
        self.current_node: NodeBase | None = None
        self.current_node_name: str | None = None
        self.mock_dataflow: MockDataFlow | None = None
        self.mock_trigger: MockTrigger | None = None
        self.status_queue: queue.Queue | None = None
        self.status_log: list[dict] = []
        self.node_logs: list[dict] = []
        self._initialized: bool = False
        self._load_nodes()

    def _load_nodes(self) -> None:
        self.available_nodes = discover_nodes(self.project_path)

    def reload_nodes(self) -> dict:
        """Reload node modules from disk so code changes take effect.

        If a node is currently configured, it is stopped and the same node
        class is re-configured with the same config.
        """
        self._initialized = False
        prev_name = self.current_node_name
        prev_config = None
        if self.current_node and prev_name:
            prev_config = {}
            try:
                prev_config = self.current_node.on_get_configuration()
            except Exception:
                pass
            self.stop_node()

        # Reload the Python modules that define node classes
        for info in self.available_nodes.values():
            module = info["class"].__module__
            if module in importlib.sys.modules:
                try:
                    importlib.reload(importlib.sys.modules[module])
                except Exception:
                    pass

        # Re-discover nodes (picks up reloaded classes + new nodes)
        self._load_nodes()
        node_names = [n["name"] for n in self.list_nodes()]

        # Re-configure the previously active node if it still exists
        reconfigured = False
        if prev_name and prev_name in self.available_nodes:
            result = self.configure_node(prev_name, prev_config or {})
            reconfigured = result.get("success", False)

        return {
            "success": True,
            "nodes": node_names,
            "reconfigured": prev_name if reconfigured else None,
        }

    def list_nodes(self) -> list[dict]:
        """Return available node info for display."""
        result = []
        for name, info in self.available_nodes.items():
            schema = info.get("schema")
            result.append({
                "name": name,
                "description": schema.get("description", "") if schema else "",
                "has_schema": schema is not None,
                "inputs": list((schema or {}).get("inputs", {}).keys()),
                "outputs": list((schema or {}).get("outputs", {}).keys()),
                "configuration_keys": list((schema or {}).get("configuration", {}).keys()),
            })
        return result

    def get_node_schema(self, class_name: str) -> dict | None:
        """Return the raw schema JSON for a node class."""
        info = self.available_nodes.get(class_name)
        return info["schema"] if info else None

    def init_node(self, class_name: str) -> dict:
        """Initialize a node and return its default typed configuration.

        This mirrors the real SDK's initialize flow: instantiate the node,
        set up mock infrastructure, and call on_get_configuration() to retrieve
        the node's default NodeConfigEntry configuration.
        """
        # Stop current node if one exists
        if self.current_node:
            self.stop_node()

        info = self.available_nodes.get(class_name)
        if not info:
            return {"success": False, "error": f"Node class '{class_name}' not found"}

        node_class = info["class"]
        schema = info.get("schema") or _minimal_schema(class_name)

        try:
            # 1. Instantiate and initialize
            node: NodeBase = node_class()
            mock_service_config = _create_mock_service_config()
            node.node_service_config = mock_service_config

            # 2. Replace state machine with a fresh one
            node.state_machine = StateMachine(IdleState())

            # 3. Create mock adapters
            self.mock_dataflow = MockDataFlow()
            self.mock_trigger = MockTrigger()
            node.data_flow = self.mock_dataflow
            node.trigger = self.mock_trigger

            # 4. Build protobuf Node from schema (no config yet)
            node_proto = build_node_from_schema(schema)
            node.node_info = node_proto
            node.node_inputs = dict(node_proto.inputs)
            node.node_outputs = dict(node_proto.outputs)
            node.node_trigger_inputs = dict(node_proto.triggerFlowEntry.inputTriggers)
            node.node_trigger_outputs = dict(node_proto.triggerFlowEntry.outputTriggers)

            # 5. Initialize state machine with status queue
            self.status_queue = queue.Queue()
            self.status_log = []
            node.state_machine.initialize(self.status_queue, node_proto.id)

            # 6. Configure mock dataflow with the protobuf entry
            self.mock_dataflow.configure(node_proto.dataFlowEntry)

            # 7. Patch logging to capture node logs
            self.node_logs = []
            self._patch_node_logging(node)

            # 8. Get default typed configuration from the node
            raw_config = node.on_get_configuration()
            serialized = {}
            for key, entry in raw_config.items():
                if isinstance(entry, NodeConfigEntry):
                    serialized[key] = MessageToDict(
                        entry,
                        preserving_proto_field_name=True,
                        always_print_fields_with_no_presence=True,
                    )
                else:
                    # Legacy fallback for nodes returning plain strings
                    serialized[key] = entry

            self.current_node = node
            self.current_node_name = class_name
            self._initialized = True
            self._drain_status_queue()

            return {
                "success": True,
                "class_name": class_name,
                "node_id": node_proto.id,
                "node_name": node_proto.name,
                "state": self.get_state(),
                "configuration": serialized,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def configure_node(self, class_name: str, config: dict[str, str] | None = None, dynamic_config: dict[str, dict] | None = None) -> dict:
        """Configure a node instance with mock infrastructure.

        This bypasses NodeBase.configure() (which needs real MQTT/ROS) and instead
        sets up mock adapters and calls on_configure() directly.

        If init_node() was called first for the same class, reuses the already
        initialized node instance instead of re-instantiating.
        """
        config = config or {}
        info = self.available_nodes.get(class_name)
        if not info:
            return {"success": False, "error": f"Node class '{class_name}' not found"}

        node_class = info["class"]
        schema = info.get("schema") or _minimal_schema(class_name)

        try:
            # Reuse initialized node if available for the same class
            if self._initialized and self.current_node and self.current_node_name == class_name:
                node = self.current_node
            else:
                # 1. Instantiate and initialize from scratch
                node: NodeBase = node_class()
                mock_service_config = _create_mock_service_config()
                node.node_service_config = mock_service_config

                # 2. Replace state machine with a fresh one
                node.state_machine = StateMachine(IdleState())

                # 3. Create mock adapters
                self.mock_dataflow = MockDataFlow()
                self.mock_trigger = MockTrigger()
                node.data_flow = self.mock_dataflow
                node.trigger = self.mock_trigger

                # 5. Initialize state machine with status queue
                self.status_queue = queue.Queue()
                self.status_log = []
                node.state_machine.initialize(self.status_queue, f"mock-{class_name}")

                # 9. Patch logging to capture node logs
                self.node_logs = []
                self._patch_node_logging(node)

            # 4. Build protobuf Node from schema with config
            node_proto = build_node_from_schema(schema, config, dynamic_config=dynamic_config)
            node.node_info = node_proto
            node.node_inputs = dict(node_proto.inputs)
            node.node_outputs = dict(node_proto.outputs)
            node.node_trigger_inputs = dict(node_proto.triggerFlowEntry.inputTriggers)
            node.node_trigger_outputs = dict(node_proto.triggerFlowEntry.outputTriggers)

            # 6. Configure mock dataflow with the protobuf entry
            self.mock_dataflow.configure(node_proto.dataFlowEntry)

            # 7. Call the node's on_configure with both legacy and dynamic config
            node.on_configure(node_proto.configuration, node_proto.dynamicConfiguration or None)

            # 8. Transition to CONFIGURED
            node.state_machine.configure()

            self.current_node = node
            self.current_node_name = class_name
            self._initialized = False
            self._drain_status_queue()

            return {
                "success": True,
                "node_id": node_proto.id,
                "node_name": node_proto.name,
                "state": self.get_state(),
                "input_ports": [
                    {"name": name, "ros_type": info.get("ros_type", "")}
                    for name, info in self.mock_dataflow.input_topics.items()
                ],
                "output_ports": [
                    {"name": name, "ros_type": info.get("ros_type", "")}
                    for name, info in self.mock_dataflow.output_topics.items()
                ],
            }
        except Exception as e:
            self._initialized = False
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

    def execute_node(self) -> dict:
        """Execute the current node's on_execute()."""
        if not self.current_node:
            return {"success": False, "error": "No node configured"}

        node = self.current_node
        self.mock_dataflow.clear_outputs()
        self.mock_trigger.triggered.clear()

        try:
            start_time = time.time()
            node.state_machine.execute()
            node.on_execute()
            execution_time = time.time() - start_time
            node.state_machine.configure()  # Back to CONFIGURED

            self._drain_status_queue()

            return {
                "success": True,
                "execution_time": round(execution_time, 3),
                "state": self.get_state(),
                "outputs": self._serialize_outputs(self.mock_dataflow.get_published_data()),
                "triggers_fired": self.mock_trigger.get_triggered(),
            }
        except Exception as e:
            try:
                node.state_machine.error(str(e))
            except Exception:
                pass
            self._drain_status_queue()
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "state": self.get_state(),
                "outputs": self._serialize_outputs(self.mock_dataflow.get_published_data()),
            }

    def inject_input(self, port_name: str, ros_type: str = "", fields: dict | None = None, data: Any = None) -> dict:
        """Inject data on an input port so the node can read it via get_data().

        If ros_type and fields are provided, builds a mock ROS2 message.
        Otherwise falls back to injecting raw data.
        """
        if not self.current_node:
            return {"success": False, "error": "No node configured"}
        if not self.mock_dataflow:
            return {"success": False, "error": "Dataflow not initialized"}

        if ros_type and fields is not None:
            try:
                msg = build_mock_message(ros_type, fields)
            except Exception as e:
                return {"success": False, "error": f"Failed to build message: {e}"}
        else:
            msg = data

        self.mock_dataflow.inject_input(port_name, msg)
        return {"success": True, "port": port_name, "ros_type": ros_type}

    def get_outputs(self) -> dict:
        """Get all published outputs from the last (or current) execution."""
        if not self.mock_dataflow:
            return {"outputs": {}}
        return {"outputs": self._serialize_outputs(self.mock_dataflow.get_published_data())}

    def get_state(self) -> str:
        """Get current state machine state as a human-readable string."""
        if not self.current_node:
            return "NO_NODE"
        return _state_name(self.current_node.state_machine.get_state())

    def stop_node(self) -> dict:
        """Stop the current node."""
        if not self.current_node:
            return {"success": False, "error": "No node configured"}

        try:
            node = self.current_node
            node.state_machine.stop()
            node.on_cleanup()
            node.on_stop()
            self._drain_status_queue()
            state = self.get_state()
            self.current_node = None
            self.current_node_name = None
            self._initialized = False
            return {"success": True, "state": state}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_status_log(self) -> list[dict]:
        """Return all status transitions that have been recorded."""
        self._drain_status_queue()
        return list(self.status_log)

    def get_logs(self) -> list[dict]:
        """Return captured node logs."""
        return list(self.node_logs)

    def clear_logs(self) -> None:
        """Clear captured node logs."""
        self.node_logs.clear()

    def _patch_node_logging(self, node: NodeBase) -> None:
        """Replace node's log methods to capture messages."""
        def _make_logger(level: str):
            def _log(message: str, **kwargs):
                self.node_logs.append({
                    "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                    "level": level,
                    "message": message,
                })
            return _log

        node.log_info = _make_logger("INFO")
        node.log_error = lambda message, exception=None: self.node_logs.append({
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "level": "ERROR",
            "message": f"{message} {exception}" if exception else message,
        })
        node.log_warning = _make_logger("WARNING")
        node.log_debug = _make_logger("DEBUG")

    def _drain_status_queue(self) -> None:
        """Read all pending status updates from the queue into status_log."""
        if not self.status_queue:
            return
        while True:
            try:
                item = self.status_queue.get_nowait()
                if item is None:
                    break
                if isinstance(item, dict):
                    item["state_name"] = _state_name(item.get("state", 0))
                    self.status_log.append(item)
            except queue.Empty:
                break

    def _serialize_outputs(self, outputs: dict[str, list]) -> dict[str, list[str]]:
        """Convert output messages to JSON-serializable strings."""
        result = {}
        for port, messages in outputs.items():
            result[port] = [self._msg_to_str(m) for m in messages]
        return result

    def _msg_to_str(self, msg: Any) -> str:
        """Best-effort serialization of a message to string."""
        if isinstance(msg, (str, int, float, bool)):
            return str(msg)
        if hasattr(msg, "data"):
            return repr(msg.data)
        if isinstance(msg, dict):
            return str(msg)
        return repr(msg)


def _minimal_schema(class_name: str) -> dict:
    """Create a minimal schema when no JSON file is found."""
    return {
        "name": class_name,
        "executionContext": {"className": class_name},
        "inputs": {},
        "outputs": {},
        "configuration": {},
    }
