"""Interactive terminal CLI for the Neuraverse Mock Runner."""

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Neuraverse Node Mock Runner — test nodes locally"
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("MOCK_RUNNER_PROJECT", "."),
        help="Path to the node project (default: current directory or $MOCK_RUNNER_PROJECT)",
    )
    args = parser.parse_args()

    project_path = os.path.abspath(args.project)

    # ROS2 mocks must be set up before importing SDK classes
    _setup_ros_mocks()

    from mock_runner.runner import MockRunner

    print(f"\n{'=' * 50}")
    print("  Neuraverse Node Mock Runner")
    print(f"{'=' * 50}")
    print(f"  Project: {project_path}\n")

    try:
        runner = MockRunner(project_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    nodes = runner.list_nodes()
    if not nodes:
        print("No nodes found in project. Ensure your nodes inherit from NodeBase.")
        sys.exit(1)

    while True:
        node_name = _select_node(nodes)
        if node_name is None:
            break
        _run_node_session(runner, node_name)

    print("\nGoodbye!")


def _select_node(nodes: list[dict]) -> str | None:
    """Let user pick a node from the discovered list."""
    print("Available nodes:")
    for i, n in enumerate(nodes, 1):
        desc = f" — {n['description']}" if n["description"] else ""
        print(f"  {i}. {n['name']}{desc}")
    print(f"  0. Exit")

    while True:
        choice = input("\nSelect node [number]: ").strip()
        if choice == "0":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(nodes):
                return nodes[idx]["name"]
        except ValueError:
            pass
        print("Invalid choice. Try again.")


def _run_node_session(runner, class_name: str):
    """Interactive session for a single node."""
    # Configure
    config = _prompt_configuration(runner, class_name)
    result = runner.configure_node(class_name, config)

    if not result["success"]:
        print(f"\nConfiguration failed: {result['error']}")
        if "traceback" in result:
            print(result["traceback"])
        return

    print(f"\n  Node configured successfully!")
    print(f"  ID: {result['node_id']}")
    print(f"  State: {result['state']}")
    if result["input_ports"]:
        print(f"  Input ports: {', '.join(result['input_ports'])}")
    if result["output_ports"]:
        print(f"  Output ports: {', '.join(result['output_ports'])}")

    # Action loop
    while True:
        action = _show_action_menu()
        if action == "execute":
            _do_execute(runner)
        elif action == "inject":
            _do_inject(runner)
        elif action == "outputs":
            _do_show_outputs(runner)
        elif action == "state":
            print(f"\n  State: {runner.get_state()}")
        elif action == "status_log":
            _do_show_status_log(runner)
        elif action == "reconfigure":
            config = _prompt_configuration(runner, class_name)
            result = runner.configure_node(class_name, config)
            if result["success"]:
                print(f"\n  Reconfigured. State: {result['state']}")
            else:
                print(f"\n  Reconfigure failed: {result['error']}")
        elif action == "stop":
            result = runner.stop_node()
            print(f"\n  Node stopped. State: {result.get('state', 'STOPPED')}")
            break
        elif action == "switch":
            runner.stop_node()
            break


def _prompt_configuration(runner, class_name: str) -> dict[str, str]:
    """Prompt user for key=value configuration pairs."""
    schema = runner.get_node_schema(class_name)
    config_keys = list((schema or {}).get("configuration", {}).keys())

    print(f"\n--- Configure {class_name} ---")
    if config_keys:
        print(f"  Known config keys: {', '.join(config_keys)}")
    print("  Enter key=value pairs (empty line to finish):")

    config = {}
    while True:
        line = input("  > ").strip()
        if not line:
            break
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
        else:
            print("  Invalid format. Use: key=value")
    return config


def _show_action_menu() -> str:
    """Show action menu and return the chosen action."""
    print(f"\n--- Actions ---")
    actions = [
        ("1", "execute", "Execute node"),
        ("2", "inject", "Inject input data"),
        ("3", "outputs", "Show published outputs"),
        ("4", "state", "Show current state"),
        ("5", "status_log", "Show status log"),
        ("6", "reconfigure", "Reconfigure node"),
        ("7", "stop", "Stop node"),
        ("8", "switch", "Switch to another node"),
    ]
    for num, _, label in actions:
        print(f"  {num}. {label}")

    while True:
        choice = input("\n> ").strip()
        for num, action, _ in actions:
            if choice == num:
                return action
        print("Invalid choice.")


def _do_execute(runner):
    """Execute the node and show results."""
    print("\nExecuting...")
    result = runner.execute_node()
    if result["success"]:
        print(f"  Completed in {result['execution_time']}s")
        print(f"  State: {result['state']}")
        if result["triggers_fired"]:
            print(f"  Triggers fired: {', '.join(result['triggers_fired'])}")
        if result["outputs"]:
            print("  Outputs:")
            for port, msgs in result["outputs"].items():
                for msg in msgs:
                    print(f"    {port}: {msg}")
    else:
        print(f"  Execution failed: {result['error']}")
        if "traceback" in result:
            print(result["traceback"])


def _do_inject(runner):
    """Inject data into an input port."""
    if not runner.mock_dataflow:
        print("  No dataflow configured.")
        return

    ports = list(runner.mock_dataflow.input_topics.keys())
    if not ports:
        print("  No input ports available.")
        return

    print(f"  Available input ports: {', '.join(ports)}")
    port = input("  Port name: ").strip()
    if port not in ports:
        print(f"  Port '{port}' not found. Creating it anyway...")

    data_str = input("  Data (JSON or plain string): ").strip()
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        data = data_str

    result = runner.inject_input(port, data)
    if result["success"]:
        print(f"  Injected data into '{port}'")
    else:
        print(f"  Injection failed: {result['error']}")


def _do_show_outputs(runner):
    """Display published outputs."""
    result = runner.get_outputs()
    outputs = result.get("outputs", {})
    if not outputs:
        print("  No outputs published yet.")
        return
    print("  Published outputs:")
    for port, msgs in outputs.items():
        for msg in msgs:
            print(f"    {port}: {msg}")


def _do_show_status_log(runner):
    """Display state transition log."""
    log = runner.get_status_log()
    if not log:
        print("  No status transitions recorded.")
        return
    print("  Status log:")
    for entry in log:
        node_id = entry.get("nodeId", "?")
        state = entry.get("state_name", "?")
        msg = entry.get("resultMessage", "")
        code = entry.get("resultCode", 0)
        prefix = "OK" if code == 0 else "ERR"
        print(f"    [{prefix}] {node_id} -> {state}: {msg}")


def _setup_ros_mocks():
    """Mock ROS2 dependencies so the SDK can be imported without ROS2 installed."""
    from unittest.mock import Mock

    if "rclpy" in sys.modules:
        return

    mock_rclpy = Mock()
    mock_rclpy.init = Mock(return_value=None)
    mock_rclpy.ok = Mock(return_value=True)
    mock_rclpy.create_node = Mock(return_value=Mock())

    class MockSingleThreadedExecutor:
        def __init__(self, *a, **kw):
            pass
        def shutdown(self):
            pass
        def spin_once(self, timeout_sec=0.1):
            pass
        def add_node(self, node):
            pass

    mock_executors = Mock()
    mock_executors.SingleThreadedExecutor = MockSingleThreadedExecutor

    mock_serialization = Mock()
    mock_serialization.serialize_message = Mock(return_value=b"mock")
    mock_serialization.deserialize_message = Mock(return_value=Mock())

    sys.modules["rclpy"] = mock_rclpy
    sys.modules["rclpy.executors"] = mock_executors
    sys.modules["rclpy.serialization"] = mock_serialization


if __name__ == "__main__":
    main()
