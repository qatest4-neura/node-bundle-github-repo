# Compatible I/O Types

This reference lists all ROS2 message types you can use when defining node input and output ports. Types are grouped by package.

!!! info "Schema Usage"
    Use the short form `pkg/MsgName` (e.g. `std_msgs/String`) in your schema JSON.
    The long form `/pkg/msg/MsgName` also works but the short form is preferred.

    ```json
    {
      "rosType": "sensor_msgs/CompressedImage",
      "edgeType": "NODE_EDGE_TYPE_DATA"
    }
    ```

---

## Standard Messages (`std_msgs`)

Simple wrapper types around a single `.data` field.

### Scalar Types

| rosType | Python Type | Fields | Description |
|---------|-------------|--------|-------------|
| `std_msgs/String` | `str` | `.data` | Text data |
| `std_msgs/Bool` | `bool` | `.data` | Boolean flag |
| `std_msgs/Float32` | `float` | `.data` | 32-bit floating point |
| `std_msgs/Float64` | `float` | `.data` | 64-bit floating point (double precision) |
| `std_msgs/Int32` | `int` | `.data` | 32-bit signed integer |
| `std_msgs/Int64` | `int` | `.data` | 64-bit signed integer |

```python
from std_msgs.msg import String, Float32, Bool

# Reading
msg = self.get_data("text_input")
if msg:
    value = msg.data  # str, float, int, or bool depending on type

# Publishing
out = String()
out.data = "hello"
self.publish("text_output", out)
```

### Array Types

| rosType | Element Type | Fields | Description |
|---------|-------------|--------|-------------|
| `std_msgs/Float32MultiArray` | `list[float]` | `.data` | Array of 32-bit floats |
| `std_msgs/Float64MultiArray` | `list[float]` | `.data` | Array of 64-bit floats |
| `std_msgs/Int32MultiArray` | `list[int]` | `.data` | Array of 32-bit integers |

```python
from std_msgs.msg import Float32MultiArray

arr = Float32MultiArray()
arr.data = [1.0, 2.0, 3.0]
self.publish("array_output", arr)
```

---

## Sensor Messages (`sensor_msgs`)

Types for camera images, depth data, point clouds, and robot joint states.

### `sensor_msgs/CompressedImage`

Compressed image data (JPEG, PNG). The most common image type for node-to-node transfer.

| Field | Type | Description |
|-------|------|-------------|
| `.format` | `str` | Compression format (e.g. `"jpeg"`, `"png"`) |
| `.data` | `bytes` | Compressed image bytes |

**Use case:** Camera feeds, processed images, segmentation masks (PNG format for masks).

```python
from sensor_msgs.msg import CompressedImage

img = self.get_data("camera_feed")
if img:
    image_bytes = img.data       # bytes
    image_format = img.format    # "jpeg" or "png"
    self.log_info(f"Image: {image_format}, {len(image_bytes)} bytes")
```

### `sensor_msgs/Image`

Raw (uncompressed) image data with pixel-level access.

| Field | Type | Description |
|-------|------|-------------|
| `.width` | `int` | Image width in pixels |
| `.height` | `int` | Image height in pixels |
| `.encoding` | `str` | Pixel encoding (e.g. `"rgb8"`, `"bgr8"`, `"mono8"`, `"16UC1"`) |
| `.step` | `int` | Row length in bytes |
| `.data` | `bytes` | Raw pixel data |

**Use case:** Image processing pipelines that need direct pixel access, depth images (`16UC1` encoding).

```python
from sensor_msgs.msg import Image

img = self.get_data("raw_image")
if img:
    self.log_info(f"Image: {img.width}x{img.height}, encoding={img.encoding}")
```

!!! tip "CompressedImage vs Image"
    Prefer `CompressedImage` for transfer between nodes — it uses much less bandwidth.
    Use raw `Image` only when you need direct pixel access or specific encodings (e.g. depth).

### `sensor_msgs/CameraInfo`

Camera calibration and metadata.

