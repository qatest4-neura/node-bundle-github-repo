"""Discover NodeBase subclasses and their schemas from a node project."""

import importlib
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any

from neuraverse_sdk.node_base import NodeBase


def discover_nodes(project_path: str) -> dict[str, dict[str, Any]]:
    """Scan a node project's src/ directory for NodeBase subclasses and schemas.

    Args:
        project_path: Root path of the node project (e.g., .../node-template).

    Returns:
        Mapping of class_name -> {"class": NodeClass, "schema": dict|None, "module_path": str}
    """
    src_dir = Path(project_path) / "src"
    if not src_dir.is_dir():
        raise FileNotFoundError(f"No src/ directory found at {src_dir}")

    # Add src/ to sys.path so node modules can be imported
    src_str = str(src_dir)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

    found_nodes: dict[str, dict[str, Any]] = {}

    for py_file in src_dir.rglob("*.py"):
        # Skip __pycache__, __init__, and mock_runner itself
        if "__pycache__" in str(py_file) or py_file.name == "__init__.py":
            continue
        if "mock" in py_file.name.lower():
            continue

        module_name = _path_to_module_name(py_file, src_dir)
        if not module_name:
            continue

        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, NodeBase) and obj is not NodeBase:
                schema = _find_schema(py_file)
                found_nodes[name] = {
                    "class": obj,
                    "schema": schema,
                    "module_path": str(py_file),
                }

    return found_nodes


def _path_to_module_name(py_file: Path, src_dir: Path) -> str | None:
    """Convert a .py file path to a dotted module name relative to src/."""
    try:
        relative = py_file.relative_to(src_dir)
        parts = list(relative.parts)
        parts[-1] = parts[-1].removesuffix(".py")
        return ".".join(parts)
    except ValueError:
        return None


def _find_schema(py_file: Path) -> dict | None:
    """Look for a *_schema.json file alongside a node's .py file."""
    directory = py_file.parent
    for json_file in directory.glob("*_schema.json"):
        try:
            with open(json_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
    return None
