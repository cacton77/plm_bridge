# plm_bridge extraction: report

Status: **in progress** (draft, updated at the end of every phase).

This report separates what was verified against a live system from what was
verified offline only. Open questions for Colin are in `QUESTIONS.md`.

## Scope change (2026-10-30)

Before Phase 0, Colin narrowed the work: the priority is getting the 3DX
integration into the new package; **no Onshape backend and no Onshape
references in the new package for now**. Phase 3 (local and Onshape backends)
is deferred; the backend protocol is still designed to be generic.

## Phase 0: baseline and characterization tests

ViewpointGeneration `plm-bridge` commit `b4a950d`.

- 44 pytest characterization tests added under `viewpoint_generation/test/`
  (plan_io; CatalogSync reconciliation, paging, bookmark and space scoping;
  plan history, staleness, upload policy, orphan adoption; result upload and
  NCR issue threshold; CatalogDB migration; STEP loader on an
  OpenCascade-generated box). All pass in the `inspection-docker:jazzy`
  container. No ROS or network needed (`FakeDXClient`).
- The package's existing ament `flake8`/`pep257` tests already failed before
  this work (about 1,800 and 1,100 findings) and are deselected; they are not
  a usable gate.
- Baseline bringup (`catalog:=true picker:=true`, headless, no cell) starts
  the catalog node and picker and serves the cached catalog.

### Smoke checklist, Phase 0 (baseline code, live 3DX, 2026-10-30)

| # | Result | Evidence |
|---|---|---|
| S1 | pass | Bookmark scope, 6 engineering items; two full syncs, both "0 added, 0 modified, 6 unchanged" (about 4 s) |
| S2 | pass | Picker lists 6 parts; both parts with a cached STEP have a locally rendered thumbnail |
| S3 | pass | Cached STEP deleted; selection re-downloaded it from 3DX derived outputs; VG loaded it (`source_format: STEP`, regions carry `brep_face_ids`) |
| S4 | pass | Segment, cluster, project, order: four plan rows; only `ordered` auto-uploaded, as a `TEST_PLM_BRIDGE_` Document |
| S5 | pass | Re-selection returns CURRENT and VG loads the ordered plan; with the plan's token changed, selection returns STALE and VG loads no plan |
| S6 | pass | `--network none`, credentials set: cached part selected, four stages recorded locally, upload failed cleanly (`upload_status=failed`) |

How the smoke run works, and its limits:

- **No cell.** The real traversal node needs MoveItPy and the cell's MoveIt
  configuration, so the `ordered` stage comes from a stub
  `viewpoint_traversal/optimize_traversal` service. The stub writes the plan
  with VG's own `plan_io.write_plan` (trivial visiting order, no TSP); the VG
  node's real recording path then runs unchanged.
- **Segmentation.** PartField needs the GPU model under `/models`, so the
  smoke run uses `regions.algorithm: brep`.
- **Tenant hygiene.** A guard loaded through `sitecustomize` forces every
  created Document title to start with `TEST_PLM_BRIDGE_`, and stubs out
  document-to-item linking and Issue creation.
- **S5 check.** The first version of the check also required VG's "earlier
  CAD revision" warning. That warning never fires on re-selection because of
  a pre-existing VG quirk (see open issues), so S5 was re-evaluated from the
  log against what the checklist actually asks.

## Phase 1: cut the couplings in place

ViewpointGeneration `plm-bridge` commit `88445ad`.

- **Plan contract.** `catalog/plan_contract.py` is in place, and the catalog
  imports no `plan_io`. `PartSelected` gained `plan_dir` and
  `plm_context_json`. `RecordPlan` gained `stage_rank`, `summary_json`,
  `summary_text`, `change_token` and `generated_at`, alongside the old fields.
- **Plans table.** It has new columns, and versioned migrations
  (`PRAGMA user_version`) back the database up first. A copy of the real
  `catalog.db` (11 plan rows across 2 parts) migrated with a `.bak` file
  written; the legacy counts became `summary_text`/`stage_rank`.
- **Orphan adoption.** It moved to the producer through a new
  `DescribePlans` service on the VG node, plus a
  `plan_io describe` CLI for the catalog CLI. The plan suggested "a CLI
  subcommand or a node service"; I did both, and the catalog only ever lists
  file names. **Behaviour change:** an adopted file is now recorded with its
  *own* change token when it has one. Previously every adopted file took the
  part's current cestamp, so an old file was always shown as CURRENT.
- **Picker.** It runs inside the catalog node with injected callbacks, and
  `picker_node` is gone.
- **Thumbnails.** They load STEP only through `catalog/cad.py`.
- **Tests.** 50 pass. Live smoke S1–S6 all pass, plus X1 (the picker's
  "Scan for files" adopting an orphan plan through `describe_plans`).

## Tenant objects created

| When (UTC) | System | Kind | ID | Title | By |
|---|---|---|---|---|---|
| 2026-10-30T21:36:56Z | 3DX | Document | `F74C7BC56D720F006AE50DF600026546` | `TEST_PLM_BRIDGE_PLAN_<part number of "Test">_A.1_ORDERED` | Phase 0 smoke S4 |
| 2026-10-30T21:39:58Z | 3DX | Document | `9B76B1F917A924006AE50EAB00023334` | `TEST_PLM_BRIDGE_PLAN_<part number of "Test">_A.1_ORDERED` | Phase 1 smoke S4 |

## Open issues found so far

- **3DX credentials.** At the start of the session the passport rejected the
  credentials in `.env` (the catalog's own sync log shows the same failure
  since 2026-10-15). Colin fixed `.env` during the session; login works.
- **Re-selecting the loaded part logs an error (pre-existing, not fixed).**
  When the selected model is already loaded, `set_mesh_file()` returns
  "Mesh file and units already set." and `_part_selected_cb` treats that as a
  failure: it logs "Failed to load selected model" and returns early. That
  skips `_apply_plm_context()` and the STALE/SELECTED warnings. Plan loading
  itself still behaves correctly, because the plan is loaded before the mesh.
