# Questions for Colin

## Answered (2026-10-30)

| # | Question | Answer | What was done |
|---|---|---|---|
| 1 | Should re-selecting the loaded part count as success? | Yes | Fixed in ViewpointGeneration `afc94f9`. The final smoke run checks it strictly. |
| 2 | Test `POST documents/parentId` on the tenant? | Go ahead | Tested live. No route works: 405 on the parentId POST, and 500 on creating with parent parameters (three relationship types). Nothing was created. See REPORT.md section 6. |
| 3 | How to merge the inspection-docker branch? | The repo was reorganised into a `ros2_ws/` workspace; fix what wasn't updated | Copied your reorganisation into `plm-bridge` as its own commit (`b46ae16`), redid the plm_bridge edits on top, and ignored everything under `ros2_ws/` except the manifest (`d59ba93`). Two runtime files were left untracked and unignored. |
| 4 | License? | BSD, and make the repo public | BSD-3-Clause, Copyright (c) 2026 Colin Acton. Public after a full-history scan. |
| 5 | Rewrite public history that holds tenant identifiers? | Default | Not rewritten. |
| 6 | Delete the test Documents? | Yes, once findings are preserved | All 7 `TEST_PLM_BRIDGE_*` Documents and the 2 August ones deleted, each confirmed gone. |
| 7 | Onshape design choices for Phase 3? | Default | Deferred. |
| 8 | Rename the core parameter prefix? | Rename | `catalog.*` became `core.*` (`0aaecba`, fixed in `6ff3ae4`). The topic and service namespace is still `catalog`. |

## Open

1. **Cross-cell plan discovery on 3DX without a relationship.** Uploaded plans
   are titled `PLAN_<part number>_<revision>_<STAGE>`, and
   `documents/search?searchStr=` works (fuzzy, so titles would be filtered
   to the exact prefix). Should dx3's `list_attachments` find plans that way
   and declare `link_attachment`? Then a second cell could download a plan
   another cell uploaded for the same revision. The risks: titles are not
   identity, so another uploader's same-titled document would match; and
   every `ensure_plan` that misses locally costs one search call.
   *Default: not built.*
2. **Merging: done** (2026-10-30). ViewpointGeneration `main` = `3ffc150`,
   inspection-docker `main` = `10bab66`.
