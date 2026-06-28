# SimStraddleCarrier — Shared Interface Contract

All agents MUST read this file first and MUST NOT deviate from the values below.
Any change to this file requires agreement from the human (You LI).

---

## 1. Vehicle Dimensions (Kalmar/Konecranes 40ft, 1-over-2 stacking)

| Parameter              | Value     | Notes                                   |
|------------------------|-----------|-----------------------------------------|
| Portal inner width     | 6.0 m     | Clear span over container row           |
| Portal outer width     | 9.5 m     | Centre-to-centre of outer tyre pairs    |
| Wheelbase              | 9.5 m     | Front axle to rear axle                 |
| Portal frame height    | 13.5 m    | Top of structural frame                 |
| Wheel radius           | 0.75 m    | 18.00R25 industrial tyre (Ø 1.5 m)     |
| Wheel width            | 0.55 m    |                                         |
| Max travel speed       | 8.0 m/s   | ~30 km/h, unladen                       |
| Max lift speed         | 0.2 m/s   |                                         |
| Lift capacity (SWL)    | 50 000 kg |                                         |

## 2. Spreader (40ft ISO)

| Parameter              | Value     |
|------------------------|-----------|
| Spreader length        | 12.192 m  |
| Spreader width         | 2.438 m   |
| Spreader thickness     | 0.3 m     |
| Lift range (joint)     | 0 – 9.0 m | Prismatic z-axis, lower = 0 m          |

## 3. 40ft ISO Container (world reference)

| Parameter  | Value     |
|------------|-----------|
| Length     | 12.192 m  |
| Width      | 2.438 m   |
| Height     | 2.591 m   |

---

## 4. URDF Joint Names (fixed — control agent depends on these)

| Joint name                  | Type       | Axis  | Parent      | Child                   |
|-----------------------------|------------|-------|-------------|-------------------------|
| `front_left_wheel_joint`    | continuous | Y     | base_link   | front_left_wheel_link   |
| `front_right_wheel_joint`   | continuous | Y     | base_link   | front_right_wheel_link  |
| `rear_left_wheel_joint`     | continuous | Y     | base_link   | rear_left_wheel_link    |
| `rear_right_wheel_joint`    | continuous | Y     | base_link   | rear_right_wheel_link   |
| `spreader_joint`            | prismatic  | Z     | base_link   | spreader_link           |

## 5. URDF Link Names (fixed)

`base_footprint` → `base_link` → wheel links, `spreader_link`

---

## 6. ROS 2 Topic Contract

| Topic                   | Message type                    | Direction           | Description                          |
|-------------------------|---------------------------------|---------------------|--------------------------------------|
| `/cmd_vel`              | `geometry_msgs/Twist`           | External → Gazebo   | linear.x = fwd speed, angular.z = yaw rate |
| `/odom`                 | `nav_msgs/Odometry`             | Gazebo → ROS        | Ground-truth odometry (perfect localisation) |
| `/spreader/cmd`         | `std_msgs/Float64`              | External → Control  | Target lift height in metres [0, 9]  |
| `/spreader/state`       | `std_msgs/Float64`              | Control → External  | Current lift height in metres        |
| `/joint_states`         | `sensor_msgs/JointState`        | Gazebo → ROS        | All joint positions & velocities     |
| `/tf`                   | `tf2_msgs/TFMessage`            | Gazebo → ROS        | Dynamic transforms                   |
| `/tf_static`            | `tf2_msgs/TFMessage`            | RSP → ROS           | Static transforms                    |
| `/clock`                | `rosgraph_msgs/Clock`           | Gazebo → ROS        | Simulation time                      |

---

## 7. Coordinate Convention

- `base_footprint`: on the ground, centre of the vehicle footprint.
- `base_link`: at wheel-centre height (z = wheel_radius = 0.75 m above footprint).
- X: forward (length axis), Y: left, Z: up.
- All angles in radians.

---

## 8. Gazebo Harmonic Plugins (fixed names)

| Plugin system name                        | Used for                     |
|-------------------------------------------|------------------------------|
| `gz::sim::systems::DiffDrive`             | Wheel drive from `/cmd_vel`  |
| `gz::sim::systems::JointPositionController` | Spreader height control    |
| `gz::sim::systems::JointStatePublisher`   | `/joint_states`              |
| `gz::sim::systems::OdometryPublisher`     | `/odom`                      |

---

## 9. Package & File Layout (do not create files outside these paths)

```
SimStraddleCarrier/
  package.xml
  CMakeLists.txt
  description/urdf/straddle_carrier.urdf.xacro   ← Model agent
  worlds/port_yard.sdf                            ← World agent
  launch/sim.launch.py                            ← shared / integration
  config/sim_params.yaml                          ← Control agent
  src/control_node.cpp                            ← Control agent
  include/sim_straddle_carrier/control_node.hpp   ← Control agent
  scripts/teleop.py                               ← Control agent
  agents/                                         ← instruction files only, no runtime code
```
