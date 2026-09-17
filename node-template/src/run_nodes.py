from neuraverse_sdk.node_manager_service import run, set_node_classes

from publisher_node.publisher_node import PublisherNode
from hello_world_node.hello_world_node import HelloWorldNode

def main():
    print("🚀 Starting Nodes...")

    # Create and register the node instance
    set_node_classes([PublisherNode, HelloWorldNode])

    print(f"📍 Node created and registered")
    run()


if __name__ == "__main__":
    import os

    import os
    root_dirpath = os.path.dirname(os.path.dirname(__file__))
    service_config_path = os.path.join(root_dirpath, 'config/service_config.yaml')
    log_config_path = os.path.join(root_dirpath, 'config/log_config.yaml')

    os.environ.setdefault('SERVICE_NAME', 'node-error')
    os.environ.setdefault('SERVICE_TAG', '0.8.0')
    os.environ.setdefault('SERVICE_CONFIG', service_config_path)
    os.environ.setdefault('ENVVAR_LOG_CFG_PATH', log_config_path)
    os.environ.setdefault('ENVVAR_CFG_PATH', service_config_path)

    main()
