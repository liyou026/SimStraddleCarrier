# World Agent Instructions

## Goal
Create the simplest usable Gazebo Harmonic world: flat concrete ground + one 40ft
ISO container placed so the straddle carrier can drive over it and pick it up.

## Read First
`agents/interfaces.md` — container dimensions are fixed there (§3).

## Scope — files you own
- `worlds/port_yard.sdf` (rewrite from scratch)

## Off-limits — do not touch
- `description/`, `src/`, `include/`, `scripts/`, `launch/`, `config/`

---

## What to build

### 1. Required Gazebo plugins (world level)
```xml
gz-sim-physics-system
gz-sim-user-commands-system
gz-sim-scene-broadcaster-system
gz-sim-contact-system
```

### 2. Lighting
One directional sun light. No fog, no sky complexity.

### 3. Ground plane
- Flat plane, 200 × 200 m.
- Material: grey concrete (ambient 0.55 0.55 0.55 1).
- Static = true, friction mu1 = mu2 = 0.8.

### 4. Container
- One 40ft ISO container: 12.192 × 2.438 × 2.591 m.
- Placed at position (20, 0) — 20 m ahead of vehicle spawn, centred on Y.
- Container bottom sits on ground (z = 2.591 / 2 = 1.2955 m).
- Static = true (the control agent handles pick logic separately).
- Visual colour: red (0.8 0.15 0.15 1).
- Named `container_A1`.

### 5. Physics
```xml
<max_step_size>0.001</max_step_size>
<real_time_factor>1.0</real_time_factor>
```

### 6. Vehicle spawn point
The world does not spawn the robot — that is done by the launch file.
Just ensure the origin (0, 0) is clear so the carrier can be placed there.

---

## Done Criteria
- [ ] `worlds/port_yard.sdf` is valid SDF 1.10 (no XML errors).
- [ ] World loads in `gz sim worlds/port_yard.sdf` without warnings.
- [ ] Exactly one container named `container_A1` at (20, 0, 1.2955).
- [ ] Container dimensions match `interfaces.md §3` exactly.
- [ ] Ground plane is static and covers at least 200 × 200 m.
- [ ] No robots, no sensors, no extra models beyond ground + container.
