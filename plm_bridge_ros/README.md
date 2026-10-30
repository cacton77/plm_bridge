# plm_bridge_ros

The `plm_bridge` ROS 2 node: it hosts the configured PLM backends, serves the
catalog services and topics, runs syncs on a background thread (on a timer,
on demand, or driven by backend events), and serves the browser part picker
from the same process.

```bash
ros2 launch plm_bridge_ros plm_bridge.launch.py
ros2 launch plm_bridge_ros plm_bridge.launch.py plm_backends:=dx3 picker_port:=5050 \
    describe_plans_service:=viewpoint_generation/describe_plans
```

| Launch argument | Parameter | Default |
|---|---|---|
| `plm_backends` | `catalog.backends` | `$PLM_BACKENDS`, else `dx3` |
| `sync_interval` | `catalog.sync_interval` | `300` (0 disables the timer) |
| `sync_on_startup` | `catalog.sync_on_startup` | `true` |
| `mesh_units` | `catalog.mesh_units` | `mm` |
| `picker` | `catalog.picker_enabled` | `true` |
| `picker_port` | `catalog.picker_port` | `5050` |
| `describe_plans_service` | `catalog.describe_plans_service` | empty (no producer) |
| `namespace` | `catalog.namespace` | `catalog` |

Every `CoreConfig` field is a `catalog.<field>` parameter, and every field of
a backend's settings is `<backend>.<field>` (e.g. `dx3.bookmark_scope`).
Credentials are never parameters; they come from the environment.

Services and topics: `<ns>/{list_backends, list_parts, select_part, sync_now,
ensure_plan, record_plan, upload_plan, upload_results}`, `/<ns>/part_selected`
(latched) and `/<ns>/sync_complete`. See `plm_interfaces`.

The picker is reachable at `http://<host>:<picker_port>` (the cell's
containers use host networking). It labels each part with its backend and
hides actions a backend cannot do.
