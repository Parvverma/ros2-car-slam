import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('my_robot')
    xacro_file = os.path.join(pkg, 'urdf', 'my_robot.urdf.xacro')
    world_file = os.path.join(pkg, 'worlds', 'room.sdf')
    ekf_file = os.path.join(pkg, 'config', 'ekf.yaml')

    # 1) Gazebo Classic (gzserver = physics, gzclient = window).
    #    gazebo.launch.py also loads libgazebo_ros_init, which publishes /clock.
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'),
                         'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world_file}.items())

    # 2) xacro -> URDF, then publish /robot_description and static TFs
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)
    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description,
                            'use_sim_time': True}])

    # 3) Spawn the robot into Gazebo from the /robot_description topic
    spawn = Node(package='gazebo_ros', executable='spawn_entity.py',
                 arguments=['-topic', 'robot_description',
                            '-entity', 'my_robot',
                            '-x', '-2.5', '-y', '-2.5', '-z', '0.1'],
                 output='screen')

    # 4) EKF: fuses /wheel/odom + /imu -> /odom + TF odom->base_footprint
    ekf = Node(package='robot_localization', executable='ekf_node',
               name='ekf_filter_node', output='screen',
               parameters=[ekf_file],
               remappings=[('odometry/filtered', '/odom')])

    return LaunchDescription([gazebo, rsp, spawn, ekf])