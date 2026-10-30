# plm_bridge

Connects a ROS 2 inspection cell to product lifecycle management (PLM)
systems. It provides:
- a local catalog of parts, synced from one or more PLM backends;
- STEP and thumbnail caching;
- a browser part picker;
- recording and upload of inspection plans and results.

The first backend is 3DEXPERIENCE (`dx3`).

| Package | What it is |
|---|---|
| [`cad_loader/`](cad_loader/) | STEP (with B-rep topology) and mesh loading. No ROS; pip-installable. |
| [`plm_interfaces/`](plm_interfaces/) | ROS 2 messages and services (part selection, catalog, plan recording, uploads). |
| [`plm_bridge/`](plm_bridge/) | The catalog core, the backends, the picker and the `plm-bridge` CLI. No ROS; pip-installable. |
| [`plm_bridge_ros/`](plm_bridge_ros/) | The `plm_bridge` node and `plm_bridge.launch.py`. |

Read [`docs/architecture.md`](docs/architecture.md) first. It covers who owns
what, the backend protocol, the plan contract, and the migration notes.
Backend notes are in [`docs/backends/`](docs/backends/), and the rules for
changing code are in [`CLAUDE.md`](CLAUDE.md).

## In the inspection cell

The repository is cloned into the cell's colcon workspace next to
ViewpointGeneration, which depends on `plm_interfaces` and `cad_loader`:

```bash
cd ros2_ws/src
git clone https://github.com/cacton77/plm_bridge.git     # private
cd .. && colcon build
ros2 launch viewpoint_generation bringup.launch.py catalog:=true picker:=true
# or the bridge alone:
ros2 launch plm_bridge_ros plm_bridge.launch.py
```

Configuration comes from the environment. For 3DX that is the `DX_*`
variables in inspection-docker's `.env`; `PLM_BACKENDS` picks the backends,
default `dx3`. See [`plm_bridge/README.md`](plm_bridge/README.md).

## Without ROS

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install './cad_loader[step]' './plm_bridge[dx3,picker,thumbnails,test]'
plm-bridge --status
python -m pytest cad_loader/test plm_bridge/test
```

## Status

Private, unreleased; the license is not chosen yet (see `LICENSE`). Work
history and verification results are in [`REPORT.md`](REPORT.md); open
questions are in [`QUESTIONS.md`](QUESTIONS.md).
