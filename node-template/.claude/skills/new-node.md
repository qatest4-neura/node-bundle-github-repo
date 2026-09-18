# Skill: new-node

Scaffold a new Neuraverse node that extends `NodeBase`.

## Instructions

When the user invokes `/new-node`, do the following:

1. **Ask for the node name** if not already provided (e.g. `MathNode`, `ImageProcessingNode`).
   - Name must be PascalCase and end with `Node`.

2. **Ask for a brief description** of what the node does (1–2 sentences). Skip if the user already gave one.

3. **Ask for input and output port names** (comma-separated). Use sensible defaults if the user is unsure:
   - Default input: `input`
   - Default output: `output`

4. **Ask for any configuration parameters** the node needs (key: type pairs, e.g. `threshold: float, mode: str`). Skip if none.

5. **Generate the node file** at `src/<snake_case_name>/<snake_case_name>.py` with:

```python
from google.protobuf.internal.containers import ScalarMap
from neuraverse_sdk import NodeBase
from neuraverse_sdk.utils.exceptions import NodeConfigurationError, NodeExecutionError


class {NodeName}(NodeBase):
    """{Description}"""

    def on_configure(self, config: ScalarMap[str, str]) -> None:
        """Receive configuration from the Neuraverse UI/Runtime."""
        # TODO: parse config parameters
        # Example: self.threshold = float(config.get("threshold", "0.5"))
        pass

    def on_execute(self) -> None:
        """Main processing logic — called each execution cycle."""
        try:
            # TODO: read input ports
            # data = self.get_data("{input_port}")

            # TODO: process data

            # TODO: publish to output ports
            # self.publish("{output_port}", result)
            pass
        except Exception as e:
            raise NodeExecutionError(f"{NodeName} execution failed: {e}") from e

    def on_stop(self) -> None:
        """Release any resources acquired during on_configure."""
        self.log_info("{NodeName} stopped.")

    def on_get_configuration(self) -> dict[str, str]:
        """Return current configuration state for the UI."""
        return {}
```

6. **Generate the entry point** at `src/<snake_case_name>/main.py`:

```python
from neuraverse_sdk import run, set_node_classes
from .<snake_case_name> import {NodeName}

set_node_classes([{NodeName}])
run()
```
7. ** Node Schema** at `src/<snake_case_name>/<snake_case_name>_schema.json`:

```json
{
  "id": "",
  "name": "Node 1",
  "type": 1,
  "description": "Node 1 description",
  "tags": [
    "tag1",
    "tag2"
  ],
  "inputs": {
    "<input_port>": {
      "rosType": "<rosType>",
      "type": 1,
      "requestTarget": "",
      "edgeType": 1,
      "defaultValue": "default"
    },
    "<input_port>": {
      "rosType": "<rosType>",
      "type": 1,
      "requestTarget": "",
      "edgeType": 1,
      "defaultValue": "default"
    }
  },
  "outputs": {
    "Start": {
      "rosType": "Start",
      "edgeType": "NODE_EDGE_TYPE_TRIGGER"
    },
    "Stop": {
      "rosType": "Stop",
      "edgeType": "NODE_EDGE_TYPE_TRIGGER"
    },
    "Error": {
      "rosType": "Error",
      "edgeType": "NODE_EDGE_TYPE_TRIGGER"
    }
  },
  "errorOutputs": {},
  "dataFlowEntry": {},
  "assetInstanceId": "",
  "triggerFlowEntry": {},
  "executionContext": {
    "type": "EXECUTION_TARGET_TYPE_GRPC",
    "target": "",
    "className": "Node1"
  },
  "nodeBaseUrl": "",
  "executionStatus": {
    "state": "EXECUTION_STATE_IDLE",
    "lastUpdate": "",
    "statusMessage": "Executing Node 1"
  },
  "dataFlowCommunicationType": "DATA_FLOW_COMMUNICATION_TYPE_ROS",
  "configuration": {
    "<config_key>": "<config_value>"
  },
  "assetInstanceConfigurationKeys": {},
  "resourceVersion": 101,
  "history": []
}
```

8. **Print a summary** of what was generated, including:
   - File paths created
   - Ports defined
   - Config parameters defined
   - Next steps: implement `on_execute`, write tests with `/test-node`, build Docker image

## Rules

- Use `snake_case` for file names, `PascalCase` for class names.
- Never use `print()` — use `self.log_info()`, `self.log_warning()`, `self.log_error()`.
- Never put side-effectful code in `__init__`; all setup belongs in `on_configure()`.
- Always wrap `on_execute` body in a `try/except` that raises `NodeExecutionError`.
- Add type hints to all methods.
