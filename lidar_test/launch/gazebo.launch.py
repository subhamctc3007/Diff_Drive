from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import ExecuteProcess, TimerAction

from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_path = get_package_share_directory('lidar_test')

    xacro_file = os.path.join(
        pkg_path,
        'description',
        'lidar.urdf.xacro'
    )

    sdf_file = os.path.join(
        pkg_path,
        'description',
        'lidar_bot.sdf'
    )

    bridge_file = os.path.join(
        pkg_path,
        'config',
        'gz_bridge.yaml'
    )

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description}
        ]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )

    spawn_entity = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', '/robot_description',
                    '-name', 'lidar_bot'
                ],
                output='screen'
            )
        ]
    )

    gz_bridge = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                parameters=[{
                    'config_file': bridge_file,
                }],
                output='screen'
            )
        ]
    )

    static_lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'lidar_bot/base_link/lidar'
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity,
        gz_bridge,
        # static_lidar_tf
    ])