import os

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    package_name = "unity_slam_example"
    package_dir = get_package_share_directory(package_name)

    return LaunchDescription(
        {
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("ros_tcp_endpoint"),
                        "launch",
                        "endpoint.py",
                    )
                ),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("nav2_bringup"),
                        "launch",
                        "bringup_launch.py",
                    )
                ),
                launch_arguments={
                    "use_sim_time": "true",
                    "map": os.path.join(package_dir, "warehouse.yaml"),
                    "params_file": os.path.join(package_dir, "nav_params.yaml"),
                }.items(),
            ),
        }
    )
