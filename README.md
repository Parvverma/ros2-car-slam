# ROS 2 Car SLAM Simulation

A ROS 2 and Gazebo Classic simulation of a small four-wheel car with a 2D LiDAR and IMU. The project includes a differential-drive controller, an EKF for local odometry, a Gazebo room world, and a `slam_toolbox` configuration for mapping.

> This is a differential-drive model: the left and right wheel pairs are driven independently. It does not model Ackermann steering geometry.

## Requirements

- Ubuntu with ROS 2 Humble
- Gazebo Classic and its ROS integration (`gazebo_ros`)
- `colcon` and `rosdep`

The ROS dependencies are declared in `src/my_robot/package.xml` and can be installed with `rosdep`.

## Build

From the workspace root:

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

If `rosdep` has not been initialized on this machine, run `sudo rosdep init` once, then `rosdep update` before installing dependencies.

## Run the simulation

In a terminal with the ROS 2 Humble and workspace environments sourced:

```bash
ros2 launch my_robot sim.launch.py
```

This starts Gazebo Classic with the room world, expands and publishes the robot description, spawns the car, and starts `robot_localization`'s EKF. The robot is spawned near `(-2.5, -2.5)`.

## Start SLAM

The simulation launch does not start SLAM automatically. In a second terminal, source both environments and launch the asynchronous `slam_toolbox` mapper with the package configuration:

```bash
cd ~/slam_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:="$(ros2 pkg prefix --share my_robot)/config/slam_toolbox.yaml" \
  use_sim_time:=true
```

The mapper is configured in mapping mode with a 5 cm map resolution. Drive the car around the environment to build a map.

## Drive the car

The Gazebo differential-drive plugin listens on `/cmd_vel`. For example, publish a forward velocity for a few seconds, then publish zero velocity to stop:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.0}}"
```

Stop the publisher with `Ctrl+C`, then send a stop command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

## Topics

| Topic | Purpose |
| --- | --- |
| `/cmd_vel` | Car velocity command |
| `/scan` | 360-sample 2D LiDAR scan, published at 10 Hz |
| `/imu` | Simulated IMU data, published at 100 Hz |
| `/wheel/odom` | Wheel odometry from Gazebo |
| `/odom` | EKF-filtered odometry |
| `/joint_states` | Wheel joint states |
| `/map` | SLAM map, available after starting `slam_toolbox` |

## Project layout

```text
slam_ws/
├── src/my_robot/
│   ├── config/       # EKF and slam_toolbox parameters
│   ├── launch/       # Gazebo, robot spawn, and EKF launch
│   ├── urdf/         # Xacro robot model, sensors, and Gazebo plugins
│   └── worlds/       # Room world with walls and obstacles
├── .gitignore       # Ignores generated build/install/log and local files
└── README.md
```