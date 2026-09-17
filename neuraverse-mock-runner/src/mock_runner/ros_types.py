"""Mock ROS2 message types for testing nodes without ROS2 installed."""

import base64
from typing import Any


class MockMessage:
    """Generic mock ROS2 message. Attributes are set dynamically."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"MockMessage({attrs})"


# Schema for each supported ROS2 type.
# Each entry describes the fields the frontend should render.
# "type" is one of: string, float, int, bool, float_array, bytes, json
ROS_TYPE_SCHEMAS: dict[str, dict] = {
    "std_msgs/String": {
        "fields": [{"name": "data", "type": "string", "label": "Text"}],
    },
    "std_msgs/Float32": {
        "fields": [{"name": "data", "type": "float", "label": "Value (float32)"}],
    },
    "std_msgs/Float64": {
        "fields": [{"name": "data", "type": "float", "label": "Value (float64)"}],
    },
    "std_msgs/Int32": {
        "fields": [{"name": "data", "type": "int", "label": "Value (int32)"}],
    },
    "std_msgs/Int64": {
        "fields": [{"name": "data", "type": "int", "label": "Value (int64)"}],
    },
    "std_msgs/Bool": {
        "fields": [{"name": "data", "type": "bool", "label": "Value"}],
    },
    "std_msgs/Float32MultiArray": {
        "fields": [{"name": "data", "type": "float_array", "label": "Values (comma-separated)"}],
    },
    "std_msgs/Float64MultiArray": {
        "fields": [{"name": "data", "type": "float_array", "label": "Values (comma-separated)"}],
    },
    "std_msgs/Int32MultiArray": {
        "fields": [{"name": "data", "type": "int_array", "label": "Values (comma-separated)"}],
    },
    "sensor_msgs/CompressedImage": {
        "fields": [
            {"name": "format", "type": "string", "label": "Format (e.g. jpeg, png)"},
            {"name": "data", "type": "base64", "label": "Image data (base64)"},
        ],
    },
    "sensor_msgs/Image": {
        "fields": [
            {"name": "width", "type": "int", "label": "Width"},
            {"name": "height", "type": "int", "label": "Height"},
            {"name": "encoding", "type": "string", "label": "Encoding (e.g. rgb8)"},
            {"name": "step", "type": "int", "label": "Row length in bytes"},
            {"name": "is_bigendian", "type": "int", "label": "Is big-endian (0 or 1)"},
            {"name": "data", "type": "base64", "label": "Pixel data (base64)"},
        ],
    },
    "geometry_msgs/Twist": {
        "fields": [
            {"name": "linear_x", "type": "float", "label": "Linear X"},
            {"name": "linear_y", "type": "float", "label": "Linear Y"},
            {"name": "linear_z", "type": "float", "label": "Linear Z"},
            {"name": "angular_x", "type": "float", "label": "Angular X"},
            {"name": "angular_y", "type": "float", "label": "Angular Y"},
            {"name": "angular_z", "type": "float", "label": "Angular Z"},
        ],
    },
    "audio_common_msgs/AudioData": {
        "fields": [
            {"name": "data", "type": "base64", "label": "Audio data (base64)"},
        ],
    },
}


def _normalize_ros_type(ros_type: str) -> str:
    """Normalise a ROS2 type string to the short ``pkg/MsgName`` form.

    Accepts ``/sensor_msgs/msg/CompressedImage``, ``sensor_msgs/msg/CompressedImage``,
    and the already-short ``sensor_msgs/CompressedImage``.
    """
    parts = ros_type.strip("/").split("/")
    if len(parts) == 3 and parts[1] == "msg":
        return f"{parts[0]}/{parts[2]}"
    return ros_type.strip("/")


def get_type_schema(ros_type: str) -> dict:
    """Return the field schema for a ROS2 type, or a generic JSON fallback."""
    key = _normalize_ros_type(ros_type)
    if key in ROS_TYPE_SCHEMAS:
        return ROS_TYPE_SCHEMAS[key]
    return {
        "fields": [{"name": "json", "type": "json", "label": f"Data ({ros_type}) — JSON"}],
    }


def build_mock_message(ros_type: str, fields: dict[str, Any]) -> MockMessage:
    """Build a mock ROS2 message from a type string and field values.

    Args:
        ros_type: ROS2 type string, e.g. "std_msgs/String"
        fields: Dict of field_name -> value from the user

    Returns:
        A MockMessage instance that mimics the ROS2 message interface.
    """
    ros_type = _normalize_ros_type(ros_type)

    if ros_type in ("std_msgs/String",):
        return MockMessage(data=str(fields.get("data", "")))

    if ros_type in ("std_msgs/Float32", "std_msgs/Float64"):
        return MockMessage(data=float(fields.get("data", 0)))

    if ros_type in ("std_msgs/Int32", "std_msgs/Int64"):
        return MockMessage(data=int(fields.get("data", 0)))

    if ros_type == "std_msgs/Bool":
        val = fields.get("data", False)
        if isinstance(val, str):
            val = val.lower() in ("true", "1", "yes")
        return MockMessage(data=bool(val))

    if ros_type in ("std_msgs/Float32MultiArray", "std_msgs/Float64MultiArray"):
        raw = fields.get("data", "")
        if isinstance(raw, str):
            data = [float(x.strip()) for x in raw.split(",") if x.strip()]
        elif isinstance(raw, list):
            data = [float(x) for x in raw]
        else:
            data = []
        return MockMessage(data=data)

    if ros_type == "std_msgs/Int32MultiArray":
        raw = fields.get("data", "")
        if isinstance(raw, str):
            data = [int(x.strip()) for x in raw.split(",") if x.strip()]
        elif isinstance(raw, list):
            data = [int(x) for x in raw]
        else:
            data = []
        return MockMessage(data=data)

    if ros_type == "sensor_msgs/CompressedImage":
        fmt = str(fields.get("format", "jpeg"))
        raw_data = fields.get("data", "")
        if isinstance(raw_data, str):
            raw_data = base64.b64decode(raw_data) if raw_data else b""
        return MockMessage(data=raw_data, format=fmt)

    if ros_type == "sensor_msgs/Image":
        width = int(fields.get("width", 0))
        height = int(fields.get("height", 0))
        encoding = str(fields.get("encoding", "rgb8"))
        pixel_data = base64.b64decode(fields.get("data", "")) if fields.get("data") else b""
        # Default step: width * bytes-per-pixel based on encoding
        bpp = {"rgb8": 3, "rgba8": 4, "bgr8": 3, "bgra8": 4, "mono8": 1, "mono16": 2}
        default_step = width * bpp.get(encoding, 3)
        step = int(fields.get("step", default_step))
        is_bigendian = int(fields.get("is_bigendian", 0))
        return MockMessage(
            width=width,
            height=height,
            encoding=encoding,
            step=step,
            is_bigendian=is_bigendian,
            data=pixel_data,
        )

    if ros_type == "geometry_msgs/Twist":
        linear = MockMessage(
            x=float(fields.get("linear_x", 0)),
            y=float(fields.get("linear_y", 0)),
            z=float(fields.get("linear_z", 0)),
        )
        angular = MockMessage(
            x=float(fields.get("angular_x", 0)),
            y=float(fields.get("angular_y", 0)),
            z=float(fields.get("angular_z", 0)),
        )
        return MockMessage(linear=linear, angular=angular)

    if ros_type == "audio_common_msgs/AudioData":
        raw_data = fields.get("data", "")
        if isinstance(raw_data, str):
            raw_data = base64.b64decode(raw_data) if raw_data else b""
        return MockMessage(data=raw_data)

    # Fallback: treat fields as raw JSON attributes
    json_data = fields.get("json", fields)
    if isinstance(json_data, dict):
        return MockMessage(**json_data)
    return MockMessage(data=json_data)
