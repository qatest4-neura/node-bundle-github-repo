# Schema Reference

Every node has a `*_schema.json` file that defines its name, ports, and configuration for the Neuraverse platform.

---

## Minimal Schema

```json
{
  "name": "My Node",
  "type": 1,
  "description": "What this node does",
  "tags": ["example"],
  "inputs": {},
  "outputs": {
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

---

## Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Display name of the node. |
| `type` | integer | Yes | Node type identifier. Use `1` for standard nodes. |
| `description` | string | Yes | Human-readable description. |
| `tags` | string[] | Yes | Tags for filtering and search in the UI. |
| `id` | string | No | Auto-assigned by the platform. Leave empty. |

---

## `inputs` and `outputs`

Define the data and trigger ports on your node. Each key is the port name.

```json
"inputs": {
  "camera_feed": {
    "rosType": "sensor_msgs/CompressedImage",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
},
"outputs": {
  "processed_image": {
    "rosType": "sensor_msgs/CompressedImage",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  },
  "Start": { "rosType": "Start", "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
  "Stop":  { "rosType": "Stop",  "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
  "Error": { "rosType": "Error", "edgeType": "NODE_EDGE_TYPE_TRIGGER" }
}
```

| Field | Description |
|---|---|
| `rosType` | ROS2 message type (e.g. `std_msgs/String`) or trigger name (`Start`, `Stop`, `Error`). |
| `edgeType` | `NODE_EDGE_TYPE_DATA` for data flow, `NODE_EDGE_TYPE_TRIGGER` for control flow. |

!!! warning "Required Trigger Outputs"
    Every node **must** include `Start`, `Stop`, and `Error` trigger outputs.

See [API Reference - Supported ROS2 Types](api_reference.md#supported-ros2-message-types) for the full list of available message types.

---

## `executionContext`

```json
"executionContext": {
  "className": "MyNode"
}
```

| Field | Description |
|---|---|
| `className` | **Must exactly match** the Python class name. Case-sensitive. |

!!! danger
    If your class is `class MyNode(NodeBase):`, then `className` must be `"MyNode"`. A mismatch will cause the node to fail to load.

---

## `configuration` (Legacy String Config)

Optional key-value string pairs for basic settings:

```json
"configuration": {
  "threshold": "0.5",
  "mode": "fast"
}
```

These are passed to `on_configure(config, ...)` as the first argument.

---

## Typed Configuration (`NodeConfigEntry`)

For richer configuration with UI controls, implement `on_get_configuration()` in your node class. This is the **recommended** approach.

### Value Types

| Type | Constructor | UI Control |
|---|---|---|
| **String** | `NodeConfigValue(stringValue="text")` | Text input |
| **Toggle** | `NodeConfigValue(toggleValue=ToggleValue(enabled=True))` | Toggle switch |
| **Range** | `NodeConfigValue(rangeValue=RangeValue(min=0, max=100, value=50, step=1))` | Slider |
| **Single Select** | `NodeConfigValue(singleSelectListValue=SingleSelectListValue(allowedItems=[...], selectedItem="..."))` | Dropdown |
| **Multi Select** | `NodeConfigValue(multiSelectListValue=MultiSelectListValue(allowedItems=[...], selectedItems=[...]))` | Checkboxes |

### `NodeConfigEntry` Fields

| Field | Type | Description |
|---|---|---|
| `configValue` | `NodeConfigValue` | The typed value (required). |
| `displayLabel` | `str` | Label shown in the UI. |
| `description` | `str` | Help text / tooltip. |
| `unit` | `str` | Unit annotation (e.g. `"Hz"`, `"ms"`, `"%"`). |
| `readOnly` | `bool` | If `True`, non-editable in the UI. |
| `required` | `bool` | If `True`, must be set before the node can run. |

### Example

```python
from neuraverse.models.v1.gen.business.node_graph_pb2 import (
    NodeConfigEntry, NodeConfigValue,
    ToggleValue, RangeValue,
    SingleSelectListValue, MultiSelectListValue,
)

def on_get_configuration(self) -> dict[str, NodeConfigEntry]:
    return {
        "enabled": NodeConfigEntry(
            configValue=NodeConfigValue(toggleValue=ToggleValue(enabled=True)),
            displayLabel="Enabled",
            description="Activate this node",
            required=True,
        ),
        "confidence": NodeConfigEntry(
            configValue=NodeConfigValue(
                rangeValue=RangeValue(min=0.0, max=1.0, value=0.8, step=0.01),
            ),
            displayLabel="Confidence Threshold",
            description="Minimum confidence for detections",
            unit="%",
        ),
        "model": NodeConfigEntry(
            configValue=NodeConfigValue(
                singleSelectListValue=SingleSelectListValue(
                    allowedItems=["yolo-v8", "resnet-50", "mobilenet"],
                    selectedItem="yolo-v8",
                ),
            ),
            displayLabel="Model",
            description="AI model to use for inference",
        ),
    }
```

!!! tip "Mock Runner"
    The Mock Runner automatically renders typed configuration. Click **Init Node** to see sliders, toggles, and dropdowns generated from your `on_get_configuration()`.

---

## Full Schema Example

```json
{
  "id": "",
  "name": "Image Classifier",
  "type": 1,
  "description": "Classifies images using a selected AI model",
  "tags": ["ai", "vision", "classification"],
  "inputs": {
    "image_input": {
      "rosType": "sensor_msgs/CompressedImage",
      "edgeType": "NODE_EDGE_TYPE_DATA"
    }
  },
  "outputs": {
    "result_output": {
      "rosType": "std_msgs/String",
      "edgeType": "NODE_EDGE_TYPE_DATA"
    },
    "confidence_output": {
      "rosType": "std_msgs/Float32",
      "edgeType": "NODE_EDGE_TYPE_DATA"
    },
    "Start": { "rosType": "Start", "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
    "Stop":  { "rosType": "Stop",  "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
    "Error": { "rosType": "Error", "edgeType": "NODE_EDGE_TYPE_TRIGGER" }
  },
  "executionContext": {
    "className": "ImageClassifier"
  },
  "configuration": {}
}
```
