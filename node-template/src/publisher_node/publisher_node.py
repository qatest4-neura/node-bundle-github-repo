from neuraverse.models.v1.gen.business.node_graph_pb2 import NodeConfigEntry, NodeConfigValue, ToggleValue, RangeValue, \
    SingleSelectListValue, MultiSelectListValue
from neuraverse_sdk.models.node_models import NodeVisualizationsTopic, NodeVisualizationsTopics
from neuraverse_sdk.node_base import NodeBase


class PublisherNode(NodeBase):
    """
    A simple example node that re-publishes input data
    """

    def __init__(self):
        super().__init__()

    def on_execute(self) -> None:
        """Execute the main node logic — reads all inputs, logs them, publishes to outputs."""
        self.log_info("Executing Re-publisher node")

        text_msg = self.get_data("text_input")
        if text_msg:
            self.log_info(f"[String] text_input: {text_msg.data}")
            self.publish("text_output", text_msg)

        float32_msg = self.get_data("float32_input")
        if float32_msg:
            self.log_info(f"[Float32] float32_input: {float32_msg.data}")
            self.publish("float32_output", float32_msg)

        float64_msg = self.get_data("float64_input")
        if float64_msg:
            self.log_info(f"[Float64] float64_input: {float64_msg.data}")
            self.publish("float64_output", float64_msg)

        int32_msg = self.get_data("int32_input")
        if int32_msg:
            self.log_info(f"[Int32] int32_input: {int32_msg.data}")
            self.publish("int32_output", int32_msg)

        int64_msg = self.get_data("int64_input")
        if int64_msg:
            self.log_info(f"[Int64] int64_input: {int64_msg.data}")
            self.publish("int64_output", int64_msg)

        bool_msg = self.get_data("bool_input")
        if bool_msg:
            self.log_info(f"[Bool] bool_input: {bool_msg.data}")
            self.publish("bool_output", bool_msg)

        float_arr_msg = self.get_data("float_array_input")
        if float_arr_msg:
            self.log_info(f"[Float32MultiArray] float_array_input: {float_arr_msg.data}")
            self.publish("float_array_output", float_arr_msg)

        int_arr_msg = self.get_data("int_array_input")
        if int_arr_msg:
            self.log_info(f"[Int32MultiArray] int_array_input: {int_arr_msg.data}")
            self.publish("int_array_output", int_arr_msg)

        image_msg = self.get_data("image_input")
        if image_msg:
            self.log_info(f"[CompressedImage] image_input: format={image_msg.format}, data_len={len(image_msg.data)}")
            self.publish("image_output", image_msg)

        twist_msg = self.get_data("twist_input")
        if twist_msg:
            self.log_info(f"[Twist] twist_input: linear=({twist_msg.linear.x}, {twist_msg.linear.y}, {twist_msg.linear.z}), angular=({twist_msg.angular.x}, {twist_msg.angular.y}, {twist_msg.angular.z})")
            self.publish("twist_output", twist_msg)

        audio_msg = self.get_data("audio_input")
        if audio_msg:
            self.log_info(f"[AudioData] audio_input: data_len={len(audio_msg.data)}")
            self.publish("audio_output", audio_msg)


    def on_stop(self) -> None:
        """Called when the node is stopped"""
        self.log_info(f"Stopping Node 1")

    def on_cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def on_configure(self, config, dynamic_config=None) -> None:
        """Handle configuration updates"""
        if dynamic_config:
            self.log_info(f"Received dynamic configuration with {len(dynamic_config)} entries")
            for key, entry in dynamic_config.items():
                self.log_info(f"  Config [{key}]: {entry}")

    def on_get_data_visualization_topics(self) -> NodeVisualizationsTopics:
        return NodeVisualizationsTopics(
            topics=[
                NodeVisualizationsTopic(
                    topic_name="/ros2_topic_name",
                    visualization_type="std_msgs/Float64",
                )
            ]
        )

    def on_get_configuration(self) -> dict[str, NodeConfigEntry]:
        """Get the configuration of the node"""

        return {
            "node_name": NodeConfigEntry(
                configValue=NodeConfigValue(stringValue="NumbersPublisher"),
                displayLabel="Node Name",
                description="Display name for this publisher node",
                readOnly=True,
                required=True,
            ),
            "enabled": NodeConfigEntry(
                configValue=NodeConfigValue(
                    toggleValue=ToggleValue(enabled=True),
                ),
                displayLabel="Enabled",
                description="Whether the node should actively publish numbers",
                required=True,
            ),
            "publish_rate": NodeConfigEntry(
                configValue=NodeConfigValue(
                    rangeValue=RangeValue(min=0.1, max=100.0, value=10.0, step=0.1),
                ),
                displayLabel="Publish Rate",
                description="How often numbers are published",
                unit="Hz",
                required=True,
            ),
            "distribution": NodeConfigEntry(
                configValue=NodeConfigValue(
                    singleSelectListValue=SingleSelectListValue(
                        allowedItems=["uniform", "gaussian", "exponential"],
                        selectedItem="uniform",
                    ),
                ),
                displayLabel="Distribution",
                description="Statistical distribution used to generate random numbers",
            ),
            "active_outputs": NodeConfigEntry(
                configValue=NodeConfigValue(
                    multiSelectListValue=MultiSelectListValue(
                        allowedItems=["float_1", "float_2"],
                        selectedItems=["float_1", "float_2"],
                    ),
                ),
                displayLabel="Active Outputs",
                description="Which output ports should publish data",
                required=True,
            ),
        }

    def on_pause(self) -> None:
        """Called when the node is paused"""
        pass

    def on_resume(self) -> None:
        """Called when the node is resumed"""
        pass
