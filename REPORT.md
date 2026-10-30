# plm_bridge extraction: report

**Status: finished** (2026-10-30), with Phase 3 deferred at Colin's request.
Everything is pushed to GitHub. The repository is public under BSD-3-Clause.
Nothing secret was pushed (see the "Secrets" section at the end).
[`QUESTIONS.md`](QUESTIONS.md) records Colin's answers to the open questions
and what was done with each.

How to read the verification claims:
- **Verified live:** the behaviour was observed against the UW 3DEXPERIENCE
  tenant on 2026-10-30.
- **Verified offline:** covered by tests, or by replaying HTTP recorded from
  that tenant, but not exercised live.

## 1. Summary

Before any work, Colin narrowed the scope: get the 3DX integration into the
new package; no Onshape backend and no Onshape references in the new
packages for now. Phase 3 (Onshape and local backends) was therefore not done.
Phases 0, 1, 2, 4 and 5 and both stretch items were.

| Phase | What was done | Commits |
|---|---|---|
| 0. Baseline | 44 characterization tests (`plan_io`, reconciliation, paging, scoping, plan history and upload policy, result upload and NCR threshold, DB migration, the STEP loader on an OpenCascade-generated box). Live smoke S1–S6 on the baseline code. | VG `b4a950d` |
| 1. Cut couplings in place | Plan contract (`plan_contract.py`): the catalog stopped opening plan files and importing `plan_io`. `PartSelected` gained `plan_dir` and `plm_context_json`. `RecordPlan` carries the producer's stage, rank, summary, token and time. Versioned migrations with backup. Adoption goes through a new `DescribePlans` service on the VG node. The picker moved into the catalog node with callbacks. One loader shim. | VG `88445ad` |
| 2. Backend abstraction | `PLMBackend` protocol, registry, fake backend. dx3 backend (`DXClient` moved). Core rewritten against the protocol and imports only `backends.base`. Identity `(backend, part_id)` with opaque `change_token`. `storage_key` cache layout with legacy resolution. Migration step 2. Interfaces in the Section 4.6 shapes. Plan schema 3.0. Capability fallbacks. Contract tests over the fake and over dx3 replaying sanitized recorded HTTP. | VG `52ae8b6` |
| 3. Local and Onshape backends | **Deferred** (Colin, 2026-10-30) | none |
| 4. Extract | Four packages in this repository with fresh history. ViewpointGeneration depends only on `plm_interfaces` and `cad_loader`. inspection-docker wired in. 3DX docs moved here, scrubbed. Clean `colcon build`. Tests pass, including in a plain Python 3.12 virtualenv with no ROS. Live smoke S1–S6 on the extracted packages. | plm_bridge `fbdd07b`, VG `b23e871`, inspection-docker `2f4efa8` |
| 5. Docs and release prep | READMEs per package, `docs/architecture.md`, `CHANGELOG.md`, `CLAUDE.md`, scrub. Then, after Colin's answers: BSD-3-Clause license (Copyright (c) 2026, Colin Acton) and public visibility. | plm_bridge `fbdd07b`, `c1a2d64`, and the commits below |
| Stretch | `RecordRun` service. Read-only investigation of 3DX attributes and Document links. Live result upload on a synthetic run. | plm_bridge `12e99ea`, `51f05d1` |
| Merge | `plm-bridge` merged into `main` in ViewpointGeneration and inspection-docker | VG `3ffc150`, inspection-docker `10bab66` |
| Colin's answers | VG re-selection fixed. Document-to-item write routes tested live (none works). inspection-docker moved onto Colin's reorganised layout, with a `.gitignore` fix. Parameters renamed `core.*`. All test Documents deleted. BSD-3-Clause; repository public. Final live smoke S1–S6 pass. | VG `afc94f9`; inspection-docker `b46ae16`/`d59ba93`; plm_bridge `0aaecba`, `6ff3ae4`, and the final commits |

Tests at the end:

