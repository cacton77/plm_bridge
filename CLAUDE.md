# CLAUDE.md

Rules for working in this repository. They encode facts that were expensive
to learn; do not "simplify" code that follows them.

## Keep the READMEs current

When you change a package (modules, ROS interfaces, parameters, environment
variables, dependencies, launch arguments, the database schema, the plan
contract), update that package's `README.md`, and `docs/architecture.md` when
the change crosses packages.

## Configuration and secrets

- Config dataclasses expose `to_dict()` returning
  `{field: {value, type, description, control, range}}`, and the ROS node
  declares a parameter for every field (`core.<field>` for `CoreConfig`,
  `<backend>.<field>` for a backend's settings). Adding a field to the
  dataclass and its `to_dict()` must remain sufficient.
- Secret-bearing config (`DXConfig`, and every backend's credential config)
  never has a `to_dict()`, is never a ROS parameter, and is never written into
  a plan, result or log. Use `redacted()` when logging.
- No credentials or tenant identifiers in commits: tenant ids, hostnames
  containing tenant ids, collaborative-space and organization names, personal
  names, PLM object ids and API keys stay in `.env` or in test fixtures with
  obviously fake values. Recorded HTTP fixtures are sanitized when they are
  recorded (`plm_bridge/test/http_replay.py`), not later.

## Architecture rules

- The core (`plm_bridge.core`) imports only `plm_bridge.backends.base`, never
  a concrete backend. Backends are found by name in `backends/registry.py`.
- The core calls a backend method only when the backend declares the
  matching `Capability`, and falls back otherwise.
- Reads that depend on a service a PLM may not expose degrade to an empty
  result and log, rather than raising: a missing service must not fail a
  whole sync. Writes the operator asked for raise `BackendError` with a
  readable message.
- A `part_id` is opaque and never a path component; use the `storage_key`.
- **The plan contract:** the bridge never opens a plan file to learn
  anything about it. The producer states stage, rank, summary, change token
  and generation time (`RecordPlan`) and describes files the bridge finds
  (`DescribePlans`). The only exception is a plan downloaded from a PLM,
  whose `plm_context` block (authored by the bridge) is read back, and
  nothing else.
- **The cell keeps working when the PLM does not.** Everything selection and
  planning need comes from the local catalog and disk, never the network.

## Database and files

- **Plans are never deleted.** Plan files and plan rows, history included,
  survive every migration.
- `catalog.db` migrates in place by numbered, idempotent steps tracked with
  `PRAGMA user_version`, after a backup to `catalog.db.bak-<UTC stamp>`. Add
  a step; never edit a released one.
- Cached paths are environment-relative: the host (`./catalog`) and the
  container (`/catalog`) see the same database at different mount points.
  Resolve through `Catalog.resolved_geometry_path()` / `resolved_thumb_path()`
  / `resolved_plan_path()`; never trust a stored absolute path.

## 3DEXPERIENCE (dx3) client

The REST surface differs between tenants and releases. Before assuming an
endpoint exists, read `docs/backends/dx3.md` (what the tenant actually
exposes, and what it does not). Dassault's public C# SDK
(`3ds-cpe-emed/ws3dx-dotnet`) documents endpoints and mask names; consult it
before concluding a capability is absent.

- **HTTP 200 does not mean a write happened.** Several endpoints accept the
  wrong method or shape, return 200 and do nothing (file check-in via PUT is
  the known case). Judge success on the returned object.
- **An expired session is not a 401.** 3DX answers with the passport login
  page: HTML with status 200. Keep every request on `DXClient._request()` so
  it inherits `_looks_like_login_redirect()` and the re-login-and-retry.
- The FCS job ticket is a named form field on check-in (named by
  `ticketparamname`) but a real query parameter on download. The bookmark
  mask family is `dsbks:BksMask.*`. The search's `totalItems` is the page
  size, so page until a short page. These are all in `docs/backends/dx3.md`.

## Model files and STEP (cad_loader)

- Never call `o3d.io.read_triangle_mesh()` on an operator-selected model. Use
  `cad_loader.mesh_io.read_mesh_file()` and scale by `mesh_file_units()`.
- STEP loader invariants: keep the vertex weld; rebuild `tri_to_brep` and
  `BRepFace.triangle_indices` after the weld; always return metres and
  ignore the caller's units for STEP; keep the OCP 7/8 import fallbacks; take
  B-rep face identity from OCC's shape map. Details in
  `cad_loader/README.md`.

## Live systems

Tests never touch a live PLM. On a live tenant, test runs may read the test
scope and create only objects whose titles start with `TEST_PLM_BRIDGE_`
(set `CATALOG_TITLE_PREFIX`); they never delete anything, and never create
Issues or relate documents to items.
