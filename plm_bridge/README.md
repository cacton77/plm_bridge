# plm_bridge (Python package)

A local parts catalog over one or more PLM systems, for an inspection cell:
it keeps a SQLite index of the parts each backend reports, caches their STEP
files and thumbnails, records every inspection plan the cell produces, and
uploads plans and result bundles back to the PLM. No ROS imports: the ROS
node lives in `plm_bridge_ros`.

The first backend is `dx3` (3DEXPERIENCE). `fake` is an in-memory backend for
tests and development.

## Install

```bash
colcon build --packages-up-to plm_bridge          # in a ROS workspace (with cad_loader)
pip install './plm_bridge[dx3,picker]'             # anywhere
pip install './plm_bridge[dx3,picker,events,thumbnails]'
```

Extras: `dx3` (requests), `events` (stomp.py, for 3DX JMS events),
`picker` (flask), `thumbnails` (numpy, matplotlib, cad_loader). The core
itself is standard library only.

## Layout

```
plm_bridge/
├── core/
│   ├── catalog.py        Catalog: reconciliation, geometry cache, plans, selection, status
│   ├── runs.py           inspection runs and result bundles (record_run: the RecordRun service)
│   ├── schema.py         SQLite schema, versioned migrations (PRAGMA user_version), CatalogDB
│   ├── paths.py          cache layout (storage_key), legacy-path resolution
│   ├── config.py         CoreConfig (to_dict -> ROS parameters)
│   └── plan_contract.py  the PLM context the bridge authors; what it may read from plans
├── backends/
│   ├── base.py           PLMBackend protocol, RemotePart, RemoteRef, Capability, errors
│   ├── registry.py       backends by name
│   ├── fake.py           in-memory backend
│   └── dx3/              3DEXPERIENCE: client.py, config.py, backend.py, jms.py
├── factory.py            build_catalog(): the core plus the configured backends
├── cli.py                the plm-bridge command
├── picker/               browser part picker (Flask), driven by callbacks
├── thumbnails.py         local preview rendering from STEP
└── cad.py                the one import of cad_loader
```

The core imports only `backends.base`. Concrete backends are looked up by
name in `backends.registry`.

## Configuration

Everything comes from the environment (see `.env.example` in
inspection-docker).

| Scope | Variables |
|---|---|
| Core | `PLM_BACKENDS` (default `dx3`), `CATALOG_ROOT`, `CATALOG_SYNC_INTERVAL`, `CATALOG_SYNC_ON_STARTUP`, `CATALOG_MATURITY_FILTER` (falls back to `DX_MATURITY_FILTER`), `CATALOG_AUTO_UPLOAD_PLAN_STAGES` (default `ordered`), `CATALOG_NCR_THRESHOLD`, `CELL_ID`, `CATALOG_RENDER_THUMBNAILS`, `CATALOG_MESH_UNITS`, `CATALOG_TITLE_PREFIX`, `PICKER_PORT`, `CATALOG_NAMESPACE`; `PLAN_DESCRIBE_CMD` for CLI adoption |
| `dx3` credentials | `DX_PASSPORT_URL`, `DX_SPACE_URL`, `DX_TENANT`, `DX_USERNAME`, `DX_PASSWORD`, `DX_SECURITY_CONTEXT` (with its `ctx::` prefix), `DX_JMS_BROKER_URL` |
| `dx3` settings | `DX_BOOKMARK_SCOPE`, `DX_USE_BOOKMARK_SCOPE`, `DX_COLLAB_SPACE`, `CATALOG_PAGE_SIZE`, `CATALOG_MAX_ITEMS`, `CATALOG_FETCH_THUMBNAILS`, `DX_DOCUMENT_LINKS` |

`CoreConfig` and each backend's settings follow the config-dataclass
convention: `to_dict()` returns `{field: {value, type, description, control,
range}}`, and the ROS node declares every field as a parameter
(`core.<field>`, `<backend>.<field>`). Credential configuration
(`DXConfig`) never has a `to_dict()`, is never a parameter, and is never
written into a plan, result or log; log it with `redacted()`.

