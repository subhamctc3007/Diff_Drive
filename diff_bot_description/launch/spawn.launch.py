from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction
from launch.actions import SetEnvironmentVariable

from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_share = get_package_share_directory('diff_bot_description')

    resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.environ.get('GZ_SIM_RESOURCE_PATH', '') + ':' + pkg_share
    )

    # Include your existing URDF launch
    urdf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'urdf.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'use_rviz': 'false',
            'use_jsp': 'false'
        }.items()
    )

    # Spawn robot into Gazebo (gz sim)
    spawn = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-name', 'diff_bot',
                    '-topic', '/robot_description',
                    '-x', '0.0',
                    '-y', '-0.5',
                    '-z', '0.2',
                ],
                output='screen'
            )
        ]
    )

    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_share, 'config', 'gz_bridge.yaml')
        }],
        output='screen'
    )

    controller_manager = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller"],
    )

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        prefix='xterm -e',  # opens teleop in its own terminal
        output='screen',
        parameters=[
            {'stamped': True}
        ],
        remappings=[
            ('/cmd_vel', '/diff_drive_controller/cmd_vel')
        ]
    )

    return LaunchDescription([
        resource_path,
        urdf_launch,
        spawn,
        controller_manager,
        joint_state_broadcaster,
        gz_bridge,
        # teleop,
    ])