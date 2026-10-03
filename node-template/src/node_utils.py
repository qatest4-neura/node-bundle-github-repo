import importlib.util
import inspect
import os
import re
import sys
import types
from pathlib import Path

from neuraverse_sdk.node_base import NodeBase


def get_pyproject_fpath() -> str:
    root_dirpath = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(root_dirpath, 'pyproject.toml')


def set_env_defaults() -> None:
    root_dirpath = os.path.dirname(os.path.dirname(__file__))
    service_config_path = os.path.join(root_dirpath, 'config/service_config.yaml')
    log_config_path = os.path.join(root_dirpath, 'config/log_config.yaml')

    with open(get_pyproject_fpath()) as f:
        pyproject = f.read()
    name_match = re.search(r'^name\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    assert name_match and version_match, f"Could not parse name/version from {get_pyproject_fpath()}"

    os.environ.setdefault('SERVICE_NAME', name_match.group(1))
    os.environ.setdefault('SERVICE_TAG', version_match.group(1))
    os.environ.setdefault('AUTH_JWKS_URL', 'https://account.qa.neuraverse.com/.well-known/jwks.json
    os.environ.setdefault('AUTH_ISSUER', 'https://account.qa.neuraverse.com/')
    os.environ.setdefault('SERVICE_CONFIG', service_config_path)
    os.environ.setdefault('ENVVAR_LOG_CFG_PATH', log_config_path)
    os.environ.setdefault('ENVVAR_CFG_PATH', service_config_path)


def discover_node_classes(src_dirpath: str) -> list[type[NodeBase]]:
    if src_dirpath not in sys.path:
        sys.path.insert(0, src_dirpath)

    node_classes = []
    for fpath in Path(src_dirpath).rglob('*.py'):
        module = _load_module(str(fpath), src_dirpath)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, NodeBase) and cls is not NodeBase and cls not in node_classes:
                node_classes.append(cls)
    return node_classes


def _load_module(fpath: str, src_dirpath: str) -> types.ModuleType:
    rel = Path(fpath).relative_to(src_dirpath)
    module_name = str(rel.with_suffix('')).replace(os.sep, '.')
    spec = importlib.util.spec_from_file_location(module_name, fpath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