## Command line

```bash
plm-bridge --full                       # sync every backend
plm-bridge --list | --status | --backends
plm-bridge --sync-item PART_ID          # one part, regardless of scope
plm-bridge --fetch-step PART_ID
plm-bridge --plans PART_ID
plm-bridge --adopt-plans PART_ID        # needs PLAN_DESCRIBE_CMD or --describe-cmd
plm-bridge --record-plan PART_ID FILE --stage ordered [--stage-rank 3]
plm-bridge --upload-plan PLAN_ID
plm-bridge --render-thumbnails [--force]
plm-bridge --contexts | --bookmarks     # dx3 options
```

With more than one backend, part options take `--backend NAME`.

## Concepts

**Identity.** Every part is `(backend, part_id)`. `part_id` is the backend's
own identifier, opaque and never used as a path. The catalog derives
`storage_key = {backend}-{sha1(part_id)[:16]}` for everything on disk.

**Change detection.** Each part has an opaque `change_token` (on 3DX, the
cestamp). When it moves, the part's cached STEP is dropped and every plan
generated against the old token becomes STALE.

**Capabilities.** A backend declares what it can do (`geometry`, `attach`,
`link_attachment`, `issues`, `events`, `thumbnails`, `attributes`). The core
calls a method only when the matching capability is declared, and falls back
otherwise: previews are rendered locally, and plans stay on the cell when a
backend cannot store files.

**The plan contract.** The bridge never opens a plan file to learn anything
about it. When a part is selected it publishes the PLM context it authored
(`plm_context_json`: backend, part_id, part_number, revision, change_token,
container, title, cell_id, generated_by) and the plan directory. The producer
embeds the context as the plan's `plm_context`, adding only stage,
generated_at and software_version. When recording a plan, the producer states
its stage, stage rank, summary, change token and generation time. To adopt
files it never saw written, the bridge lists names and asks the producer to
describe them (`DescribePlans`). The one exception is a plan downloaded from
the PLM, whose `plm_context` block (authored by the bridge) is read back.

**The cell keeps working without the PLM.** Selection and planning read only
the local database and disk.

**Cache layout** (under `CATALOG_ROOT`): `catalog.db`,
`{storage_key}/geometry/{token}.stp`, `{storage_key}/thumbnail.png`,
`plans/{storage_key}/`, `results/{storage_key}/{run_id}/`. The pre-backend
layout (`steps/{id}/{revision}.stp`, `thumbnails/{id}.png`, `plans/{id}/`) is
still resolved, read-only. Paths stored in the database are never trusted
directly, because the host and the container mount the catalog at different
places.

**Migrations.** `catalog.db` is upgraded in place by numbered, idempotent
steps tracked with `PRAGMA user_version`, after a backup to
`catalog.db.bak-<UTC stamp>`. Plans and their history are never deleted.

## Adding a backend

1. Implement `PLMBackend` (`backends/base.py`) in `backends/<name>/`, keeping
   credentials in a config class with no `to_dict()`, and non-secret settings
   in a `settings` dataclass with `to_dict()`.
2. Register it in `backends/registry.py`, with a `from_env()` factory and,
   optionally, CLI hooks (`add_cli_arguments`, `apply_cli_overrides`,
   `handle_cli`).
3. Add it to `test/test_backend_contract.py` (with HTTP recorded through
   `test/http_replay.py`, sanitized at record time) and make it pass.

## Tests

```bash
python3 -m pytest plm_bridge/test
```

These need neither ROS nor a network. `test/test_backend_contract.py` runs
every backend through the same contract. The dx3 case replays HTTP recorded
from a live tenant (`test/fixtures/dx3/contract.json`); re-record it with
`test/fixtures/dx3/record_contract.py`.
