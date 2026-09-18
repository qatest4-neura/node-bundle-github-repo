"""In-memory dataflow adapter for testing nodes without MQTT/ROS infrastructure."""

import threading
from collections import defaultdict
from typing import Any, Optional

from neuraverse.models.v1.gen.business.node_graph_pb2 import DataFlowNodeEntry
from neuraverse_sdk.dataflow.i_dataflow import IDataFlow


class MockDataFlow(IDataFlow):
    """
    In-memory IDataFlow implementation that captures published outputs
    and allows injecting input data programmatically.

    Inherits blackboard, _data_events, get_data(), and _save_data() from IDataFlow.
    """

    def __init__(self):
        super().__init__()
        self.captured_outputs: dict[str, list[Any]] = defaultdict(list)
        self.input_topics: dict[str, dict] = {}
        self.output_topics: dict[str, dict] = {}
        self.connected_ports: dict[str, bool] = {}

    def init(self, config):
        pass

    def configure(self, node_data_flow_entry: DataFlowNodeEntry) -> None:
        """Parse DataFlowNodeEntry to set up input/output topic metadata."""
        for output_name, output_conn in node_data_flow_entry.outputPorts.items():
            topic_name = f"{node_data_flow_entry.name}/{output_name}"
            self.output_topics[output_name] = {
                "topic_name": topic_name,
                "ros_type": output_conn.rosType,
            }

        for input_name, input_cfg in node_data_flow_entry.inputPorts.items():
            ros_type = input_cfg.rosType
            source_connections = list(input_cfg.sourceConnection)
            topic_name = source_connections[0] if source_connections else f"mock/{input_name}"

            self.input_topics[input_name] = {
                "topic_name": topic_name,
                "ros_type": ros_type,
            }
            self.connected_ports[input_name] = True
            self._data_events[input_name] = threading.Event()

    def destroy(self) -> None:
        self.captured_outputs.clear()
        self.blackboard.clear()
        for event in self._data_events.values():
            event.clear()
        self._data_events.clear()
        self.input_topics.clear()
        self.output_topics.clear()
        self.connected_ports.clear()

    def publish(self, target: Any, message: Any, meta_data: Any = None) -> None:
        """Capture published output and print it."""
        self.captured_outputs[target].append(message)
        print(f"  [OUTPUT] {target}: {_format_message(message)}")

    def get_data(self, placeholder: str, timeout: Optional[float] = 0) -> Any:
        """Override to return immediately (timeout=0) instead of waiting 1s per port."""
        return super().get_data(placeholder, timeout)

    def wait_for_message(self, subscription: Any, timeout: float = -1.0) -> tuple[bool, Any]:
        effective_timeout = None if timeout < 0 else timeout
        event = self._data_events.get(subscription)
        if event is None:
            return (False, None)
        received = event.wait(effective_timeout)
        if not received:
            return (False, None)
        with self.blackboard_lock:
            return (True, self.blackboard.get(subscription))

    def get_connected_ports(self) -> dict[str, bool]:
        return self.connected_ports

    def get_input_topics(self) -> dict[str, dict]:
        return self.input_topics

    def get_output_topics(self) -> dict[str, dict]:
        return self.output_topics

    def handle_message(self, input_name: str, msg: Any, topic_info: dict[str, Any]):
        pass

    # --- Mock-specific methods ---

    def inject_input(self, port_name: str, data: Any) -> None:
        """Simulate incoming data on an input port.

        Uses IDataFlow._save_data() which writes to blackboard and sets the
        threading event, so the node's get_data(port_name) will return this data.
        """
        if port_name not in self._data_events:
            self._data_events[port_name] = threading.Event()
        topic_info = self.input_topics.get(port_name, {})
        self._save_data(data, port_name, topic_info)

    def get_published_data(self) -> dict[str, list[Any]]:
        """Return all captured output data."""
        return dict(self.captured_outputs)

    def clear_outputs(self) -> None:
        """Clear captured outputs (keeps input state)."""
        self.captured_outputs.clear()


def _format_message(msg: Any) -> str:
    """Best-effort human-readable representation of a message."""
    if hasattr(msg, "data"):
        return repr(msg.data)
    if hasattr(msg, "DESCRIPTOR"):
        # Protobuf message
        return str(msg)
    return repr(msg)
