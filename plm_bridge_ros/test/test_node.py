"""The node starts, declares its parameters and serves its services (fake backend)."""

import os

import pytest

rclpy = pytest.importorskip('rclpy')


@pytest.fixture
def node(tmp_path, monkeypatch):
    monkeypatch.setenv('PLM_BACKENDS', 'fake')
    monkeypatch.setenv('CATALOG_ROOT', str(tmp_path / 'catalog'))
    monkeypatch.setenv('CATALOG_SYNC_ON_STARTUP', '0')
    monkeypatch.setenv('CATALOG_SYNC_INTERVAL', '0')
    monkeypatch.setenv('ROS_DOMAIN_ID', os.environ.get('ROS_DOMAIN_ID', '91'))
    from plm_bridge_ros.node import PLMBridgeNode

    rclpy.init()
    instance = PLMBridgeNode()
    yield instance
    instance.catalog.close()
    instance.destroy_node()
    rclpy.shutdown()


def test_node_declares_core_and_backend_parameters(node):
    assert node.get_parameter('core.backends').value == 'fake'
    assert node.get_parameter('core.namespace').value == 'catalog'
    assert node.get_parameter('core.describe_plans_service').value == ''
    assert node.has_parameter('core.sync_interval')
    assert not any(name.startswith('catalog.') for name in node._parameters)
    assert set(node.catalog.backends) == {'fake'}


def test_node_serves_the_catalog_services(node):
    services = {name for name, _ in node.get_service_names_and_types()
                if name.startswith('/catalog/')}
    assert {'/catalog/list_backends', '/catalog/list_parts', '/catalog/select_part',
            '/catalog/sync_now', '/catalog/ensure_plan', '/catalog/record_plan',
            '/catalog/upload_plan', '/catalog/upload_results',
            '/catalog/record_run'} <= services
