# dx3 design history

The documents that designed the 3DEXPERIENCE integration, kept for history.
Code references in them predate the extraction into plm_bridge (they name
`viewpoint_generation.catalog`, `CatalogSync`, `eng_item_id` and `cestamp`).
What the tenant actually does is in [`../dx3.md`](../dx3.md).

| File | What it is |
|---|---|
| `3dx_catalog_integration_plan.md` | The original integration design |
| `3dx_step_ingest_addendum.md` | STEP ingest and the B-rep loader |
| `3dx_plan_sync_addendum.md` | Plan history and plan upload |
| `3DX_API_EXPLAINED.md` | A walk-through of the 3DX REST concepts |
| `3dx_integration_setup_checklist.md` | Setting up credentials and a SecurityContext |
| `3dx_integration_agent_prompt.md` | The brief the first implementation was built from |
| `3dx_rest_api_tour.ipynb` | Notebook of live calls (outputs cleared) |

Identifiers of the tenant (ids, hostnames, organization, space and personal
names) have been replaced with example values.
