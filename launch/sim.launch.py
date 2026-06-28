"""Launch Gazebo Harmonic simulation with the Straddle Carrier."""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    ExecuteProcess,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = get_package_share_directory("sim_straddle_carrier")

    # ── Arguments ────────────────────────────────────────────────────────────
    world_arg = DeclareLaunchArgument(
        "world",
        default_value=os.path.join(pkg, "worlds", "port_yard.sdf"),
        description="Path to the Gazebo SDF world file",
    )
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz", default_value="true", description="Launch RViz2"
    )
    x_arg = DeclareLaunchArgument("x", default_value="0.0")
    y_arg = DeclareLaunchArgument("y", default_value="0.0")
    z_arg = DeclareLaunchArgument("z", default_value="0.5")
    yaw_arg = DeclareLaunchArgument("yaw", default_value="0.0")

    # ── Robot description (xacro → URDF) ─────────────────────────────────────
    xacro_file = os.path.join(pkg, "description", "urdf", "straddle_carrier.urdf.xacro")
    robot_description = {"robot_description": ExecuteProcess(
        cmd=["xacro", xacro_file], output="screen"
    )}

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": open(xacro_file).read()
            if os.path.exists(xacro_file) else "",
            "use_sim_time": True,
        }],
    )

    # ── Gazebo Harmonic ───────────────────────────────────────────────────────
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py",
            ])
        ),
        launch_arguments={"gz_args": [LaunchConfiguration("world"), " -r"]}.items(),
    )

    # ── Spawn robot into Gazebo ───────────────────────────────────────────────
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "straddle_carrier",
            "-topic", "/robot_description",
            "-x", LaunchConfiguration("x"),
            "-y", LaunchConfiguration("y"),
            "-z", LaunchConfiguration("z"),
            "-Y", LaunchConfiguration("yaw"),
        ],
        output="screen",
    )

    # ── ROS ↔ Gazebo bridge ───────────────────────────────────────────────────
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V",
            "/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model",
            "/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock",
        ],
        output="screen",
    )

    # ── Control node ──────────────────────────────────────────────────────────
    control_node = Node(
        package="sim_straddle_carrier",
        executable="control_node",
        name="control_node",
        output="screen",
        parameters=[
            os.path.join(pkg, "config", "sim_params.yaml"),
            {"use_sim_time": True},
        ],
    )

    # ── RViz2 ─────────────────────────────────────────────────────────────────
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", os.path.join(pkg, "config", "default.rviz")],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription([
        world_arg, use_rviz_arg, x_arg, y_arg, z_arg, yaw_arg,
        robot_state_publisher,
        gz_sim,
        spawn_robot,
        gz_bridge,
        control_node,
        rviz_node,
    ])
