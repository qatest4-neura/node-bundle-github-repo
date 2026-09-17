# Getting Started

## Prerequisites

- **Docker & Docker Compose**
- **VS Code** with the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension (recommended)

## Setting Up the Dev Environment

### Option 1: Dev Container (Recommended)

1. Open the **repository root** in VS Code.
2. Click **"Reopen in Container"** when prompted (or use `Ctrl+Shift+P` → `Dev Containers: Reopen in Container`).
3. Three services start automatically:

| Service | URL | Description |
|---------|-----|-------------|
| Node Template | -- | Your VS Code workspace (terminal access) |
| Mock Runner | [http://localhost:8599](http://localhost:8599) | Test nodes in the browser |
| Documentation | [http://localhost:8089](http://localhost:8089) | This documentation |

### Option 2: Docker Compose (Without VS Code)

```bash
cd node-template
docker compose -f docker-compose-dev.yml up -d
```

## Creating Your First Node

### Step 1: Create the Node Directory

```
src/
  my_node/
    my_node.py
    my_node_schema.json
```

### Step 2: Implement the Node Class

```python title="src/my_node/my_node.py"
from neuraverse_sdk.node_base import NodeBase


class MyNode(NodeBase):

    def __init__(self):
        super().__init__()

    def on_execute(self) -> None:
        """Main logic — read inputs, process, publish outputs."""
        msg = self.get_data("my_input")
        if msg:
            self.log_info(f"Received: {msg.data}")
            self.publish("my_output", msg)

    def on_configure(self, config, dynamic_config=None) -> None:
        """Called when configuration is applied."""
        pass

    def on_stop(self) -> None:
        """Called when the node is stopped."""
        self.log_info("Node stopped")

    def on_get_configuration(self):
        """Return default configuration for the UI."""
        return {}
```

### Step 3: Create the Schema

```json title="src/my_node/my_node_schema.json"
{
  "name": "My Node",
  "type": 1,
  "description": "Processes input and produces output",
  "tags": ["example"],
  "inputs": {
    "my_input": {
      "rosType": "std_msgs/String",
      "edgeType": "NODE_EDGE_TYPE_DATA"
    }
  },
  "outputs": {
    "my_output": {
      "rosType": "std_msgs/String",
      "edgeType": "NODE_EDGE_TYPE_DATA"
    },
    "Start": { "rosType": "Start", "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
    "Stop":  { "rosType": "Stop",  "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
    "Error": { "rosType": "Error", "edgeType": "NODE_EDGE_TYPE_TRIGGER" }
  },
  "executionContext": {
    "className": "MyNode"
  },
  "configuration": {}
}
```

!!! warning "className must match"
    `executionContext.className` must **exactly** match your Python class name. `MyNode` in the schema must correspond to `class MyNode(NodeBase)` in your code.

### Step 4: Register the Node

Edit `src/run_nodes.py`:

```python title="src/run_nodes.py"
from neuraverse_sdk.node_manager_service import run, set_node_classes
from node_1.node_1 import Node1
from node_2.node_2 import Node2
from my_node.my_node import MyNode  # Add your import

def main():
    set_node_classes([Node1, Node2, MyNode])  # Add your class
    run()

if __name__ == "__main__":
    main()
```

### Step 5: Test with Mock Runner

1. Open [http://localhost:8599](http://localhost:8599)
2. Select **MyNode** from the sidebar
3. Click **Init Node** to load the configuration form
4. Click **Configure** to apply configuration
5. Inject test data into input ports
6. Click **Execute** and observe outputs and logs
7. After code changes, click **Reload Code** to pick up changes without restarting

## Best Practices

- **One directory per node** — keep each node isolated in `src/my_node/`
- **Use logging** — `self.log_info()`, `self.log_error()`, etc. instead of `print()`
- **Name clearly** — class names and file names should be descriptive
- **Always call `super().__init__()`** in your `__init__` method