| Where | Package | Result |
|---|---|---|
| Container (colcon) | `plm_bridge` | 74 passed, 1 skipped (dx3 Issue creation is deliberately not recorded) |
| Container (colcon) | `cad_loader` | 3 passed |
| Container (colcon) | `plm_bridge_ros` | 1 passed |
| Container (colcon) | ViewpointGeneration | 16 passed |
| Plain Python 3.12 virtualenv, no ROS, PyPI dependencies (numpy 2.5, open3d 0.20, cadquery-ocp 8.0.1) | `cad_loader` + `plm_bridge` | 74 passed, 1 skipped (before the `RecordRun` tests were added) |

ViewpointGeneration's ament `flake8` and `pep257` tests already failed before
this work (about 1,800 and 1,100 findings) and were deselected throughout.

## 2. Names and locations

| Thing | Value |
|---|---|
| Repository | <https://github.com/cacton77/plm_bridge> (created private with `gh`, Option A; made public on 2026-10-30 at Colin's request), branch `main` |
| Packages | `cad_loader`, `plm_interfaces`, `plm_bridge`, `plm_bridge_ros` (node `plm_bridge`, executable `plm_bridge_node`, launch `plm_bridge.launch.py`, CLI `plm-bridge`) |
| ViewpointGeneration | branch `plm-bridge` (from `feature-3dx-integration` @ `53c0ba1`); Phase 4 commit `b23e871`, plus status-file commits |
| inspection-docker | branch `plm-bridge` (from `feature-3dx-integration` @ `68bfdbd`). `2f4efa8` (Phase 4 on the old layout); `b46ae16` (Colin's reorganisation, copied from his working tree); `d59ba93` (plm_bridge on the new layout, `.gitignore` fix) |
| Local clone of the new repository | `inspection-docker/ros2_ws/src/plm_bridge` (`ros2_ws/src` exists on this machine) |
| Git worktrees | ViewpointGeneration `plm-bridge`: `/home/macs/plm_bridge_work/ws/src/ViewpointGeneration`; inspection-docker `plm-bridge`: `/home/macs/plm_bridge_work/inspection-docker` |
| Test workspace | `/home/macs/plm_bridge_work/ws`, built in throwaway `inspection-docker:jazzy` containers. It never mounted Colin's `ros2_ws` or his real `catalog/`; smoke runs used copies of the real catalog. |
| Status file | `PLM_BRIDGE_STATUS.md` on ViewpointGeneration's `plm-bridge` branch |
| Onshape connector snapshot | Untracked files in inspection-docker `docs/onshape_integration/` (branch `feature-3dx-integration` @ `68bfdbd`). sha256: `ONSHAPE_API_FINDINGS.md` `c15ef112…6b1ce8`; `onshape_catalog_integration_plan.md` `f6b1822c…bdf299`; `onshape_rest_api_tour.ipynb` `df9d7d16…29d1`. Unchanged at the end. **Not ported** (scope change); used read-only to keep the protocol generic. |

Repositories that had uncommitted work and were left untouched:
- inspection-docker on `feature-3dx-integration`: 32 entries, including a
  reorganisation that moves `src/` to `ros2_ws/src/` and
  `docker-compose.yaml` to `docker/`.
- ViewpointGeneration on `main`: Zivid and dual-arm edits to `README.md`,
  `bringup.launch.py` and `package.xml`.
- Inspection_Cell (15 entries) and Inspection_Control (5 entries).

Nothing was stashed, reset, committed or checked out over in any of them. Two
side effects: the new repository sits inside inspection-docker's untracked
`ros2_ws/`, which Colin's own pending `.gitignore` ignores; and the worktrees
added refs under each repository's `.git`.

## 3. Deviations from the plan

1. **Scope.** There is no Onshape backend, no local backend, and no Onshape
   names in the packages (Colin, 2026-10-30). No Onshape API calls were made
   (0 of the 150 allowed). Onshape appears only in this report.
2. **Protocol, compared with the Section 4.3 sketch (same shape, more
   explicit):**
   - Additions to the data types:
     - `RemotePart.geometry_available` may be `None` ("ask
       `check_geometry()`"). Listing every 3DX part's derived outputs on
       every sync would cost a call per part; the old code only checked new
       or modified parts.
     - `RemotePart.description` was added.
     - `RemoteRef` gained `title`, `modified` and `note`.
   - Methods added to the protocol: `scope`, `is_configured()`,
     `list_recent()` (incremental), `check_geometry()`, `fetch_attachment()`
     (needed to download remote plans), `describe()` and `close()`.
   - `list_scope()` raises `ScopeTruncated` at the end when it stopped at a
     budget, so the core knows not to archive.
   - Writes the operator asked for (`attach_file`, `raise_issue`) raise
     `BackendError` with the reason rather than returning `None`, so the
     reason reaches the picker. Reads still degrade to `None` or empty.
3. **The plan contract.**
   - The bridge's `plm_context` also carries `title`.
   - The one place the bridge reads a plan file is a plan **downloaded** from
     a PLM, which has no producer to ask. There it reads only the
     `plm_context` block it authored. This happens only for backends declaring
     `link_attachment`, so never on the UW tenant.
   - Adoption was built as both options the plan offered: the
     `DescribePlans` service (used by the picker) and a producer CLI
     (`python3 -m viewpoint_generation.plan_io describe`, used by
     `plm-bridge --adopt-plans` via `PLAN_DESCRIBE_CMD`).
4. **Behaviour changes, deliberate:**
   - An adopted plan keeps its own change token. Previously every adopted
     file took the part's current cestamp and showed as CURRENT.
   - Relating uploaded Documents to their item is opt-in (`DX_DOCUMENT_LINKS`,
     default off). It always 404s on this tenant, and as a write to a real
     item it falls outside what test runs may do.
   - `list_parts` no longer hides parts outside `DX_COLLAB_SPACE` (the
     bookmark is the scope).
5. **Names.**
   - The node is `plm_bridge`, while services and topics keep the `catalog`
     namespace.
   - Core parameters keep the `catalog.<field>` prefix. dx3 settings moved to
     `dx3.<field>`; they used to be `catalog.<field>`, and no launch file set
     them.
   - The `plm_bridge` packages name no producer. The `DescribePlans` service
     name and the describe command are configuration, and ViewpointGeneration's
     bringup and docker-compose supply them.
6. **Cache files are not moved.** The resolver finds the legacy layout
   read-only. New files go to `{storage_key}/…`, and the legacy
   `steps/{id}/{revision}.stp` hand-placed location still works.
7. **CLI.** Backend options are registered as flags (`--contexts`,
   `--bookmarks`, `--collab-space`), not subcommands, to keep the commands
   operators know.
8. **`mesh_utils`** in ViewpointGeneration re-exports
   `cad_loader.mesh_io.read_mesh_file`/`mesh_file_units`, so its callers
   are unchanged.
9. **inspection-docker.** Phase 4 edited the committed layout. Afterwards,
   at Colin's request, his uncommitted reorganisation was copied into the
   `plm-bridge` branch as its own commit and the edits redone on top
   (`ros2_ws/src/shared.repos`, `docker/docker-compose.yaml`). The copy
   leaves out three things:
   - his untracked `docs/onshape_integration/`;
   - two runtime files;
   - the `.env.example` tenant values, kept as placeholders.

   His two path edits to the 3DX docs were applied to the copies here.
   `ONSHAPE_*` and `LOCAL_PARTS_DIR` were not added (scope).
10. **Smoke harness limits** (`/home/macs/plm_bridge_work/tools/smoke.py`):
    - Without the cell there is no MoveIt, so `ordered` plans come from a stub
      traversal service that writes through VG's own `plan_io.write_plan` with
      a trivial order. The VG node's real recording path still runs.
    - Segmentation uses `brep`, because PartField needs the GPU model.
    - A `sitecustomize` guard forced every created Document title to start
      with `TEST_PLM_BRIDGE_` and stubbed item-linking and Issue creation.
      From Phase 2 on, `CATALOG_TITLE_PREFIX` did the same in the code.

## 4. Capability matrix

| Capability | `dx3` | `onshape` | `local` |
|---|---|---|---|
| Sign-on (CAS, CSRF, SecurityContext) | verified live 2026-10-30 | not implemented (deferred) | not implemented |
| Scope listing (bookmark) | verified live 2026-10-30 (6 parts) | not implemented | not implemented |
| Scope listing (search, `[ds6w:project]`, fallback, paging) | verified offline only this time (verified live in Aug per the findings) | not implemented | not implemented |
| Change detection | unchanged parts verified live 2026-10-30; modification path verified offline only (no live CAD edit was made) | not implemented | not implemented |
| Geometry (STEP via derived outputs) | verified live 2026-10-30 | not implemented | not implemented |
| Attributes (material, finish) | not available on this system (probed 2026-10-30) | not implemented | not implemented |
| Thumbnails (per-object preview) | not available on this system; local rendering from STEP verified live | not implemented | not implemented |
| Attach plan (Document + FCS) | verified live 2026-10-30 (5 uploads, plus a download round trip) | not implemented | not implemented |
| Link plan to part | not available on this system (write routes tested live 2026-10-30: 405 and 500; see section 6) | not implemented | not implemented |
| Result upload | verified live 2026-10-30 (synthetic run, 2 files on one Document) | not implemented | not implemented |
| Issues (`dsiss:Issue`) | implemented, untested live (offline only; creating Issues is outside what test runs may do) | not implemented | not implemented |
| Events (JMS via EIF) | implemented, untested (no broker) | not implemented | not implemented |

The in-memory `fake` backend implements every capability and is used by the
tests only.

## 5. Smoke checklist results (dx3, live)

Run on 2026-10-30, each time on a fresh copy of the cell's real `catalog.db`.

| Check | Phase 0 (baseline) | Phase 1 | Phase 2 | Phase 4 (extracted) | Final |
|---|---|---|---|---|---|
| S1 full sync, then all unchanged | pass | pass | pass | pass | pass |
| S2 picker lists parts with local thumbnails | pass | pass | pass | pass | pass |
| S3 STEP downloaded and loaded with B-rep faces | pass | pass | pass (new layout) | pass | pass |
| S4 one row per stage; `ordered` auto-uploads as `TEST_PLM_BRIDGE_` | pass | pass | pass | pass | pass |
| S5 re-select loads CURRENT; a different token gives STALE and no load | pass* | pass* | pass* | pass* | pass |
| S6 network disconnected: cached part plans and records locally | pass | pass | pass | pass | pass |
| X1 picker "Scan for files" adopts through the producer | n/a | pass | pass | pass | pass |
| X2 `list_backends` reports dx3 and its capabilities | n/a | n/a | pass | pass | pass |

\* Through Phase 4, S5 was judged without VG's "earlier CAD revision"
warning, which a pre-existing VG quirk suppressed on re-selection. The quirk
is fixed (VG `afc94f9`). The final run applies the strict check: no "Failed
to load selected model" on re-selection, and the STALE warning is logged.

## 6. Answers

1. **Is there now a working route on 3DX to relate an uploaded Document to
   its engineering item? No.** Tested live on 2026-10-30, with Colin's
   approval, against the "Test" part:
   - `POST documents/parentId/{engItemId}` answers `405 Method Not Allowed`.
   - `POST documents?parentId=…&parentRelName=…&parentDirection=from` answers
     `500 "An unexpected error has occurred"` for `Reference Document`,
     `SpecificationDocument` and `PLMDocConnection`. Listing and search both
     confirm nothing was created.
   - `GET documents/parentId/{id}` exists and validates its parent, but it
     only reads.
   - The older routes (`dseng:…/dseng:SpecificationDocument`,
     `documents/{id}/relateddata`) still 404.

   Untried: the derived-output workaround (not approved). Also untried:
   finding plans by title through `documents/search`, which works and needs
   no relationship (QUESTIONS.md).
2. **Can engineering attributes (material, finish, specification) be read on
   the UW tenant? No, not for the parts in scope.**
   - `dsmveng:EngItemMask.Details` works but returns no
     `dseno:EnterpriseAttributes`, and `dseng:EnterpriseReference` is empty.
   - `dsxcad:Part/{id}/dsxcad:xCADAttributes` (a route from Dassault's SDK)
     holds only `cadorigin: SOLIDWORKS` on all six parts.
   - Dassault's SDK has no materials service.
   - Making material readable would be a modelling change (enterprise
     attributes, or SolidWorks properties mapped on save), not client work.
     Evidence: `tools/dx3_probe_attributes.py`.
3. **Were result upload and Issue creation exercised?**
   - Result upload: yes, **live** on dx3 with a synthetic run through the new
     `RecordRun` path. One Document held the manifest and an image (section
     8). Also offline, through the fake client and the fake backend.
   - Issue creation: **offline only**, through the fake client and the fake
     backend, including the threshold. Live creation is outside what test
     runs may do.
4. **On Onshape, where do uploaded plans live, and can they be found from
   the part? Not implemented here** (deferred).
   - Colin's design and decision: plans go as blob elements ("tabs") in the
     part's own document.
   - His spike (`ONSHAPE_API_FINDINGS.md`, 2026-10-16) lists blob upload,
     finding it again, and download as **still open**.
   - So this is unverified.
5. **How does the Onshape backend detect change, and how often does it mark
   plans stale? Not implemented, and so not measured.** Colin's spike
   found:
   - A part's `microversionId` is document-wide, so it is useless per part.
   - The element microversion is a good prefilter only.
   - The per-part stamp that works is a mass-properties fingerprint (volume,
     centroid, inertia), one call per Part Studio. In V1→V2→V3 it flagged
     exactly the one part that changed.
   - It would miss geometry edits that preserve all three.
   - The protocol's opaque `change_token` and hashed `storage_key` (Onshape
     part ids contain `/`) were designed so that this fits without changes.

## 7. API findings (also in `docs/backends/dx3.md`)

- **Bookmark scope:** 6 members, all engineering items; a full sync takes
  1.5–4 s.
- **Derived outputs:** 2 of the 6 parts publish a STEP. `Locate` answers the
  rest with `500 "Error in Get Derived Output Info"`.
- **Document round trip:** create, check-in ticket (PUT), FCS upload,
  completion (POST), download ticket (PUT) and checkout all work. The bytes
  came back intact.
- **CSRF token is echoed in responses:** the token appears in Document
  responses (`"csrf": {"name": "ENO_CSRF_TOKEN", "value": …}`), and
  `ownerInfo` carries `firstname`/`lastname`. Anything that records 3DX
  traffic must strip both. The recorder's first pass missed both;
  re-sanitized before any commit.
- **FCS ticket handling is asymmetric:** the FCS upload is sent outside the
  client's session (`requests.post`). The job ticket goes raw in a form field
  on check-in, but URL-encoded in the query on download.
- **Masks:**
  - `dsmveng:EngItemMask.Details` works on `dseng`; `dskern:Mask.Details`
    does not.
  - `dsxcad:xCADAttributes` exists.
  - The `documents/parentId` route exists and validates its parent.
- **Unknown item id:** an unknown engineering item id gives
  `404 "URI not Found."`.
- **Wrong credentials:** the passport still answers 200 (no CASTGC cookie).
  The cell's own sync log showed this failure from 2026-10-15 until `.env`
  was fixed on 2026-10-30.

## 8. Tenant objects created

These are all Documents on the UW 3DX tenant. None was related to an
engineering item, and no Issue was created. The link tests (section 6)
created nothing.

**Every one of them was deleted on 2026-10-30, at Colin's request, after its
findings were recorded here and in `docs/backends/dx3.md`.** Each was
confirmed gone by reading it back, which answers
`400 "Invalid Business Object Specified."`.

| Created (UTC) | Title | By |
|---|---|---|
| 21:36:56 | `TEST_PLM_BRIDGE_PLAN_<part>_A.1_ORDERED` | Phase 0 smoke S4 |
| 21:39:58 | `TEST_PLM_BRIDGE_PLAN_<part>_A.1_ORDERED` | Phase 1 smoke S4 |
| 22:00:40 | `TEST_PLM_BRIDGE_CONTRACT_PLAN` | contract fixture recording |
| 22:08:17 | `TEST_PLM_BRIDGE_PLAN_<part>_A.1_ORDERED` | Phase 2 smoke S4 |
| 22:17:59 | `TEST_PLM_BRIDGE_PLAN_<part>_A.1_ORDERED` | Phase 4 smoke S4 |
| 22:32:32 | `TEST_PLM_BRIDGE_RESULT_<part>_A.1_run_synthetic_plm_bridge` | live result upload (synthetic run) |
| 23:07:45 | `TEST_PLM_BRIDGE_PLAN_<part>_A.1_ORDERED` | final smoke S4 |

The two August test Documents named in `docs/backends/dx3.md` (titled
`PLAN_<part>_A.1`, created 2026-08-12) were deleted at the same time. The
cell's real uploaded plan from 2026-08-26 was not touched. The cleanup tool
is `tools/dx3_delete_test_documents.py`.

## 9. Breaking changes for the cell

- **Workspace.** ViewpointGeneration `plm-bridge` needs this repository in the
  same colcon workspace (it depends on `plm_interfaces` and `cad_loader`).
  inspection-docker's `ros2_ws/src/shared.repos` adds it, and since the
  repository is public, `vcs import` needs no credentials. Without
  `plm_bridge_ros`, bringup logs a message and runs without the catalog.
- **Interfaces** (now in `plm_interfaces`). Field renames:
  - `eng_item_id` becomes `backend` + `part_id`;
  - `cestamp` becomes `change_token`;
  - `collab_space` becomes `container`;
  - `step_file_path`/`step_path` become `geometry_path`;
  - `step_cached`/`step_available` become `geometry_cached`/`geometry_available`;
  - `plan_doc_id` and `result_doc_id` become `remote_ref`.

  `UploadPlan` takes a `plan_id`. `SyncNow` returns `SyncResult[]`. New:
  `ListBackends`, `DescribePlans`, `RecordRun`. Topic and service names are
  unchanged (`/catalog/...`), but the node is now `/plm_bridge`.
- **Parameters.**
  - Core settings are `core.*` (they were `catalog.*`): `core.sync_interval`,
    `core.mesh_units`, `core.auto_upload_plan_stages`, and so on.
  - `catalog.bookmark_scope`, `use_bookmark_scope`, `collab_space_filter`,
    `page_size`, `max_items` and `fetch_thumbnails` became `dx3.*`.
  - New: `core.backends`, `core.title_prefix`, `core.picker_enabled`,
    `core.picker_port`, `core.namespace`, `core.describe_plans_service`.

  Launch arguments are unchanged, and the bringup argument `plm_backends` is
  new. The service and topic namespace is still `catalog`.
- **Environment.** Existing `DX_*` and `CATALOG_*` names are unchanged. New:
  `PLM_BACKENDS` (default `dx3`), `CATALOG_TITLE_PREFIX`,
  `DX_DOCUMENT_LINKS`, `PLAN_DESCRIBE_CMD`, `CATALOG_MATURITY_FILTER` (which
  falls back to `DX_MATURITY_FILTER`).
- **Commands.** `python -m viewpoint_generation.catalog.sync` becomes
  `plm-bridge` (same flags). The `catalog_node` and `picker_node` executables
  are gone; use `ros2 launch plm_bridge_ros plm_bridge.launch.py`. The picker
  is served by the node.
- **Database.** The first start of the new code migrates `catalog.db` in
  place: schema 0→2, after writing `catalog.db.bak-<stamp>`. **Old catalog
  code cannot read a migrated database.** To go back, stop the cell and
  restore the `.bak`. No cached file moves; new STEPs go to
  `{storage_key}/geometry/`.
- **Plan files** are written as schema 3.0. ViewpointGeneration still reads
  2.0, 1.0 and bare results.
- **Result manifests** are `envelope_version: 2.0` (`plm_context` with
  `backend`/`part_id`/`change_token`/`plan_ref`).

## 10. Open issues and follow-ups

- **Inspection_Control follow-up (not implemented).** The TSDF pose node
  could load parts through `cad_loader` and learn the selected part from
  `PartSelected`, instead of its own model loading.
- **Phase 3 is deferred.** The Onshape backend is to be ported from Colin's
  spike, with blob-element plans and a mass-property change token. A local
  (directory) backend is also missing.
- **Cross-cell plan discovery on 3DX** needs another route, because the
  relationship writes fail (section 6). Searching for plans by title
  (`documents/search`, filtered to the exact `PLAN_<part>_<rev>_` prefix)
  would work without a relationship. It is not built (QUESTIONS.md).
- **Merged into `main`** (2026-10-30, at Colin's request): ViewpointGeneration
  `main` = `3ffc150`, inspection-docker `main` = `10bab66`. Both are
  `--no-ff` merges of the `plm-bridge` branches, and each tree is identical
  to its branch. Each brings in the `feature-3dx-integration` history.
  Colin's local checkouts (with uncommitted work) were not touched. His
  ViewpointGeneration edits rebased onto the new `main` are in
  `/home/macs/plm_bridge_work/colin_vg_edits_on_new_main.patch`: the
  README and `bringup.launch.py` conflicts are resolved by keeping both sides.
- **Untested live:** Issue creation and the JMS listener remain so.
  Inspection_Control does not call `RecordRun` yet.
- **Tenant identifiers already public.** inspection-docker's history on
  `main` and `feature-3dx-integration` contains the tenant id, hostnames, and
  the organization and collaborative-space names. Colin decided to leave
  that history as it is; the branch tips no longer contain them.
- **ament lint.** ViewpointGeneration's ament flake8/pep257 tests fail
  throughout, as before this work. The new packages are flake8-clean apart
  from `step_loader.py` and the dx3 client and JMS modules, which were moved
  verbatim.
- **Picker plan chips** show the producer's full summary
  ("8 regions, 65 clusters, 65 viewpoints") instead of "8r · 65c · 65v",
  and may be wider.
- **Regression caught and fixed.** The parameter rename (`0aaecba`) also
  rewrote `self.catalog.backends` in the node, so the node could not start.
  The final smoke run caught it before anything else used the code. It was
  fixed in `6ff3ae4`, and `plm_bridge_ros/test/test_node.py` now constructs
  the node.

## Secrets

- `.env` was never staged.
- Every push went through a scan: generic credential patterns, plus the
  literal `.env` values (password, keys, tenant, SecurityContext parts,
  username, hostnames), plus owner-name tokens.
- The recorded fixture was sanitized at record time and audited before
  commit. The audit caught the username, the CSRF token and the owner's
  first and last names, which were removed before the first commit.
- The only scan warnings were Colin's own name as package maintainer, as
  license holder, in `cacton77` URLs, and in the status file.
- Before the repository was made public, its whole history was scanned for
  every identifier above. The only finds were Colin's name and the object
  ids of the test Documents in earlier versions of this report; those
  Documents have since been deleted.
- In one push (VG `307a7a7`) the scan's exit status was masked by a pipe.
  Its only finding was that name. The pushes after it used a script that
  stops on any finding.
