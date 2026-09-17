# Neuraverse Mock Runner

Test Neuraverse nodes locally without MQTT, Consul, ROS2, or any external infrastructure. The Mock Runner simulates the orchestrator — configure, execute, inject data, and view outputs — all in-memory.

## Quick Start

### With Docker Compose (recommended)

The mock runner is designed to run alongside a node project via `docker-compose-dev.yml` in the node template:

```bash
cd your-node-project
docker compose -f docker-compose-dev.yml up -d
```

Web UI: **http://localhost:8599**

To point to a custom mock runner location:
```bash
MOCK_RUNNER_PATH=/path/to/neuraverse-mock-runner docker compose -f docker-compose-dev.yml up -d
```

### Standalone (without Docker)

```bash
cd neuraverse-mock-runner
bash install.sh
```

**CLI:**
```bash
poetry run python -m mock_runner.cli --project /path/to/node-project
```

**Web UI:**
```bash
poetry run python -m mock_runner.web.app --project /path/to/node-project
```

Open http://localhost:8599

---

## Web UI

The browser interface provides:

- **Sidebar** — Node list + key-value configuration form
- **Action bar** — Execute, Stop, Clear Outputs, Reload Code buttons
- **Input Ports** — Per-port type-aware forms (text, numbers, booleans, file uploads, Twist fields)
- **Published Outputs** — Shows data the node published on each output port
- **Node Logs** — Timestamped, color-coded log messages (INFO, WARNING, ERROR, DEBUG)
- **Status Log** — State machine transitions (IDLE -> CONFIGURED -> RUNNING -> ...)
- **Dark mode** — Toggle via header button

**Workflow:** Select node -> Configure -> Inject inputs -> Execute -> View outputs & logs -> Reload Code after edits

---

## How It Works

The Mock Runner bypasses `NodeBase.configure()` (which needs real MQTT/ROS) and instead:

1. Creates the node instance directly
2. Assigns **MockDataFlow** (in-memory) for `publish()` and `get_data()`
3. Assigns **MockTrigger** (no-op) for trigger signals
4. Builds a protobuf `Node` message from the node's `*_schema.json`
5. Calls `on_configure(config)` with key-value pairs
6. Uses the real **StateMachine** for state tracking
7. Calls `on_execute()` for execution

### MockDataFlow
- `publish()` — captures output data in-memory
- `inject_input()` — simulates incoming data (writes to blackboard, signals event)
- `get_data()` — returns immediately (timeout=0) from in-memory blackboard

### MockTrigger
- Records `trigger_next_node()` calls for inspection
- Does not connect to any broker

### ROS2 Types
Mock ROS2 message objects mimic real ones (e.g., `MockMessage(data="hello")` for `std_msgs/String`). Supported types:

| Type | Form Field |
|------|-----------|
| `std_msgs/String` | Text input |
| `std_msgs/Float32`, `Float64` | Number input |
| `std_msgs/Int32`, `Int64` | Integer input |
| `std_msgs/Bool` | Toggle switch |
| `std_msgs/Float32MultiArray` | Comma-separated values |
| `sensor_msgs/CompressedImage` | File upload + format |
| `geometry_msgs/Twist` | 6 number fields (linear/angular xyz) |
| `audio_common_msgs/AudioData` | File upload |

---

## Architecture

```
mock_runner/
├── mock_dataflow.py      # In-memory IDataFlow
├── mock_trigger.py       # No-op ITrigger
├── ros_types.py          # Mock ROS2 message types + builder
├── proto_builder.py      # Schema JSON -> Node protobuf
├── node_loader.py        # Discovers NodeBase subclasses
├── runner.py             # Core engine (shared by CLI and Web)
├── cli.py                # Interactive terminal CLI
└── web/
    ├── app.py            # FastAPI server
    └── static/           # HTML/CSS/JS (vanilla, no build step)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/nodes` | List discovered nodes |
| GET | `/api/nodes/{name}/schema` | Get node schema JSON |
| POST | `/api/configure` | Configure node `{class_name, config}` |
| POST | `/api/execute` | Execute current node |
| POST | `/api/inject` | Inject input `{port_name, ros_type, fields}` |
| GET | `/api/outputs` | Get published outputs |
| GET | `/api/state` | Get current state + node name |
| GET | `/api/status-log` | State transition log |
| GET | `/api/logs` | Node log messages |
| POST | `/api/logs/clear` | Clear log buffer |
| GET | `/api/ros-types` | List all ROS2 type schemas |
| GET | `/api/ros-types/{type}` | Get field schema for a type |
| POST | `/api/reload` | Reload node code from disk |
| POST | `/api/stop` | Stop current node |

## Node Discovery

The mock runner scans the project's `src/` directory for:
1. Python files containing classes that inherit from `NodeBase`
2. `*_schema.json` files alongside each node module

Expected project structure:
```
node-project/
├── src/
│   ├── my_node/
│   │   ├── my_node.py              # class MyNode(NodeBase): ...
│   │   └── my_node_schema.json     # Node schema
│   └── run_nodes.py
├── config/
└── pyproject.toml
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_RUNNER_PROJECT` | `.` | Path to node project (alternative to `--project`) |
| `MOCK_RUNNER_PATH` | `../../neuraverse-mock-runner` | Used in docker-compose-dev.yml to locate this package |
