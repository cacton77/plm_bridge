"""Launch the plm_bridge node, which also serves the part picker UI.

The node hosts the backends named by `plm_backends` (default: the
PLM_BACKENDS environment variable, else dx3). Backend credentials come only
from the environment (for dx3, the DX_* variables); without them the node
still starts and serves whatever is already cached.

    ros2 launch plm_bridge_ros plm_bridge.launch.py
    ros2 launch plm_bridge_ros plm_bridge.launch.py picker:=false
    ros2 launch plm_bridge_ros plm_bridge.launch.py \\
        describe_plans_service:=viewpoint_generation/describe_plans
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    arguments = [
        DeclareLaunchArgument(
            'plm_backends',
            default_value=EnvironmentVariable('PLM_BACKENDS', default_value='dx3'),
            description="Comma-separated PLM backends to host (e.g. 'dx3')."),
        DeclareLaunchArgument(
            'sync_interval', default_value='300',
            description='Seconds between background incremental syncs (0 disables).'),
        DeclareLaunchArgument(
            'sync_on_startup', default_value='true',
            description='Run a full sync when the node starts.'),
        DeclareLaunchArgument(
            'mesh_units', default_value='mm',
            description='Units announced with selections of non-STEP models.'),
        DeclareLaunchArgument(
            'picker', default_value='true',
            description='Serve the browser part picker from the node.'),
        DeclareLaunchArgument(
            'picker_port', default_value='5050',
            description='Port the part picker listens on.'),
        DeclareLaunchArgument(
            'describe_plans_service', default_value='',
            description="The plan producer's DescribePlans service (empty: none), used "
                        "by the picker's 'Scan for files'."),
        DeclareLaunchArgument(
            'namespace', default_value='catalog',
            description='Namespace of the services and topics (/<namespace>/part_selected, ...).'),
    ]

    node = Node(
        package='plm_bridge_ros',
        executable='plm_bridge_node',
        name='plm_bridge',
        parameters=[{
            'catalog.backends': LaunchConfiguration('plm_backends'),
            'catalog.sync_interval': LaunchConfiguration('sync_interval'),
            'catalog.sync_on_startup': LaunchConfiguration('sync_on_startup'),
            'catalog.mesh_units': LaunchConfiguration('mesh_units'),
            'catalog.picker_enabled': LaunchConfiguration('picker'),
            'catalog.picker_port': LaunchConfiguration('picker_port'),
            'catalog.namespace': LaunchConfiguration('namespace'),
            'catalog.describe_plans_service': LaunchConfiguration('describe_plans_service'),
        }],
        output='screen',
        emulate_tty=True,
    )
    return LaunchDescription(arguments + [node])
