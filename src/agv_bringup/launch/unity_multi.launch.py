import os

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions.node import Node
from launch_ros.actions.push_ros_namespace import PushRosNamespace
from launch_ros.actions.set_remap import SetRemap

from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.actions.declare_launch_argument import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration

package_dir = get_package_share_directory("agv_bringup")
config_dir = os.path.join(package_dir, "config")
maps_dir = os.path.join(package_dir, "maps")
launch_dir = os.path.join(package_dir, "launch")


def generate_action_groups(robots):
    action_groups = []
    slam_param = LaunchConfiguration("slam")
    amcl_param = LaunchConfiguration("amcl")
    rviz_param = LaunchConfiguration("rviz")
    remaps = [
        SetRemap(src="/tf", dst="tf"),
        SetRemap(src="/tf_static", dst="tf_static"),
        # Force root /map
        SetRemap(src="map", dst="/map"),
        SetRemap(src="map_metadata", dst="/map_metadata"),
    ]
    for robot in robots:
        action_groups.append(
            GroupAction(
                [
                    # Push the robot's namespace
                    PushRosNamespace(robot),
                    # Expand shared remappings
                    *remaps,
                    # SLAM Launch
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(
                            os.path.join(launch_dir, "slam.launch.py")
                        ),
                        condition=IfCondition(slam_param),
                        launch_arguments={
                            "use_sim_time": "true",
                            "namespace": robot,
                            "params_file": os.path.join(config_dir, "slam_params.yaml"),
                        }.items(),
                    ),
                    # AMCL Launch
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(
                            os.path.join(launch_dir, "amcl.launch.py")
                        ),
                        condition=IfCondition(amcl_param),
                        launch_arguments={
                            "use_sim_time": "true",
                            "namespace": robot,
                            "params_file": os.path.join(config_dir, "amcl_params.yaml"),
                        }.items(),
                    ),
                    # NAV2 Launch
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(
                            os.path.join(launch_dir, "navigation.launch.py")
                        ),
                        launch_arguments={
                            "use_sim_time": "true",
                            "namespace": robot,
                            "params_file": os.path.join(config_dir, "navigation_params.yaml"),
                        }.items(),
                    ),
                    # Gazebo Spawn
                    # Node(
                    #     package="robot_state_publisher",
                    #     executable="robot_state_publisher",
                    #     parameters=[
                    #         {
                    #             "robot_description": Command(
                    #                 ["xacro ", LaunchConfiguration("model")]
                    #             )
                    #         }
                    #     ],
                    # ),
                    # Node(
                    #     package="gazebo_ros",
                    #     executable="spawn_entity.py",
                    #     output="screen",
                    #     arguments=[
                    #         "-entity",
                    #         robot,
                    #         "-topic",
                    #         "robot_description",
                    #         "-robot_namespace",
                    #         robot,
                    #     ],
                    # ),
                    # RVIZ Launch
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(
                            os.path.join(launch_dir, "rviz.launch.py")
                        ),
                        condition=IfCondition(rviz_param),
                        launch_arguments={
                            "namespace": robot,
                            "rviz_config": os.path.join(config_dir, "nav2_unity.rviz"),
                        }.items(),
                    ),
                ]
            )
        )

    return action_groups


def generate_launch_description():

    map_param = LaunchConfiguration("map")

    robots = ["agv0"]

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "slam", default_value="false", description="Run slam node"
            ),
            DeclareLaunchArgument(
                "amcl",
                default_value="false",
                description="Run AMCL node",
            ),
            DeclareLaunchArgument("map", default_value="", description="map file"),
            DeclareLaunchArgument(
                "rviz", default_value="true", description="Run rviz node"
            ),
            # Map Server Launch
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(launch_dir, "map_server.launch.py")
                ),
                # condition=IfCondition(rviz_param),
                launch_arguments={
                    "use_sim_time": "true",
                    "map": os.path.join(maps_dir, "warehouse.yaml"),
                    "params_file": os.path.join(config_dir, "map_server_params.yaml"),
                }.items(),
            ),
            # Expand the action groups for each robot
            *generate_action_groups(robots),
        ]
    )
