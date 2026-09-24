# Neuraverse Node Template

Welcome to the **Neuraverse Node Template** documentation. This project is your starting point for building custom nodes within the Neuraverse ecosystem.

## What is a Node?

A node is a self-contained processing unit that receives data on **input ports**, processes it, and publishes results on **output ports**. Nodes are orchestrated into graphs where data flows between them automatically.

## Project Structure

```
node-template/                  (repository root)
├── node-template/              (your node project)
│   ├── src/                    (node implementations)
│   │   ├── node_1/             (example node)
│   │   │   ├── node_1.py
│   │   │   └── node_1_schema.json
│   │   └── run_nodes.py        (entry point)
│   ├── config/                 (service configuration)
│   ├── wheels/                 (bundled SDK dependencies)
│   ├── Dockerfile
│   ├── docker-compose-dev.yml
│   └── pyproject.toml
├── neuraverse-mock-runner/     (local testing tool)
├── docs/                       (this documentation)
└── .devcontainer/              (VS Code dev container)
```

## Quick Start

1. Open the repository in VS Code and **Reopen in Container**
2. Create your node in `node-template/src/`
3. Test it at [http://localhost:8599](http://localhost:8599) (Mock Runner)
4. Browse these docs at [http://localhost:8089](http://localhost:8089)

!!! info "Multiple Nodes"
    You can host multiple nodes in a single project. Register each one in `run_nodes.py`.

## Next Steps

- [Getting Started](getting_started.md) -- Set up your environment and create your first node
- [Node API Reference](api_reference.md) -- All methods available in your node
- [Compatible I/O Types](compatible_types.md) -- All ROS2 and custom message types for node ports
- [Schema Reference](schema.md) -- Define your node's interface
