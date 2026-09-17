# Node API Reference

All methods available inside your `NodeBase` subclass.

---

## Data Flow

### `get_data(port_name, timeout=1)`

Read a message from an input port.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `port_name` | `str` | -- | Name of the input port (must match schema) |
| `timeout` | `float` | `1` | Seconds to wait for data |

**Returns:** A ROS2 message object, or `None` if no data arrives within the timeout.

**Timeout behavior:**

| Value | Behavior |
|-------|----------|
| `1` (default) | Wait up to 1 second |
| `0` or `None` | Immediate read — return whatever is in the buffer, or `None` |
| `-1` | Wait indefinitely |
| Any positive float | Wait that many seconds |

```python
def on_execute(self) -> None:
    # Wait up to 1 second (default)
    msg = self.get_data("text_input")

    # Don't wait — return immediately
    msg = self.get_data("text_input", timeout=0)

    # Wait up to 5 seconds
    msg = self.get_data("text_input", timeout=5)
```

!!! tip
    Always check for `None` before accessing message fields:
    ```python
    msg = self.get_data("my_input")
    if msg:
        self.log_info(f"Got: {msg.data}")
    ```

### `publish(port_name, message)`

Publish a message to an output port.

| Parameter | Type | Description |
|-----------|------|-------------|
| `port_name` | `str` | Name of the output port (must match schema) |
| `message` | ROS2 message | The message object to publish |

```python
from std_msgs.msg import String

def on_execute(self) -> None:
    msg = String()
    msg.data = "Hello from my node"
    self.publish("text_output", msg)
```

### `wait_for_message(port_name, timeout=-1.0)`

Block until a message arrives on an input port. Unlike `get_data()`, this does not return the message — it only waits.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `port_name` | `str` | -- | Input port name |
| `timeout` | `float` | `-1.0` | Seconds to wait (`-1` = forever) |

```python
def on_execute(self) -> None:
    # Wait until data arrives (no timeout)
    self.wait_for_message("critical_input")
    msg = self.get_data("critical_input", timeout=0)
```

### `register_handler(callback, input_name)`

Register a callback function that is called whenever a message arrives on a specific input port.

| Parameter | Type | Description |
|-----------|------|-------------|
| `callback` | `callable` | Function to call with the message |
| `input_name` | `str` | Input port name |

```python
def on_execute(self) -> None:
    def on_image(msg):
        self.log_info(f"Image received: {len(msg.data)} bytes")
        self.publish("image_output", msg)

    self.register_handler(on_image, "image_input")
```

---

## Logging

Use these instead of `print()`. Log messages appear in the Mock Runner UI and in structured log output.

| Method | Level |
|--------|-------|
| `self.log_info(message)` | INFO |
| `self.log_warning(message)` | WARNING |
| `self.log_error(message, exception=None)` | ERROR |
| `self.log_debug(message)` | DEBUG |

```python
self.log_info("Processing started")
self.log_warning("Input was empty, using default")
self.log_debug(f"Raw value: {value}")

try:
    risky_operation()
except Exception as e:
    self.log_error("Operation failed", exception=e)
```

---

## Node Information

These read-only properties and methods are available on `self`:

| Property / Method | Returns | Description |
|-------------------|---------|-------------|
| `self.node_info` | `Node` protobuf | Full node definition |
| `self.get_node_id()` | `str` | Node instance ID |
| `self.get_node_name()` | `str` | Node display name |
| `self.get_node_class_name()` | `str` | Python class name |
| `self.get_inputs()` | `dict` | Input port definitions |
| `self.get_outputs()` | `dict` | Output port definitions |

---

## Supported ROS2 Message Types

These are the most common message types. For the full reference including all geometry, sensor, trajectory, and custom Neuraverse types, see [Compatible I/O Types](compatible_types.md).

### Basic Types

All basic types have a `.data` field.

| rosType | Python Type | Example |
|---------|-------------|---------|
| `std_msgs/String` | `str` | `msg.data = "hello"` |
| `std_msgs/Float32` | `float` | `msg.data = 3.14` |
| `std_msgs/Float64` | `float` | `msg.data = 3.14159265` |
| `std_msgs/Int32` | `int` | `msg.data = 42` |
| `std_msgs/Int64` | `int` | `msg.data = 9999999` |
| `std_msgs/Bool` | `bool` | `msg.data = True` |