| Field | Type | Description |
|-------|------|-------------|
| `.width` | `int` | Image width |
| `.height` | `int` | Image height |
| `.distortion_model` | `str` | Distortion model name (e.g. `"plumb_bob"`) |
| `.d` | `list[float]` | Distortion parameters |
| `.k` | `list[float]` | 3x3 intrinsic camera matrix (row-major, 9 elements) |
| `.r` | `list[float]` | 3x3 rectification matrix (row-major, 9 elements) |
| `.p` | `list[float]` | 3x4 projection matrix (row-major, 12 elements) |

**Use case:** Paired with camera image outputs to provide calibration data for 3D reconstruction or undistortion.

### `sensor_msgs/PointCloud2`

3D point cloud data from depth cameras or LIDAR sensors.

| Field | Type | Description |
|-------|------|-------------|
| `.width` | `int` | Number of points per row |
| `.height` | `int` | Number of rows (1 for unordered clouds) |
| `.fields` | `list[PointField]` | Description of each channel (x, y, z, rgb, etc.) |
| `.point_step` | `int` | Bytes per point |
| `.row_step` | `int` | Bytes per row |
| `.data` | `bytes` | Serialized point data |
| `.is_dense` | `bool` | `True` if no invalid points |

**Use case:** 3D scene data from depth cameras, object detection in 3D space.

### `sensor_msgs/JointState`

Robot joint positions, velocities, and efforts.

| Field | Type | Description |
|-------|------|-------------|
| `.name` | `list[str]` | Joint names |
| `.position` | `list[float]` | Joint positions (radians or meters) |
| `.velocity` | `list[float]` | Joint velocities |
| `.effort` | `list[float]` | Joint efforts (torques or forces) |

**Use case:** Robot telemetry, joint monitoring, motion feedback.

```python
from sensor_msgs.msg import JointState

js = self.get_data("joint_states")
if js:
    for name, pos in zip(js.name, js.position):
        self.log_info(f"Joint {name}: {pos:.4f} rad")
```

---

## Geometry Messages (`geometry_msgs`)

Types for positions, orientations, and velocities in 3D space.

### `geometry_msgs/Pose`

A position and orientation in 3D space.

| Field | Type | Description |
|-------|------|-------------|
| `.position` | `Point` | Position with `.x`, `.y`, `.z` (floats) |
| `.orientation` | `Quaternion` | Orientation with `.x`, `.y`, `.z`, `.w` (floats) |

**Use case:** Robot target positions, object locations, motion goals.

```python
from geometry_msgs.msg import Pose

pose = self.get_data("target_pose")
if pose:
    x, y, z = pose.position.x, pose.position.y, pose.position.z
    self.log_info(f"Target: ({x}, {y}, {z})")
```

### `geometry_msgs/PoseStamped`

A `Pose` with a timestamp and coordinate frame.

| Field | Type | Description |
|-------|------|-------------|
| `.header` | `Header` | Timestamp (`.stamp`) and frame (`.frame_id`) |
| `.pose` | `Pose` | The pose (position + orientation) |

**Use case:** Timestamped robot poses, frame-aware target positions.

### `geometry_msgs/PoseArray`

A list of poses, often used for trajectories or multiple detected objects.

| Field | Type | Description |
|-------|------|-------------|
| `.header` | `Header` | Timestamp and frame |
| `.poses` | `list[Pose]` | List of poses |

**Use case:** Pose estimation results (multiple detected object poses), waypoint lists.

```python
from geometry_msgs.msg import PoseArray

poses = self.get_data("detected_poses")
if poses:
    self.log_info(f"Detected {len(poses.poses)} objects")
    for i, p in enumerate(poses.poses):
        self.log_info(f"  Object {i}: ({p.position.x}, {p.position.y}, {p.position.z})")
```

### `geometry_msgs/TransformStamped`

A coordinate frame transformation.

| Field | Type | Description |
|-------|------|-------------|
| `.header` | `Header` | Timestamp and parent frame (`.frame_id`) |
| `.child_frame_id` | `str` | Child frame name |
| `.transform` | `Transform` | Translation (`.translation.x/y/z`) + rotation (`.rotation.x/y/z/w`) |

**Use case:** Frame transformations between robot links, camera-to-world transforms.

