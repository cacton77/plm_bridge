# Architecture

plm_bridge connects an inspection cell to product lifecycle management (PLM)
systems. It keeps a local catalog of parts, caches what inspection needs, and
records and uploads the plans and results the cell produces. It started as
the `catalog/` package inside ViewpointGeneration and was extracted
(2026-10-30) so the cell's planner depends only on two small packages:
`plm_interfaces` and `cad_loader`.

## Packages

| Package | Build | Role | ROS? |
|---|---|---|---|
| `cad_loader` | ament_python, pip | STEP (with B-rep topology) and mesh loading | no |
| `plm_interfaces` | ament_cmake | messages and services | yes |
| `plm_bridge` | ament_python, pip | core, backends, picker, CLI | no |
| `plm_bridge_ros` | ament_python | the `plm_bridge` node and its launch file | yes |

```
            ViewpointGeneration (plan producer)
              │  PartSelected ◄──────────┐
              │  RecordPlan ────────────►│
              │  DescribePlans ◄─────────┤   plm_interfaces
              ▼                          │
          cad_loader          plm_bridge_ros (node: services, topics, picker thread)
                                         │
                                    plm_bridge.core ── backends.base (protocol)
                                         │                  ▲
                                   CatalogDB, cache    backends.registry
                                                            │
                                                       backends.dx3 ── 3DEXPERIENCE
                                                       backends.fake (tests)
```

## Who owns what

**The core** (`plm_bridge.core`) owns the SQLite catalog, the reconciliation
loop (new, modified, unchanged, archived), cache invalidation when a change
token moves, plan records and their staleness, inspection runs and result
bundles, the upload and issue policies, path resolution, the fallback
thumbnail renderer, the picker and the CLI. It imports only
`backends.base`.

**Each backend** owns authentication, enumerating a scope, fetching a part,
exporting STEP, reading attributes, attaching files, finding attachments,
raising issues, change events, and its own CLI options.

**The producer** (ViewpointGeneration) owns the plan format. The bridge
never reads it.

## The backend protocol

`backends/base.py` defines `PLMBackend`, `RemotePart`, `RemoteRef`,
`Capability`, `ScopeTruncated`, `BackendError` and `BackendAuthError`.

Each backend sets `name`, `capabilities` and `scope`, and implements:

- `is_configured()`, `connect()`
- `list_scope(scope)`, `list_recent(scope)`, `get_part(part_id)`
- `check_geometry(part)`, `fetch_geometry(part, dest_dir)`,
  `fetch_thumbnail(part, dest_dir)`, `read_attributes(part)`
- `attach_file(part, path, kind, title)`, `list_attachments(part, kind)`,
  `fetch_attachment(ref, dest_dir)`
- `raise_issue(part, title, body)`, `subscribe(on_change)`
- `describe()`, `close()`

Rules:

- The core calls a method only when the matching capability is declared,
  and otherwise falls back.
- Reads of services a PLM may not expose degrade to None or empty and log.
- Writes the operator asked for raise `BackendError`, so the reason reaches
  the operator.
- `part_id` is opaque and never a path. The core derives
  `storage_key = {backend}-{sha1(part_id)[:16]}`.
- `change_token` is compared for equality only.
- `list_scope()` raises `ScopeTruncated` after yielding what it could when it
  stopped at a budget. The core then archives nothing.

## The plan contract

The bridge never opens a plan file to learn anything about it.

1. **Selection.** `PartSelected` carries the geometry path, the plan to load
   (with its status), `plan_dir` (where new plans for the part go), and
   `plm_context_json`. That is the PLM context the bridge authored:
   `backend`, `part_id`, `part_number`, `revision`, `change_token`,
   `container`, `title`, `cell_id`, `generated_by`.
2. **Writing.** The producer embeds that object as the plan's `plm_context`
   and adds only `stage`, `generated_at` and `software_version`. Plan schema
   is `3.0`.
3. **Recording.** `RecordPlan` states `stage` (required), `stage_rank`
   (higher means further through the pipeline), `summary_json` (stored
   verbatim), `summary_text` (one line for the picker), the `change_token`
   the plan was generated against, and `generated_at`.
4. **Adoption.** For plan files the bridge finds on disk but never saw
   recorded, it lists names and asks the producer's `DescribePlans` service
   to describe them. From the command line, it runs the producer's describe
   command (`PLAN_DESCRIBE_CMD`).
5. **The one exception.** A plan *downloaded* from a PLM (backends with
   `link_attachment`) has no producer to ask. Its token, stage and time are
   read back from the `plm_context` block the bridge authored, and nothing
   else.

The current plan is the most recently recorded one. After adoption it is
the one with the largest `(generated_at, stage_rank)`. A plan whose
`change_token` differs from the part's is STALE and is not auto-loaded. A
plan the operator picks explicitly is SELECTED and loads with a warning.
`auto_upload_plan_stages` (default `ordered`) decides which recorded stages
upload.

## ROS interface (`plm_interfaces`)

The node is named `plm_bridge`. Its services and topics live under
`core.namespace` (default `catalog`), so the names the cell has always
used are unchanged:

- **Services:** `<ns>/list_backends`, `list_parts`, `select_part`,
  `sync_now`, `ensure_plan`, `record_plan`, `upload_plan` (by `plan_id`),
  `upload_results` (by `run_id`), and `record_run`, which records a finished
  inspection run and its bundle (optionally uploading it) in one call.
- **Topics:** `/<ns>/part_selected` (latched) and `/<ns>/sync_complete`
  (one message per backend per pass).
- **Client:** `core.describe_plans_service` (the producer's
  `DescribePlans`).

## Data

The catalog lives under `CATALOG_ROOT`: `catalog.db`,
`{storage_key}/geometry/{token}.stp`, `{storage_key}/thumbnail.png`,
`plans/{storage_key}/`, `results/{storage_key}/{run_id}/`.

The database has four tables:
- `parts`, keyed by `(backend, part_id)`;
- `plans`, which keeps history: every recorded plan has a row;
- `inspection_runs`;
- `sync_log`.

## Migration notes

The database is migrated in place by numbered steps (`PRAGMA user_version`),
each idempotent, after a backup to `catalog.db.bak-<UTC stamp>`:

- **Version 0.** Column additions from the pre-versioning releases.
- **Step 1, the plan contract.** The planner-specific columns (`num_regions`,
  `num_clusters`, `num_viewpoints`, `seg_algorithm`, `traversal_algo`) move
  into `summary_json`. `summary_text` is regenerated, and `stage_rank` is
  derived from the stage label.
- **Step 2, backend identity.** Every table is rebuilt keyed by
  `(backend, part_id)`. Existing rows become `dx3` rows: `cestamp` becomes
  `change_token`, `collab_space` becomes `container`, `plan_doc_id` and
  `result_doc_id` become `remote_ref`, and `type` moves into `extra_json`.
  Every part, plan (with history), run and sync-log row is carried over.

No cached file is moved and nothing is re-downloaded. The resolver still
finds the pre-backend layout, read-only: `steps/{id}/{revision}.stp`,
`thumbnails/{id}.png`, `plans/{id}/`. A copy of the cell's real database
migrated (2026-10-30) with every part, plan row, plan history entry and
sync-log entry intact.

Plan files: ViewpointGeneration still reads schema 2.0 (mapping
`eng_item_id` to `part_id`, `cestamp` to `change_token`, and adding
`backend: dx3`), the 1.0 `{plm_context, plan}` envelope, and bare results
JSON.
