# Neuraverse Node Template (C++)

A template project for building **C++ Neuraverse nodes** using the
[`neuraverse-node-sdk-cpp`](https://gitlab.hrg.systems/neuraverse/neuraverse-node-sdk/-/tree/main/neuraverse-node-sdk-cpp).
This is the C++ counterpart to the Python [`node-template`](../node-template).

## Quick Start

### Prerequisites

- Docker & Docker Compose
- The combined Python + C++ SDK base image (`neuraverse-node-sdk:latest`) — see below

### 1. Build the SDK Base Image

```bash
cd ../neuraverse-node-sdk
docker compose build    # tags neuraverse-node-sdk:latest
```

### 2. Build & Run Your Nodes

```bash
cd node-template-cpp
docker compose build
docker compose up
```

The container registers nodes against Consul on port `50081`. Verify:

```bash
curl -s localhost:8500/v1/catalog/services | tr ',' '\n' | grep -i node
```

### 3. Create Your Node

Create a header in `src/` with your node class:

```
src/
  my_node/
    MyNode.hpp
    my_node_schema.json
```

```cpp
#include <neuraverse_sdk/NodeBase.hpp>

namespace node_template_cpp
{

class MyNode : public neuraverse::sdk::NodeBase
{
public:
    MyNode() = default;
    ~MyNode() override = default;

    void onExecute() override
    {
        logInfo("MyNode executing");
    }

    void onConfigure(const NodeConfigStringMap& config,
                     const NodeConfigEntryMap* dynamic_config = nullptr) override
    {
    }

    void onStop() override {}

    NodeConfigEntryMap onGetConfiguration() override
    {
        NodeConfigEntryMap entries;
        return entries;
    }
};

} // namespace node_template_cpp
```

### 4. Register It

Add your node to the `node_classes` vector in `src/main.cpp`:

```cpp
#include "my_node/MyNode.hpp"

// Inside main():
node_classes.emplace_back("MyNode",
    []() -> std::unique_ptr<neuraverse::sdk::NodeBase> {
        return std::make_unique<node_template_cpp::MyNode>();
    });
```

### 5. Rebuild & Test

```bash
docker compose build && docker compose up
```

## How C++ Nodes Register in Consul

The `node_classes` vector passed to `NodeManagerService::run(...)` in `src/main.cpp`
determines which nodes are registered:

```cpp
std::vector<std::pair<std::string, neuraverse::sdk::NodeFactory>> node_classes = {
    {"StringPublisher", [] { return std::make_unique<node_template_cpp::StringPublisher>(); }},
    {"Node2", [] { return std::make_unique<node_template_cpp::Node2>(); }},
};
neuraverse::sdk::NodeManagerService::run(node_classes, config);
```

Registration happens inside the SDK:

`NodeManagerService::run` → `NodeController` → `NodesRegistry::addNodeClass` →
`NodeBase::registerNode` → `NodeBase::registerService` →
`ServiceRegistryRepository::registerNode` → Consul `PUT` of
**`capability-<className>`** (e.g. `capability-StringPublisher`).

Note the class name has no required suffix or prefix — call it whatever fits
your node; `StringPublisher`/`Node2` here are plain examples, not a `*Cpp`
naming convention to follow.

The **string key** of each `{name, factory}` pair *is* the capability name
and must equal the schema's `executionContext.className`.

## Wiring to Other Nodes in the Frontend

The node won't appear in the NodeGraph palette until its schema is published:

1. Publish `src/<your_node>/<your_node>_schema.json` via the `publish_schema.py`
   script in `node-template`.
2. Link the resulting `AssetInstance` to your project via Creator Hub.
3. In the editor, wire your node's ports to other nodes.

## Project Structure

```
node-template-cpp/
├── CMakeLists.txt          # Build configuration
├── Dockerfile              # FROM neuraverse-node-sdk:latest
├── docker-compose.yml      # Development compose file
├── entrypoint.sh           # Container entry point (sources ROS, runs binary)
├── config/
│   └── service_config.yaml # gRPC/HTTP/MQTT/Consul config
└── src/
    ├── main.cpp            # Entry point — registers all nodes
    ├── string_publisher/
    │   ├── StringPublisher.hpp         # Example: configurable string publisher
    │   └── string_publisher_schema.json # Schema for NodeGraph frontend
    └── node_2/
        ├── Node2.hpp            # Example: minimal empty node
        └── node_2_schema.json   # Schema for NodeGraph frontend
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `NODE_GRPC_PORT` | `50081` | gRPC server port |
| `NODE_HTTP_PORT` | `8081` | HTTP health-check port |
| `MQTT_BROKER_HOST` | `localhost` | MQTT broker address |
| `MQTT_BROKER_PORT` | `1883` | MQTT broker port |
| `CONSUL_ENDPOINT` | `localhost:8500` | Consul agent endpoint |
| `NODE_ADVERTISE_HOST` | *(empty)* | Hostname to advertise in Consul |
| `ROS_DOMAIN_ID` | `0` | ROS 2 domain isolation |

## Adding Your Own Node

1. Add `src/<your_node>/YourNode.hpp` subclassing `neuraverse::sdk::NodeBase`
   (override `onExecute`, `onConfigure`, `onStop`, `onGetConfiguration`).
2. Register it in the `node_classes` vector in `src/main.cpp`.
3. Add a schema JSON describing its ports and config.
4. `docker compose build && docker compose up`.