### `geometry_msgs/Twist`

Linear and angular velocity.

| Field | Type | Description |
|-------|------|-------------|
| `.linear` | `Vector3` | Linear velocity with `.x`, `.y`, `.z` |
| `.angular` | `Vector3` | Angular velocity with `.x`, `.y`, `.z` |

**Use case:** Velocity commands for mobile robots, joystick input.

```python
from geometry_msgs.msg import Twist

twist = self.get_data("velocity_cmd")
if twist:
    self.log_info(f"Linear: ({twist.linear.x}, {twist.linear.y}, {twist.linear.z})")
    self.log_info(f"Angular: ({twist.angular.x}, {twist.angular.y}, {twist.angular.z})")
```

---

## Trajectory Messages (`trajectory_msgs`)

Types for robot motion planning and execution.

### `trajectory_msgs/JointTrajectoryPoint`

A single waypoint in joint space.

| Field | Type | Description |
|-------|------|-------------|
| `.positions` | `list[float]` | Joint positions (radians) |
| `.velocities` | `list[float]` | Joint velocities |
| `.accelerations` | `list[float]` | Joint accelerations |
| `.effort` | `list[float]` | Joint efforts |
| `.time_from_start` | `Duration` | Time offset from trajectory start |

**Use case:** Single motion target for robot joints (used by move_joint, move_linear, move_circular nodes).

### `trajectory_msgs/JointTrajectory`

A complete joint-space trajectory with multiple waypoints.

| Field | Type | Description |
|-------|------|-------------|
| `.header` | `Header` | Timestamp and frame |
| `.joint_names` | `list[str]` | Names of the joints |
| `.points` | `list[JointTrajectoryPoint]` | Ordered list of waypoints |

**Use case:** Multi-point motion sequences, blending trajectories (used by move_joint_blending, move_linear_blending nodes).

---

## Audio Messages (`audio_common_msgs`)

### `audio_common_msgs/AudioData`

Raw audio data.

| Field | Type | Description |
|-------|------|-------------|
| `.data` | `bytes` | Raw audio bytes |

**Use case:** Audio streaming, speech-to-text input, sound detection.

```python
audio = self.get_data("audio_input")
if audio:
    self.log_info(f"Audio: {len(audio.data)} bytes")
```

---

## Custom Neuraverse Messages

These are custom ROS2 message types defined within the Neuraverse ecosystem. They are pre-installed in the node SDK base image.

### Pose Estimation (`pose_estimation_ros_msgs`)

Types for object pose estimation with uncertainty.

#### `pose_estimation_ros_msgs/ObjectPoseWithCovariance`

Object pose estimate with a 6x6 covariance matrix.

| Field | Type | Description |
|-------|------|-------------|
| `.header` | `Header` | Timestamp and coordinate frame |
| `.object_class_name` | `str` | Detected object class name |
| `.pose` | `Pose` | 6-DoF pose (position + orientation) |
| `.covariance` | `float64[36]` | 6x6 covariance matrix (row-major) |

**Schema (input):**

```json
"inputs": {
  "pose_estimate": {
    "rosType": "pose_estimation_ros_msgs/ObjectPoseWithCovariance",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from pose_estimation_ros_msgs.msg import ObjectPoseWithCovariance

msg = self.get_data("pose_estimate")
if msg:
    self.log_info(f"Object: {msg.object_class_name}")
    pos = msg.pose.position
    self.log_info(f"Position: ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f})")
    ori = msg.pose.orientation
    self.log_info(f"Orientation: ({ori.x:.3f}, {ori.y:.3f}, {ori.z:.3f}, {ori.w:.3f})")
    # covariance is a flat 36-element array (6x6 row-major)
    self.log_info(f"Position variance: x={msg.covariance[0]:.4f}, y={msg.covariance[7]:.4f}, z={msg.covariance[14]:.4f}")
```

**Schema (output):**

