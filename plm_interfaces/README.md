# plm_interfaces

Messages and services between the PLM bridge (`plm_bridge_ros`) and the rest
of the inspection cell. Parts are always named by `backend` + `part_id`; an
empty `backend` in a request means the only hosted backend, or for
`ListParts`/`SyncNow`, all of them.

| Interface | Direction | Purpose |
|---|---|---|
| `msg/PartSelected` | bridge -> cell (latched, `/catalog/part_selected`) | the selected part: geometry path, plan to load and its status, `plan_dir`, `plm_context_json` |
| `msg/SyncResult` | bridge -> cell (`/catalog/sync_complete`) | one sync pass over one backend |
| `msg/PartSummary`, `msg/BackendInfo` | in responses | a catalogued part; a hosted backend |
| `srv/ListBackends`, `srv/ListParts` | cell -> bridge | browse |
| `srv/SelectPart` | cell -> bridge | fetch geometry, resolve the plan, publish `PartSelected` |
| `srv/SyncNow`, `srv/EnsurePlan` | cell -> bridge | sync on demand; plan validity |
| `srv/RecordPlan` | producer -> bridge | record a plan as the producer describes it (the bridge never opens it) |
| `srv/UploadPlan`, `srv/UploadResults` | cell -> bridge | upload a recorded plan (by `plan_id`) or a run's result bundle (by `run_id`) |
| `srv/DescribePlans` (with `msg/PlanDescription`) | bridge -> producer | describe plan files the bridge found on disk |

`plan_status` values: `CURRENT`, `DOWNLOADED`, `UPDATED_FROM_REMOTE`,
`SELECTED` (an operator's explicit choice; load it with a warning),
`STALE` (do not auto-load), `NONE`.

See `docs/architecture.md` for the plan contract these encode.
