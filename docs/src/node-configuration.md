# Node Configuration

The `configuration` field on a `Node` is a `map<string, NodeConfigEntry>` where each key is a
machine-readable config name and the value is a fully self-describing `NodeConfigEntry`.

---

## Proto definition

```protobuf
// A simple boolean toggle (e.g., "isBlending")
message ToggleValue {
    bool enabled = 1;
}

// A numeric range with a current value (e.g., "Confidence threshold: 0.0–1.0")
message RangeValue {
    double min   = 1;
    double max   = 2;
    double value = 3;
    // Granularity of the slider/input (e.g., 0.01 for floats, 1.0 for integers)
    double step  = 4;
}

// A single-select list of allowed string options (e.g., "Mode: [fast, balanced, accurate]")
message SingleSelectListValue {
    repeated string allowedItems = 1; // All options available for selection
    string          selectedItem = 2; // Must be one of allowedItems
}

// A multi-select list (e.g., "Active classes: [person, car, truck]")
message MultiSelectListValue {
    repeated string allowedItems  = 1; // All options available for selection
    repeated string selectedItems = 2; // Subset of allowedItems
}

// The typed value of a single configuration entry.
// Extend with new branches here as new config types are needed —
// existing entries are unaffected (oneof guarantees only one branch is set).
message NodeConfigValue {
    oneof value {
        string                 stringValue           = 1; // Free-text or opaque string
        ToggleValue            toggleValue           = 2; // Boolean on/off
        RangeValue             rangeValue            = 3; // Numeric range with current value
        SingleSelectListValue  singleSelectListValue = 4; // Single-select from a fixed list
        MultiSelectListValue   multiSelectListValue  = 5; // Multi-select from a fixed list
    }
}

// A fully described configuration entry, bundling the typed value with
// metadata that the UI and backend can use without out-of-band knowledge.
message NodeConfigEntry {
    NodeConfigValue configValue   = 1; // The typed value (what gets read/written at runtime)
    string          displayLabel  = 2; // Human-readable label shown in the UI
    string          description   = 3; // Short description or tooltip
    string          unit          = 4; // Optional unit annotation (e.g., "Hz", "ms", "%")
    bool            readOnly      = 5; // Whether this entry is read-only in the UI
    bool            required      = 6; // Whether this entry must be set before the node can run
}

// On the Node message:
map<string, NodeConfigEntry> configuration = 30;
```

---

## Complete example — AI Model Inference node (all `NodeConfigValue` types)

The example below represents a `Fast Object Detection` AI model node.

```json
{
  "id": "AI",
  "name": "Fast Object Detection",
  "type": 1,
  "description": "AI model node for Fast Object Detection",
  "tags": ["Object detection"],
  "inputs": {
    "start": {
      "rosType": "Start",
      "type": 1,
      "requestTarget": "",
      "edgeType": 2,
      "defaultValue": "default"
    },
    "stop": {
      "rosType": "Stop",
      "type": 1,
      "requestTarget": "",
      "edgeType": 2,
      "defaultValue": "default"
    },
    "image": {
      "rosType": "/sensor_msgs/msg/Image",
      "type": 1,
      "requestTarget": "",
      "edgeType": 1,
      "defaultValue": ""
    },
    "camera_info": {
      "rosType": "/sensor_msgs/msg/CameraInfo",
      "type": 1,
      "requestTarget": "",
      "edgeType": 1,
      "defaultValue": ""
    }
  },
  "outputs": {
    "Start": {
      "rosType": "Start",
      "type": 1,
      "requestTarget": "",
      "edgeType": 2,
      "defaultValue": "default"
    },
    "Stop": {
      "rosType": "Stop",
      "type": 1,
      "requestTarget": "",
      "edgeType": 2,
      "defaultValue": "default"
    },
    "Error": {
      "rosType": "Error",
      "type": 1,
      "requestTarget": "",
      "edgeType": 2,
      "defaultValue": "default"
    },
    "detections": {
      "rosType": "/vision_msgs/msg/Detection2DArray",
      "type": 1,
      "requestTarget": "",
      "edgeType": 1,
      "defaultValue": ""
    },
    "masks": {
      "rosType": "/sensor_msgs/msg/Image",
      "type": 1,
      "requestTarget": "",
      "edgeType": 1,
      "defaultValue": ""
    },
    "inference_time": {
      "rosType": "/std_msgs/msg/Float32",
      "type": 1,
      "requestTarget": "",
      "edgeType": 1,
      "defaultValue": ""
    }
  },
  "errorOutputs": {},
  "assetInstanceId": "",
  "executionContext": {
    "type": 3,
    "target": "127.0.0.1:50099",
    "className": "AI"
  },
  "nodeBaseUrl": "",
  "executionStatus": {
    "state": 2,
    "lastUpdate": "2026-03-25T12:49:54Z",
    "statusMessage": "Running"
  },
  "configuration": {
    "config_id": {
      "configValue": {
        "stringValue": "cfg-od-yolov8n-001"
      },
      "displayLabel": "Config ID",
      "description": "Identifier of the model configuration injected at deploy time",
      "unit": "",
      "readOnly": true,
      "required": true
    },
    "enable_gpu": {
      "configValue": {
        "toggleValue": {
          "enabled": true
        }
      },
      "displayLabel": "Enable GPU",
      "description": "Run inference on GPU when available, fall back to CPU otherwise",
      "unit": "",
      "readOnly": false,
      "required": false
    },
    "timeout": {
      "configValue": {
        "rangeValue": {
          "min": 1.0,
          "max": 30.0,
          "value": 5.0,
          "step": 1.0
        }
      },
      "displayLabel": "Inference Timeout",
      "description": "Maximum time to wait for a single inference call before raising an error",
      "unit": "s",
      "readOnly": false,
      "required": true
    },
    "version": {
      "configValue": {
        "singleSelectListValue": {
          "allowedItems": ["1", "2", "3", "4"],
          "selectedItem": "4"
        }
      },
      "displayLabel": "Model Version",
      "description": "Version of the model configuration to load",
      "unit": "",
      "readOnly": false,
      "required": true
    },
    "active_classes": {
      "configValue": {
        "multiSelectListValue": {
          "allowedItems": ["person", "car", "truck", "bicycle", "motorcycle"],
          "selectedItems": ["person", "car"]
        }
      },
      "displayLabel": "Active Classes",
      "description": "Object classes the model will detect and publish; others are filtered out",
      "unit": "",
      "readOnly": false,
      "required": true
    }
  },
  "resourceVersion": 1,
  "history": [],
  "dataFlowCommunicationType": 1
}
```

---

## Configuration field summary

| Key               | `NodeConfigValue` branch  | Notes                                              |
|-------------------|---------------------------|----------------------------------------------------|
| `config_id`       | `stringValue`             | Opaque ID; `readOnly` — injected at deploy time    |
| `enable_gpu`      | `toggleValue`             | Boolean on/off, falls back to CPU if disabled      |
| `timeout`         | `rangeValue`              | `step: 1.0` makes it an integer slider (seconds)   |
| `version`         | `singleSelectListValue`   | Exactly one model version selected                 |
| `active_classes`  | `multiSelectListValue`    | Subset of detectable classes to publish            |
