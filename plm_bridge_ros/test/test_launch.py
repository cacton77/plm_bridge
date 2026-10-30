"""The launch file builds a description without starting anything."""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip('launch_ros')


def test_launch_description_declares_the_cell_arguments():
    path = Path(__file__).parents[1] / 'launch' / 'plm_bridge.launch.py'
    spec = importlib.util.spec_from_file_location('plm_bridge_launch', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    description = module.generate_launch_description()
    names = {a.name for a in description.entities if hasattr(a, 'name')
             and type(a).__name__ == 'DeclareLaunchArgument'}
    assert {'plm_backends', 'picker', 'picker_port', 'sync_interval', 'sync_on_startup',
            'describe_plans_service', 'namespace'} <= names
