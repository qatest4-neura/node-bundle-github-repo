# Neuraverse Node Template

A template project for building Neuraverse nodes. Create your node, test it locally with the Mock Runner, and deploy.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- VS Code with [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension (recommended) 

### 1. Open in Dev Container

Open the **repository root** in VS Code and click **"Reopen in Container"** when prompted. Three services start automatically:

| Service | URL |
|---------|-----|
| Mock Runner | http://localhost:8599 |
| Documentation | http://localhost:8089 |

### 2. Create Your Node

Create a directory in `src/` with your node class and schema:

```
src/
  my_node/
    my_node.py
    my_node_schema.json
```

```python
from neuraverse_sdk.node_base import NodeBase

class MyNode(NodeBase):

    def __init__(self):
        super().__init__()

    def on_configure(self, config, dynamic_config=None) -> None:
        pass

    def on_execute(self) -> None:
        input_msg = self.get_data("my_input")
        if input_msg:
            self.publish("my_output", input_msg)

    def on_stop(self) -> None:
        pass

    def on_get_configuration(self):
        return {}
```

### 3. Register It

Add your node to `src/run_nodes.py`:

```python
from my_node.my_node import MyNode

set_node_classes([Node1, Node2, MyNode])
```

### 4. Test with Mock Runner

Open http://localhost:8599, select your node, click **Init Node** then **Configure**, inject inputs, and **Execute**.

## Without Dev Container

```bash
cd node-template
docker compose -f docker-compose-dev.yml up -d
```

## Documentation

Full documentation is served at **http://localhost:8089** when the dev environment is running, or browse the `docs/src/` directory directly:

- [Installation](docs/src/installation.md)
- [Dev Container](docs/src/devcontainer.md)
- [Development](docs/src/development.md)
- [Node Lifecycle](docs/src/node_lifecycle.md)
- [Schema & Configuration](docs/src/schema.md)
- [Deployment](docs/src/deployment.md)