```python
def on_execute(self) -> None:
    # Reading a string
    text_msg = self.get_data("text_input")
    if text_msg:
        self.log_info(f"Text: {text_msg.data}")  # text_msg.data is a str

    # Reading a float
    float_msg = self.get_data("float_input")
    if float_msg:
        value = float_msg.data  # float
        self.log_info(f"Value: {value}")

    # Reading a boolean
    bool_msg = self.get_data("bool_input")
    if bool_msg:
        is_active = bool_msg.data  # bool
```

### Array Types

Array types have a `.data` field containing a list.

| rosType | Element Type | Example |
|---------|-------------|---------|
| `std_msgs/Float32MultiArray` | `list[float]` | `msg.data = [1.0, 2.0, 3.0]` |
| `std_msgs/Int32MultiArray` | `list[int]` | `msg.data = [1, 2, 3]` |

```python
arr_msg = self.get_data("float_array_input")
if arr_msg:
    values = arr_msg.data  # list of floats
    self.log_info(f"Array: {values}")
```

### Image Types

| rosType | Fields | Description |
|---------|--------|-------------|
| `sensor_msgs/CompressedImage` | `.data` (bytes), `.format` (str) | Compressed image (JPEG, PNG) |

```python
img_msg = self.get_data("image_input")
if img_msg:
    image_bytes = img_msg.data      # bytes
    image_format = img_msg.format   # e.g. "jpeg"
    self.log_info(f"Image: {image_format}, {len(image_bytes)} bytes")
    self.publish("image_output", img_msg)
```

### Audio Types

| rosType | Fields | Description |
|---------|--------|-------------|
| `audio_common_msgs/AudioData` | `.data` (bytes) | Raw audio data |

```python
audio_msg = self.get_data("audio_input")
if audio_msg:
    audio_bytes = audio_msg.data  # bytes
    self.log_info(f"Audio: {len(audio_bytes)} bytes")
```

### Geometry Types

| rosType | Fields | Description |
|---------|--------|-------------|
| `geometry_msgs/Twist` | `.linear` (x,y,z), `.angular` (x,y,z) | Velocity command |

```python
twist_msg = self.get_data("twist_input")
if twist_msg:
    lx = twist_msg.linear.x
    ly = twist_msg.linear.y
    lz = twist_msg.linear.z
    ax = twist_msg.angular.x
    ay = twist_msg.angular.y
    az = twist_msg.angular.z
    self.log_info(f"Linear: ({lx}, {ly}, {lz}), Angular: ({ax}, {ay}, {az})")
```

### Schema Port Definition

Use the `rosType` string in your schema to define port types:

```json
"inputs": {
  "camera_feed": {
    "rosType": "sensor_msgs/CompressedImage",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  },
  "velocity_cmd": {
    "rosType": "geometry_msgs/Twist",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

### Edge Types

| edgeType | Purpose |
|----------|---------|
| `NODE_EDGE_TYPE_DATA` | Data flow between nodes |
| `NODE_EDGE_TYPE_TRIGGER` | Control flow (Start, Stop, Error) |

---

## Complete Example

A node that reads a string, converts it to uppercase, and publishes the result:

```python
from neuraverse_sdk.node_base import NodeBase
from neuraverse.models.v1.gen.business.node_graph_pb2 import (
    NodeConfigEntry,
    NodeConfigValue,
    ToggleValue,
)


class UppercaseNode(NodeBase):

    def __init__(self):
        super().__init__()
        self._enabled = True

    def on_configure(self, config, dynamic_config=None) -> None:
        if dynamic_config and "enabled" in dynamic_config:
            entry = dynamic_config["enabled"]
            if entry.configValue.HasField("toggleValue"):
                self._enabled = entry.configValue.toggleValue.enabled

    def on_execute(self) -> None:
        if not self._enabled:
            self.log_info("Node is disabled, skipping")
            return

        msg = self.get_data("text_input")
        if msg:
            self.log_info(f"Input: {msg.data}")
            msg.data = msg.data.upper()
            self.publish("text_output", msg)
            self.log_info(f"Output: {msg.data}")
        else:
            self.log_warning("No input received")

    def on_stop(self) -> None:
        self.log_info("UppercaseNode stopped")

    def on_get_configuration(self):
        return {
            "enabled": NodeConfigEntry(
                configValue=NodeConfigValue(
                    toggleValue=ToggleValue(enabled=self._enabled),
                ),
                displayLabel="Enabled",
                description="Process incoming text",
                required=True,
            ),
        }
```
