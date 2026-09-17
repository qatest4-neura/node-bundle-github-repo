from neuraverse_sdk.models.node_models import NodeVisualizationsTopics, NodeVisualizationsTopic
from neuraverse_sdk.node_base import NodeBase


class HelloWorldNode(NodeBase):
    """
    A hello world node that only prints log messages on execution/stop
    """

    def __init__(self):
        super().__init__()

    def on_execute(self) -> None:
        """Execute the main node logic"""
        self.log_info(f"Hello World from NodeGraph!")


    def on_stop(self) -> None:
        """Called when the node is stopped"""
        self.log_info(f"Stopping HelloWorldNode")

    def on_cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def on_configure(self, config, dynamic_config=None) -> None:
        """Handle configuration updates"""
        pass

    def on_get_data_visualization_topics(self) -> NodeVisualizationsTopics:
        return NodeVisualizationsTopics(
            topics=[
                NodeVisualizationsTopic(
                    topic_name="/ros2_topic_name",
                    visualization_type="std_msgs/Float64",
                )
            ]
        )

    def on_get_configuration(self):
        """Get the configuration of the node"""
        return {}

    def on_pause(self) -> None:
        """Called when the node is paused"""
        pass

    def on_resume(self) -> None:
        """Called when the node is resumed"""
        pass
