"""Build protobuf Node messages from node schema JSON files."""

import uuid

from google.protobuf.json_format import ParseDict
from neuraverse.models.v1.gen.business.node_graph_pb2 import Node, NodeConfigEntry


def build_node_from_schema(
    schema: dict,
    config: dict[str, str] | None = None,
    node_id: str | None = None,
    dynamic_config: dict[str, dict] | None = None,
) -> Node:
    """Build a protobuf Node message from a node's schema JSON.

    Args:
        schema: Parsed JSON from a node's *_schema.json file.
        config: Runtime configuration key-value pairs.
        node_id: Optional node ID (auto-generated if not provided).

    Returns:
        A fully populated Node protobuf message ready for mock configuration.
    """
    config = config or {}
    node_id = node_id or f"mock-{uuid.uuid4().hex[:8]}"

    node = Node()
    node.id = node_id
    node.name = schema.get("name", "MockNode")

    # Execution context
    exec_ctx = schema.get("executionContext", {})
    node.executionContext.className = exec_ctx.get("className", "")
    if exec_ctx.get("target"):
        node.executionContext.target = exec_ctx["target"]

    # Legacy configuration — plain string map
    for k, v in config.items():
        node.configuration[k] = str(v)

    # Dynamic configuration — typed NodeConfigEntry messages
    if dynamic_config:
        for k, v in dynamic_config.items():
            entry = NodeConfigEntry()
            if isinstance(v, dict):
                ParseDict(v, entry)
            node.dynamicConfiguration[k].CopyFrom(entry)

    # Inputs
    for name, io_def in schema.get("inputs", {}).items():
        node.inputs[name].rosType = io_def.get("rosType", "")
        edge_type_str = io_def.get("edgeType", "")
        if edge_type_str:
            _set_edge_type(node.inputs[name], edge_type_str)

    # Outputs
    for name, io_def in schema.get("outputs", {}).items():
        node.outputs[name].rosType = io_def.get("rosType", "")
        edge_type_str = io_def.get("edgeType", "")
        if edge_type_str:
            _set_edge_type(node.outputs[name], edge_type_str)

    # DataFlowEntry — output ports
    node.dataFlowEntry.id = node_id
    node.dataFlowEntry.name = schema.get("name", "MockNode")
    for name, io_def in schema.get("outputs", {}).items():
        edge_type = io_def.get("edgeType", "")
        if edge_type == "NODE_EDGE_TYPE_TRIGGER":
            continue  # Triggers go in triggerFlowEntry, not dataflow
        node.dataFlowEntry.outputPorts[name].rosType = io_def.get("rosType", "")

    # DataFlowEntry — input ports
    for name, io_def in schema.get("inputs", {}).items():
        edge_type = io_def.get("edgeType", "")
        if edge_type == "NODE_EDGE_TYPE_TRIGGER":
            continue
        node.dataFlowEntry.inputPorts[name].rosType = io_def.get("rosType", "")

    # TriggerFlowEntry
    node.triggerFlowEntry.id = node_id
    node.triggerFlowEntry.name = schema.get("name", "MockNode")
    for name, io_def in schema.get("outputs", {}).items():
        if io_def.get("edgeType") == "NODE_EDGE_TYPE_TRIGGER":
            node.triggerFlowEntry.outputTriggers[name] = ""
    for name, io_def in schema.get("inputs", {}).items():
        if io_def.get("edgeType") == "NODE_EDGE_TYPE_TRIGGER":
            node.triggerFlowEntry.inputTriggers[name].rosType = io_def.get("rosType", "")

    return node


def _set_edge_type(node_io, edge_type_str: str) -> None:
    """Set edgeType on a NodeIO protobuf field from string."""
    from neuraverse.models.v1.gen.business.node_graph_pb2 import NodeEdgeType

    mapping = {
        "NODE_EDGE_TYPE_DATA": NodeEdgeType.NODE_EDGE_TYPE_DATA,
        "NODE_EDGE_TYPE_TRIGGER": NodeEdgeType.NODE_EDGE_TYPE_TRIGGER,
    }
    if edge_type_str in mapping:
        node_io.edgeType = mapping[edge_type_str]