```json
"outputs": {
  "pose_estimate": {
    "rosType": "pose_estimation_ros_msgs/ObjectPoseWithCovariance",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from pose_estimation_ros_msgs.msg import ObjectPoseWithCovariance
from std_msgs.msg import Header
from geometry_msgs.msg import Pose, Point, Quaternion

msg = ObjectPoseWithCovariance()
msg.header = Header()
msg.header.frame_id = "base_link"
msg.object_class_name = "mug"
msg.pose = Pose(
    position=Point(x=0.5, y=0.1, z=0.8),
    orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
)
# 6x6 identity covariance (low uncertainty)
msg.covariance = [0.0] * 36
msg.covariance[0] = 0.001   # x variance
msg.covariance[7] = 0.001   # y variance
msg.covariance[14] = 0.001  # z variance
msg.covariance[21] = 0.01   # roll variance
msg.covariance[28] = 0.01   # pitch variance
msg.covariance[35] = 0.01   # yaw variance
self.publish("pose_estimate", msg)
```

#### `pose_estimation_ros_msgs/ObjectPoseWithCovarianceArray`

A collection of object pose estimates.

| Field | Type | Description |
|-------|------|-------------|
| `.object_poses` | `list[ObjectPoseWithCovariance]` | List of pose estimates |

**Schema (input):**

```json
"inputs": {
  "all_poses": {
    "rosType": "pose_estimation_ros_msgs/ObjectPoseWithCovarianceArray",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from pose_estimation_ros_msgs.msg import ObjectPoseWithCovarianceArray

msg = self.get_data("all_poses")
if msg:
    self.log_info(f"Received {len(msg.object_poses)} pose estimates")
    for pose_cov in msg.object_poses:
        pos = pose_cov.pose.position
        self.log_info(f"  {pose_cov.object_class_name}: ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f})")
```

**Schema (output):**

```json
"outputs": {
  "all_poses": {
    "rosType": "pose_estimation_ros_msgs/ObjectPoseWithCovarianceArray",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from pose_estimation_ros_msgs.msg import ObjectPoseWithCovarianceArray, ObjectPoseWithCovariance
from std_msgs.msg import Header
from geometry_msgs.msg import Pose, Point, Quaternion

pose1 = ObjectPoseWithCovariance()
pose1.header = Header(frame_id="base_link")
pose1.object_class_name = "mug"
pose1.pose = Pose(position=Point(x=0.5, y=0.1, z=0.8), orientation=Quaternion(w=1.0))
pose1.covariance = [0.0] * 36

pose2 = ObjectPoseWithCovariance()
pose2.header = Header(frame_id="base_link")
pose2.object_class_name = "bottle"
pose2.pose = Pose(position=Point(x=0.3, y=-0.2, z=0.75), orientation=Quaternion(w=1.0))
pose2.covariance = [0.0] * 36

msg = ObjectPoseWithCovarianceArray()
msg.object_poses = [pose1, pose2]
self.publish("all_poses", msg)
```

---

### Grasp Planning (`neura_grasp_planning_msgs`)

Types for robotic grasp planning and pick-and-place operations.

#### `neura_grasp_planning_msgs/PickPose`

A full pick motion plan with pre-grasp, grasp, and post-grasp poses.

| Field | Type | Description |
|-------|------|-------------|
| `.grasp_pose` | `PoseStamped` | The grasp pose |
| `.pre_grasp_pose` | `PoseStamped` | Approach pose before grasping |
| `.post_grasp_pose` | `PoseStamped` | Retreat pose after grasping |
| `.grasp_idx` | `int64` | Unique grasp index (`-1` if unset) |
| `.hand_opening` | `float32` | Gripper aperture (meters) |
| `.grasp_quality` | `float32` | Grasp quality score (0.0 – 1.0) |

**Schema (input):**

```json
"inputs": {
  "pick_pose": {
    "rosType": "neura_grasp_planning_msgs/PickPose",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from neura_grasp_planning_msgs.msg import PickPose

msg = self.get_data("pick_pose")
if msg:
    grasp = msg.grasp_pose.pose.position
    self.log_info(f"Grasp at: ({grasp.x:.3f}, {grasp.y:.3f}, {grasp.z:.3f})")
    self.log_info(f"Quality: {msg.grasp_quality:.2f}, opening: {msg.hand_opening:.3f}m")

    pre = msg.pre_grasp_pose.pose.position
    self.log_info(f"Approach from: ({pre.x:.3f}, {pre.y:.3f}, {pre.z:.3f})")

    post = msg.post_grasp_pose.pose.position
    self.log_info(f"Retreat to: ({post.x:.3f}, {post.y:.3f}, {post.z:.3f})")
```

