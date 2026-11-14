from neuraverse_sdk.node_manager_service import run, set_node_classes
from node_utils import set_env_defaults


def main():
    # Declare node classes explicitly
    from republisher_node.republisher_node import RepublisherNode
    from hello_world_node.hello_world_node import HelloWorldNode
    from float_monitor_node.float_monitor_node import FloatMonitorNode
    from float_publisher_node.float_publisher_node import FloatPublisherNode
    node_classes = [RepublisherNode, HelloWorldNode, FloatMonitorNode, FloatPublisherNode]

    # Alternatively: Auto discover all nodes in src
    # from node_utils import discover_node_classes
    # from pathlib import Path
    # node_classes = discover_node_classes(str(Path(__file__).parent))

    print("🚀 Starting Nodes...")
    set_node_classes(node_classes)

    print(f"📍 Node created and registered")
    run()

if __name__ == "__main__":
    set_env_defaults()
    main()
