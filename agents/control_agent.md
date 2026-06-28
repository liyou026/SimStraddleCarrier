# Control Agent Instructions

## Goal
Implement a ROS 2 control node that:
1. Forwards velocity commands (with clamping) to the Gazebo diff-drive plugin.
2. Drives the spreader to a target height via a simple P-controller that commands
   the Gazebo JointPositionController.
3. Publishes current spreader state.

No autonomy, no path planning — just safe command forwarding.

## Read First
`agents/interfaces.md` — topic names, joint names, and speed limits are fixed there.

## Scope — files you own
- `src/control_node.cpp`
- `include/sim_straddle_carrier/control_node.hpp`
- `config/sim_params.yaml`
- `scripts/teleop.py`

Do NOT modify `CMakeLists.txt` or `package.xml` unless a dependency is genuinely
missing (and note what you added and why).

## Off-limits — do not touch
- `description/`, `worlds/`, `launch/`, `agents/`

---

## What to build

### control_node (C++)

**Subscriptions**
| Topic                    | Type                        | Action                                      |
|--------------------------|-----------------------------|---------------------------------------------|
| `/straddle_carrier/cmd_vel` | `geometry_msgs/Twist`    | Clamp + forward to `/cmd_vel`               |
| `/spreader/cmd`          | `std_msgs/Float64`          | Store target height, drive spreader         |
| `/joint_states`          | `sensor_msgs/JointState`    | Read `spreader_joint` position              |

**Publications**
| Topic               | Type               | Description                        |
|---------------------|--------------------|------------------------------------|
| `/cmd_vel`          | `geometry_msgs/Twist` | Clamped velocity to Gazebo        |
| `/spreader/state`   | `std_msgs/Float64` | Current spreader height (m)        |

**Parameters** (in `config/sim_params.yaml`)
- `max_linear_vel`: 8.0 m/s
- `max_angular_vel`: 0.5 rad/s

**Clamping rules**
- `linear.x`  → clamp to `[-max_linear_vel, +max_linear_vel]`
- `angular.z` → clamp to `[-max_angular_vel, +max_angular_vel]`
- All other Twist fields → set to 0.0 before forwarding

**Spreader**
- Target height clamped to [0.0, 9.0] m.
- Publish current height from `joint_states` at 20 Hz on `/spreader/state`.
- No PID needed — JointPositionController in Gazebo handles the servo loop.
  Just forward the clamped setpoint to `/spreader/cmd` (the Gazebo topic).

### teleop.py (Python)
Keyboard teleoperation. Keys:
- W/S: increase/decrease linear.x by 0.5 m/s
- A/D: increase/decrease angular.z by 0.1 rad/s
- Q/E: hoist up / down by 0.5 m per keypress
- Space: full stop (linear and angular to 0, spreader unchanged)
- Ctrl-C: exit

Publishes to `/straddle_carrier/cmd_vel` and `/spreader/cmd`.
Prints current speed + spreader height to terminal each keypress.

---

## Done Criteria
- [ ] `control_node` compiles with `colcon build`.
- [ ] Subscribes to `/straddle_carrier/cmd_vel` and republishes clamped to `/cmd_vel`.
- [ ] Subscribes to `/joint_states`, extracts `spreader_joint` position, publishes to `/spreader/state` at 20 Hz.
- [ ] Forwards target height from `/spreader/cmd` (clamped 0–9 m) to Gazebo.
- [ ] `teleop.py` runs without import errors (`python3 scripts/teleop.py`).
- [ ] `config/sim_params.yaml` has `max_linear_vel` and `max_angular_vel` under `control_node.ros__parameters`.
