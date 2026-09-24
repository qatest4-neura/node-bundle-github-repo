"""FastAPI web server for the Neuraverse Mock Runner."""

import argparse
import json
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


# ROS mocks must be installed before any SDK import
def _setup_ros_mocks():
    from unittest.mock import Mock
    if "rclpy" in sys.modules:
        return
    mock_rclpy = Mock()
    mock_rclpy.init = Mock(return_value=None)
    mock_rclpy.ok = Mock(return_value=True)
    mock_rclpy.create_node = Mock(return_value=Mock())

    class MockSingleThreadedExecutor:
        def __init__(self, *a, **kw): pass
        def shutdown(self): pass
        def spin_once(self, timeout_sec=0.1): pass
        def add_node(self, node): pass

    mock_executors = Mock()
    mock_executors.SingleThreadedExecutor = MockSingleThreadedExecutor
    mock_serialization = Mock()
    mock_serialization.serialize_message = Mock(return_value=b"mock")
    mock_serialization.deserialize_message = Mock(return_value=Mock())
    sys.modules["rclpy"] = mock_rclpy
    sys.modules["rclpy.executors"] = mock_executors
    sys.modules["rclpy.serialization"] = mock_serialization


_setup_ros_mocks()

from mock_runner.runner import MockRunner  # noqa: E402

app = FastAPI(title="Neuraverse Mock Runner", version="0.1.0")

# Global runner instance — initialized at startup
_runner: MockRunner | None = None

STATIC_DIR = Path(__file__).parent / "static"


# --- Request models ---

class InitRequest(BaseModel):
    class_name: str


class ConfigureRequest(BaseModel):
    class_name: str
    config: dict[str, str] = {}
    dynamic_config: dict[str, dict] | None = None


class InjectRequest(BaseModel):
    port_name: str
    ros_type: str = ""
    fields: dict = {}
    data: str | None = None  # Legacy fallback


# --- API endpoints ---

@app.get("/api/nodes")
def list_nodes():
    return _runner.list_nodes()


@app.get("/api/nodes/{name}/schema")
def get_node_schema(name: str):
    schema = _runner.get_node_schema(name)
    if schema is None:
        return {"schema": None}
    return {"schema": schema}


@app.post("/api/init")
def init_node(req: InitRequest):
    result = _runner.init_node(req.class_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Initialization failed"))
    return result


@app.post("/api/configure")
def configure_node(req: ConfigureRequest):
    result = _runner.configure_node(req.class_name, req.config, req.dynamic_config)
    if not result["success"]:
        error_msg = result.get("error", "Configuration failed")
        tb = result.get("traceback", "")
        if tb:
            print(f"Configure error: {error_msg}\n{tb}", flush=True)
        raise HTTPException(status_code=400, detail=error_msg)
    return result


@app.post("/api/execute")
def execute_node():
    result = _runner.execute_node()
    return result


@app.post("/api/inject")
def inject_input(req: InjectRequest):
    if req.ros_type and req.fields:
        result = _runner.inject_input(req.port_name, ros_type=req.ros_type, fields=req.fields)
    else:
        # Legacy: raw data fallback
        data = req.data
        if data:
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                pass
        result = _runner.inject_input(req.port_name, data=data)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Injection failed"))
    return result


@app.get("/api/outputs")
def get_outputs():
    return _runner.get_outputs()


@app.get("/api/state")
def get_state():
    return {
        "state": _runner.get_state(),
        "node_name": _runner.current_node_name,
    }


@app.get("/api/status-log")
def get_status_log():
    return _runner.get_status_log()


@app.get("/api/logs")
def get_logs():
    return _runner.get_logs()


@app.post("/api/logs/clear")
def clear_logs():
    _runner.clear_logs()
    return {"success": True}


@app.get("/api/ros-types")
def get_ros_types():
    from mock_runner.ros_types import ROS_TYPE_SCHEMAS, get_type_schema
    return {"schemas": ROS_TYPE_SCHEMAS, "get_schema": "Use /api/ros-types/{type} for specific type"}


@app.get("/api/ros-types/{ros_type:path}")
def get_ros_type_schema(ros_type: str):
    from mock_runner.ros_types import get_type_schema
    return get_type_schema(ros_type)


@app.post("/api/reload")
def reload_nodes():
    return _runner.reload_nodes()


@app.post("/api/stop")
def stop_node():
    result = _runner.stop_node()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Stop failed"))
    return result


# --- Static file serving ---

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_path = STATIC_DIR / "index.html"
    return index_path.read_text()


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description="Neuraverse Mock Runner — Web UI")
    parser.add_argument(
        "--project",
        default=os.environ.get("MOCK_RUNNER_PROJECT", "."),
        help="Path to the node project",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8599, help="Port (default: 8599)")
    args = parser.parse_args()

    global _runner
    project_path = os.path.abspath(args.project)
    print(f"Loading nodes from: {project_path}")
    _runner = MockRunner(project_path)
    nodes = _runner.list_nodes()
    print(f"Found {len(nodes)} node(s): {', '.join(n['name'] for n in nodes)}")
    print(f"Web UI: http://{args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