**Schema (output):**

```json
"outputs": {
  "pick_pose": {
    "rosType": "neura_grasp_planning_msgs/PickPose",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from neura_grasp_planning_msgs.msg import PickPose
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from std_msgs.msg import Header

header = Header(frame_id="base_link")

msg = PickPose()
msg.grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.3), orientation=Quaternion(w=1.0)),
)
msg.pre_grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.45), orientation=Quaternion(w=1.0)),
)
msg.post_grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.5), orientation=Quaternion(w=1.0)),
)
msg.grasp_idx = 0
msg.hand_opening = 0.08
msg.grasp_quality = 0.92
self.publish("pick_pose", msg)
```

#### `neura_grasp_planning_msgs/PickPoses`

All pick plans for a single detected object.

| Field | Type | Description |
|-------|------|-------------|
| `.object_name` | `str` | Object class name |
| `.object_instance_id` | `int32` | Instance ID from segmentation |
| `.picks` | `list[PickPose]` | Ranked pick motion plans (best first) |

**Schema (input):**

```json
"inputs": {
  "object_picks": {
    "rosType": "neura_grasp_planning_msgs/PickPoses",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from neura_grasp_planning_msgs.msg import PickPoses

msg = self.get_data("object_picks")
if msg:
    self.log_info(f"Object: {msg.object_name} (instance {msg.object_instance_id})")
    self.log_info(f"  {len(msg.picks)} grasp candidates")
    for i, pick in enumerate(msg.picks):
        pos = pick.grasp_pose.pose.position
        self.log_info(f"  Grasp {i}: ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}), quality={pick.grasp_quality:.2f}")
```

**Schema (output):**

```json
"outputs": {
  "object_picks": {
    "rosType": "neura_grasp_planning_msgs/PickPoses",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from neura_grasp_planning_msgs.msg import PickPoses, PickPose
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from std_msgs.msg import Header

header = Header(frame_id="base_link")

pick = PickPose()
pick.grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.3), orientation=Quaternion(w=1.0)),
)
pick.pre_grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.45), orientation=Quaternion(w=1.0)),
)
pick.post_grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.5), orientation=Quaternion(w=1.0)),
)
pick.grasp_idx = 0
pick.hand_opening = 0.08
pick.grasp_quality = 0.92

msg = PickPoses()
msg.object_name = "mug"
msg.object_instance_id = 0
msg.picks = [pick]
self.publish("object_picks", msg)
```

#### `neura_grasp_planning_msgs/ObjectPickPosesArray`

Pick plans for all detected objects in a scene.

| Field | Type | Description |
|-------|------|-------------|
| `.object_pick_poses_array` | `list[PickPoses]` | Per-object pick plans |

**Schema (input):**

```json
"inputs": {
  "scene_picks": {
    "rosType": "neura_grasp_planning_msgs/ObjectPickPosesArray",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from neura_grasp_planning_msgs.msg import ObjectPickPosesArray

msg = self.get_data("scene_picks")
if msg:
    self.log_info(f"Pick plans for {len(msg.object_pick_poses_array)} objects")
    for obj_picks in msg.object_pick_poses_array:
        best = obj_picks.picks[0] if obj_picks.picks else None
        if best:
            pos = best.grasp_pose.pose.position
            self.log_info(
                f"  {obj_picks.object_name}: best grasp at ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}), "
                f"quality={best.grasp_quality:.2f}"
            )
```

**Schema (output):**

