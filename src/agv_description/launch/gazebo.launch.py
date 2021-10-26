import os

import launch_ros
from ament_index_python.packages import get_package_share_directory

import launch
from launch.substitutions import Command, LaunchConfiguration


def generate_launch_description():
    pkg_share = launch_ros.substitutions.FindPackageShare(
        package="agv_description"
    ).find("agv_description")
    aws_small_warehouse_dir = get_package_share_directory(
        "aws_robomaker_small_warehouse_world"
    )
    default_model_path = os.path.join(pkg_share, "src/urdf/main.xacro")
    default_rviz_config_path = os.path.join(pkg_share, "rviz/urdf_config.rviz")

    world = LaunchConfiguration("world")

    robot_state_publisher_node = launch_ros.actions.Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {"robot_description": Command(["xacro ", LaunchConfiguration("model")])}
        ],
    )
    joint_state_publisher_node = launch_ros.actions.Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        condition=launch.conditions.UnlessCondition(LaunchConfiguration("gui")),
    )
    spawn_entity = launch_ros.actions.Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity",
            "agv",
            "-topic",
            "robot_description",
            "-z",
            "0.5",
        ],
        output="screen",
    )
    robot_localization_node = launch_ros.actions.Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            os.path.join(pkg_share, "config/ekf.yaml"),
            {"use_sim_time": LaunchConfiguration("use_sim_time")},
        ],
    )

    return launch.LaunchDescription(
        [
            launch.actions.DeclareLaunchArgument(
                name="use_sim_time",
                default_value="True",
                description="Flag to enable use_sim_time",
            ),
            launch.actions.DeclareLaunchArgument(
                name="gui",
                default_value="True",
                description="Flag to enable joint_state_publisher_gui",
            ),
            launch.actions.DeclareLaunchArgument(
                name="model",
                default_value=default_model_path,
                description="Absolute path to robot urdf file",
            ),
            launch.actions.DeclareLaunchArgument(
                name="rvizconfig",
                default_value=default_rviz_config_path,
                description="Absolute path to rviz config file",
            ),
            launch.actions.DeclareLaunchArgument(
                "world",
                default_value=os.path.join(
                    aws_small_warehouse_dir,
                    "worlds",
                    "no_roof_small_warehouse",
                    "no_roof_small_warehouse.world",
                ),
                description="Full path to world model file to load",
            ),
            launch.actions.ExecuteProcess(
                cmd=["gazebo", "--verbose", "-s", "libgazebo_ros_factory.so", world],
                cwd=[aws_small_warehouse_dir],
                output="screen",
            ),
            robot_state_publisher_node,
            joint_state_publisher_node,
            spawn_entity,
            robot_localization_node,
            # rviz_node,
        ]
    )
