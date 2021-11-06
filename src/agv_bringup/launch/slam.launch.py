import os

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml

from launch import LaunchDescription
from launch.actions.declare_launch_argument import DeclareLaunchArgument
from launch.substitutions.launch_configuration import LaunchConfiguration


def generate_launch_description():
    package_name = "agv_bringup"

    package_dir = get_package_share_directory(package_name)
    config_dir = os.path.join(package_dir, "config")

    namespace = LaunchConfiguration("namespace")
    use_sim_time = LaunchConfiguration("use_sim_time")
    params_file = LaunchConfiguration("params_file")

    slam_params = RewrittenYaml(
        source_file=params_file,
        root_key=namespace,
        param_rewrites={"use_sim_time": use_sim_time},
        convert_types=True,
    )

    return LaunchDescription(
        [
            # Declare arguments
            DeclareLaunchArgument(
                "namespace", default_value="", description="Top-level namespace"
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use simulation clock if true",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=os.path.join(config_dir, "slam_params.yaml"),
                description="Full path to the ROS2 parameters file to use",
            ),
            # Include actions
            Node(
                parameters=[slam_params],
                package="slam_toolbox",
                executable="async_slam_toolbox_node",
                name="slam_toolbox",
                output="screen",
            ),
        ]
    )