```json
"outputs": {
  "scene_picks": {
    "rosType": "neura_grasp_planning_msgs/ObjectPickPosesArray",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from neura_grasp_planning_msgs.msg import ObjectPickPosesArray, PickPoses, PickPose
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from std_msgs.msg import Header

header = Header(frame_id="base_link")

# Build a pick for one object
pick = PickPose()
pick.grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.3), orientation=Quaternion(w=1.0)),
)
pick.pre_grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.45), orientation=Quaternion(w=1.0)),
)
pick.post_grasp_pose = PoseStamped(
    header=header,
    pose=Pose(position=Point(x=0.5, y=0.1, z=0.5), orientation=Quaternion(w=1.0)),
)
pick.hand_opening = 0.08
pick.grasp_quality = 0.92

mug_picks = PickPoses()
mug_picks.object_name = "mug"
mug_picks.object_instance_id = 0
mug_picks.picks = [pick]

msg = ObjectPickPosesArray()
msg.object_pick_poses_array = [mug_picks]
self.publish("scene_picks", msg)
```

---

### Instance Segmentation (`instance_segmentation_ros_msgs`)

Types for image segmentation and object detection results.

#### `instance_segmentation_ros_msgs/SegmentationResult`

Top-level segmentation output containing all detected instances with masks.

| Field | Type | Description |
|-------|------|-------------|
| `.header` | `Header` | Timestamp and coordinate frame |
| `.instances` | `list[MaskWithObjectName]` | Detected object instances with masks and bounding boxes |

**Schema (input):**

```json
"inputs": {
  "segmentation": {
    "rosType": "instance_segmentation_ros_msgs/SegmentationResult",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from instance_segmentation_ros_msgs.msg import SegmentationResult

msg = self.get_data("segmentation")
if msg:
    self.log_info(f"Segmentation with {len(msg.instances)} objects")
    for inst in msg.instances:
        bbox = inst.bounding_box
        self.log_info(
            f"  {inst.class_name}: score={inst.score:.2%}, "
            f"bbox center=({bbox.center.position.x:.0f}, {bbox.center.position.y:.0f}), "
            f"size=({bbox.size_x:.0f}x{bbox.size_y:.0f})"
        )
        # inst.mask is an Image (PNG-encoded binary segmentation mask)
        self.log_info(f"    mask: {inst.mask.width}x{inst.mask.height}, {len(inst.mask.data)} bytes")
```

**Schema (output):**

```json
"outputs": {
  "segmentation": {
    "rosType": "instance_segmentation_ros_msgs/SegmentationResult",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from instance_segmentation_ros_msgs.msg import SegmentationResult, MaskWithObjectName
from sensor_msgs.msg import Image
from vision_msgs.msg import BoundingBox2D
from geometry_msgs.msg import Pose2D
from std_msgs.msg import Header

instance = MaskWithObjectName()
instance.class_name = "mug"
instance.score = 0.95

# Binary segmentation mask as PNG-encoded Image
instance.mask = Image()
instance.mask.width = 640
instance.mask.height = 480
instance.mask.encoding = "png"
instance.mask.data = png_bytes  # your PNG-encoded mask bytes

# 2D bounding box
instance.bounding_box = BoundingBox2D()
instance.bounding_box.center = Pose2D(x=320.0, y=240.0, theta=0.0)
instance.bounding_box.size_x = 100.0
instance.bounding_box.size_y = 80.0

msg = SegmentationResult()
msg.header = Header(frame_id="camera_color_optical_frame")
msg.instances = [instance]
self.publish("segmentation", msg)
```

#### `instance_segmentation_ros_msgs/MaskWithObjectName`

A single detected object with its segmentation mask and bounding box.

| Field | Type | Description |
|-------|------|-------------|
| `.class_name` | `str` | Detected class name |
| `.mask` | `Image` | Binary segmentation mask (PNG encoding) |
| `.bounding_box` | `BoundingBox2D` | 2D bounding box (`vision_msgs`) |
| `.score` | `float64` | Detection confidence (0.0 – 1.0) |

**Schema (input):**

