# Model Agent Instructions

## Goal
Produce a clean, physically accurate URDF/xacro model of the straddle carrier.
No perception sensors. Assume perfect localisation — the model only needs
geometry, inertia, collision, and Gazebo drive/joint plugins.

## Read First
`agents/interfaces.md` — all dimensions, joint names, and plugin names are fixed there.

## Scope — files you own
- `description/urdf/straddle_carrier.urdf.xacro` (rewrite from scratch if needed)

## Off-limits — do not touch
- `worlds/`, `src/`, `include/`, `scripts/`, `launch/`, `config/`

---

## What to build

### 1. Links
| Link                   | Geometry                                     | Notes                              |
|------------------------|----------------------------------------------|------------------------------------|
| `base_footprint`       | none (virtual)                               | origin on ground, vehicle centre   |
| `base_link`            | portal frame: two legs + top beam (3 boxes)  | use xacro properties from contract |
| `front_left_wheel_link`  | cylinder r=0.75 l=0.55                     |                                    |
| `front_right_wheel_link` | cylinder r=0.75 l=0.55                     |                                    |
| `rear_left_wheel_link`   | cylinder r=0.75 l=0.55                     |                                    |
| `rear_right_wheel_link`  | cylinder r=0.75 l=0.55                     |                                    |
| `spreader_link`        | flat box 12.192 × 2.438 × 0.3               |                                    |

### 2. Joints
Use **exactly** the names from `interfaces.md §4`.
- Wheels: `continuous`, axis Y, positioned at the four corners.
- Spreader: `prismatic`, axis Z, range 0 – 9.0 m, effort 500 000 N, velocity 0.2 m/s.

### 3. Inertia
Use realistic inertia (not zero). Suggested masses:
- Portal frame (`base_link`): 38 000 kg
- Each wheel: 600 kg
- Spreader: 3 000 kg

### 4. Gazebo plugins (inside `<gazebo>` tags)
Wire up the four plugins from `interfaces.md §8`:
- `DiffDrive`: left joints = [front_left, rear_left], right = [front_right, rear_right],
  wheel_separation = 9.5 m (outer track), wheel_radius = 0.75 m, topic = `/cmd_vel`,
  odom_topic = `/odom`, frame_id = `odom`, child_frame_id = `base_footprint`.
- `JointPositionController`: joint = `spreader_joint`, topic = `/spreader/cmd`.
- `JointStatePublisher`: topic = `/joint_states`.
- `OdometryPublisher`: (only if DiffDrive does not already publish odom — check).

### 5. Visual appearance
- Portal frame: yellow (RGBA 0.95 0.80 0.0 1)
- Wheels: dark grey (0.2 0.2 0.2 1)
- Spreader: light grey (0.7 0.7 0.7 1)

---

## Done Criteria
- [ ] `xacro description/urdf/straddle_carrier.urdf.xacro` produces valid XML (no errors).
- [ ] All joint names match `interfaces.md §4` exactly.
- [ ] `spreader_joint` limits are 0 – 9.0 m.
- [ ] DiffDrive plugin wired to `/cmd_vel` and publishes `/odom`.
- [ ] JointPositionController wired to `/spreader/cmd`.
- [ ] No sensor links, no camera, no LiDAR.
