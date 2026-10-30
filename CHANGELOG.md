# Changelog

## 0.1.0 (unreleased, 2026-10-30)

The parts catalog that lived in ViewpointGeneration (`viewpoint_generation.catalog`,
`viewpoint_generation.picker`, `step_loader`) extracted into its own
repository and generalized over PLM backends.

### Added

- `cad_loader`: the STEP loader and model-file reading, with no ROS imports
  and pip-installable.
- `plm_interfaces`: the catalog's messages and services, with new
  `ListBackends`/`BackendInfo` and `DescribePlans`/`PlanDescription`.
- `plm_bridge`: the backend protocol (`PLMBackend`, `RemotePart`,
  `RemoteRef`, `Capability`), a registry, an in-memory `fake` backend, and
  the `dx3` (3DEXPERIENCE) backend; the `plm-bridge` CLI; a backend contract
  test suite with sanitized HTTP replay.
- `plm_bridge_ros`: the `plm_bridge` node and `plm_bridge.launch.py`.
- `RecordRun`: the node that finishes an inspection can record the run and
  its result bundle, and upload it, in one call. This exposes the
  inspection-run functions, which nothing in the cell could reach before.
- The plan contract: the bridge never opens plan files. The producer embeds
  the bridge's `plm_context` and describes its plans (`RecordPlan` fields,
  `DescribePlans`).
- Versioned database migrations (`PRAGMA user_version`) with an automatic
  backup.
- `CATALOG_TITLE_PREFIX` for test runs; `DX_DOCUMENT_LINKS` to opt in to
  relating Documents to items.

### Changed (for the inspection cell)

- **Identity.** Parts are `(backend, part_id)` with an opaque
  `change_token`. Interfaces renamed accordingly:
  - `eng_item_id` becomes `backend` + `part_id`;
  - `cestamp` becomes `change_token`;
  - `collab_space` becomes `container`;
  - `step_file_path`/`step_path` become `geometry_path`;
  - `step_cached`/`step_available` become `geometry_cached`/`geometry_available`;
  - `plan_doc_id`/`result_doc_id` become `remote_ref`.
- **Services and topics.** `UploadPlan` takes a recorded `plan_id`.
  `SyncNow` returns one `SyncResult` per backend. Services and topics keep
  their `catalog` namespace, and the node is named `plm_bridge`.
- **Plan files** are schema 3.0 (`plm_context` with `backend`, `part_id`,
  `change_token`). ViewpointGeneration still reads 2.0, 1.0 and bare results.
- **Parameters.** dx3 settings moved from `catalog.<field>` to
  `dx3.<field>`. The picker runs in the node (`catalog.picker_enabled`), and
  the separate `picker_node` is gone.
- **Database.** `catalog.db` migrates in place (steps 1 and 2) after a
  backup. Cached files are not moved, and the old layout is still read.
- **Adoption.** An adopted plan keeps its own change token; previously it
  took the part's current one.
- **Item linking.** Relating uploaded Documents to their item is off by
  default (`DX_DOCUMENT_LINKS`); the route 404s on the UW tenant.
- **Listings.** The catalog listing no longer hides parts outside
  `DX_COLLAB_SPACE` (the bookmark is the scope).