```json
"inputs": {
  "detected_object": {
    "rosType": "instance_segmentation_ros_msgs/MaskWithObjectName",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from instance_segmentation_ros_msgs.msg import MaskWithObjectName

msg = self.get_data("detected_object")
if msg:
    self.log_info(f"Class: {msg.class_name}, score: {msg.score:.2%}")

    # Access the bounding box
    bbox = msg.bounding_box
    cx, cy = bbox.center.position.x, bbox.center.position.y
    w, h = bbox.size_x, bbox.size_y
    self.log_info(f"Bounding box: center=({cx:.0f}, {cy:.0f}), size={w:.0f}x{h:.0f}")

    # Access the segmentation mask (PNG-encoded Image)
    self.log_info(f"Mask: {msg.mask.width}x{msg.mask.height}, {len(msg.mask.data)} bytes")
```

**Schema (output):**

```json
"outputs": {
  "detected_object": {
    "rosType": "instance_segmentation_ros_msgs/MaskWithObjectName",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from instance_segmentation_ros_msgs.msg import MaskWithObjectName
from sensor_msgs.msg import Image
from vision_msgs.msg import BoundingBox2D
from geometry_msgs.msg import Pose2D

msg = MaskWithObjectName()
msg.class_name = "bottle"
msg.score = 0.87

msg.mask = Image()
msg.mask.width = 640
msg.mask.height = 480
msg.mask.encoding = "png"
msg.mask.data = png_bytes  # your PNG-encoded binary mask

msg.bounding_box = BoundingBox2D()
msg.bounding_box.center = Pose2D(x=150.0, y=200.0, theta=0.0)
msg.bounding_box.size_x = 60.0
msg.bounding_box.size_y = 120.0

self.publish("detected_object", msg)
```

---

## Vision Messages (`vision_msgs`)

Standard ROS2 types for computer vision.

### `vision_msgs/BoundingBox2D`

A 2D bounding box defined by center point and size.

| Field | Type | Description |
|-------|------|-------------|
| `.center` | `Pose2D` | Center of the box (`.x`, `.y`, `.theta`) |
| `.size_x` | `float64` | Box width in pixels |
| `.size_y` | `float64` | Box height in pixels |

**Schema (input):**

```json
"inputs": {
  "bounding_box": {
    "rosType": "vision_msgs/BoundingBox2D",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Reading from input:**

```python
from vision_msgs.msg import BoundingBox2D

msg = self.get_data("bounding_box")
if msg:
    cx, cy = msg.center.position.x, msg.center.position.y
    w, h = msg.size_x, msg.size_y
    self.log_info(f"Box center: ({cx:.0f}, {cy:.0f}), size: {w:.0f}x{h:.0f}")

    # Convert to top-left corner coordinates if needed
    x_min = cx - w / 2.0
    y_min = cy - h / 2.0
    self.log_info(f"Top-left: ({x_min:.0f}, {y_min:.0f})")
```

**Schema (output):**

```json
"outputs": {
  "bounding_box": {
    "rosType": "vision_msgs/BoundingBox2D",
    "edgeType": "NODE_EDGE_TYPE_DATA"
  }
}
```

**Publishing to output:**

```python
from vision_msgs.msg import BoundingBox2D
from geometry_msgs.msg import Pose2D

msg = BoundingBox2D()
msg.center = Pose2D(x=320.0, y=240.0, theta=0.0)
msg.size_x = 100.0  # width in pixels
msg.size_y = 80.0   # height in pixels
self.publish("bounding_box", msg)
```

---

## Trigger Types

Triggers are special port types for control flow. They don't carry data.

| rosType | Direction | Description |
|---------|-----------|-------------|
| `Start` | Input / Output | Signals node to begin / has begun execution |
| `Stop` | Input / Output | Signals node to stop / has stopped |
| `Error` | Output only | Signals an error occurred |

```json
"inputs": {
  "Start": { "rosType": "Start", "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
  "Stop":  { "rosType": "Stop",  "edgeType": "NODE_EDGE_TYPE_TRIGGER" }
},
"outputs": {
  "Start": { "rosType": "Start", "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
  "Stop":  { "rosType": "Stop",  "edgeType": "NODE_EDGE_TYPE_TRIGGER" },
  "Error": { "rosType": "Error", "edgeType": "NODE_EDGE_TYPE_TRIGGER" }
}
```

!!! warning "Required Trigger Outputs"
    Every node **must** have `Start`, `Stop`, and `Error` trigger outputs in its schema.

