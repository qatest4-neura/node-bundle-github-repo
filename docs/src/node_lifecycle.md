# Node Lifecycle

Every node inherits from `NodeBase` and follows a strict state machine lifecycle.

## States

```
IDLE ──[configure]──> CONFIGURED ──[execute]──> RUNNING ──> CONFIGURED
                          ^            │                        │
                          │        [pause]──> PAUSED ──[resume]─┘
                          │
                       STOPPED <──[stop]── (any state)
                       ERROR   <──[error]── (any state)
```

| State | Description |
|-------|-------------|
| **IDLE** | Node created, waiting for configuration. |
| **CONFIGURED** | `on_configure()` called successfully, ready to execute. |
| **RUNNING** | `on_execute()` in progress. |
| **PAUSED** | Execution paused via `on_pause()`. |
| **STOPPED** | Node stopped, resources cleaned up. |
| **ERROR** | An exception occurred. Can recover via reconfigure. |

## Lifecycle Methods

These are the methods you implement in your node class. They are called by the orchestrator at the appropriate lifecycle stage.

### Required Methods

#### `on_configure(self, config, dynamic_config=None)`

Called when the node receives configuration. This happens **before** execution.

- `config` — Legacy string key-value pairs (`ScalarMap[str, str]`)
- `dynamic_config` — Typed configuration entries (`MessageMap[str, NodeConfigEntry]` or `None`)

```python
def on_configure(self, config, dynamic_config=None) -> None:
    if dynamic_config:
        for key, entry in dynamic_config.items():
            self.log_info(f"Config [{key}]: {entry}")
```

#### `on_execute(self)`

The main execution logic. Called once per execution request. This is **not** a loop — it runs once and returns.

```python
def on_execute(self) -> None:
    msg = self.get_data("input_port")
    if msg:
        result = process(msg)
        self.publish("output_port", result)
```

!!! note
    If you need continuous processing, implement your own loop inside `on_execute()`. In that case, check for pause/stop signals within the loop.

#### `on_stop(self)`

Called when the node receives a stop signal. Use this to signal threads to stop and release resources.

```python
def on_stop(self) -> None:
    self.log_info("Shutting down")
```

#### `on_get_configuration(self)`

Return the node's default typed configuration. The orchestrator calls this during initialization to discover what configuration the node supports. See [Schema - Typed Configuration](schema.md#typed-configuration-nodeconfigentry) for details.

```python
def on_get_configuration(self) -> dict[str, NodeConfigEntry]:
    return {}
```

### Optional Methods

| Method | Default Behavior | When Called |
|--------|-----------------|------------|
| `on_pause(self)` | Logs "Node paused" | Node is paused |
| `on_resume(self)` | Logs "Node resumed" | Node resumes from pause |
| `on_cleanup(self)` | Logs "Node cleanup" | Final cleanup after stop |
| `on_get_data_visualization_topics(self)` | Returns empty topics | UI requests visualization topics |

### `on_get_data_visualization_topics(self)`

Return ROS2 topics that the frontend can subscribe to for live data visualization.

```python
from neuraverse_sdk.models.node_models import (
    NodeVisualizationsTopic,
    NodeVisualizationsTopics,
)

def on_get_data_visualization_topics(self) -> NodeVisualizationsTopics:
    return NodeVisualizationsTopics(
        topics=[
            NodeVisualizationsTopic(
                topic_name="/camera/image_raw",
                visualization_type="sensor_msgs/CompressedImage",
            )
        ]
    )
```

## Execution Flow Summary

1. **Initialize** — orchestrator calls `on_get_configuration()` to get default config
2. **Configure** — user edits config in UI, orchestrator calls `on_configure(config, dynamic_config)`
3. **Execute** — orchestrator calls `on_execute()`, node reads inputs and publishes outputs
4. **Repeat** — node returns to CONFIGURED, ready for another execution
5. **Stop** — `on_stop()` then `on_cleanup()` called
