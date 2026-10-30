# Questions for Colin

Collected while working unattended. Where a question blocked something, the
safe default that was taken instead is stated. Newest last.

1. **Re-selecting the part that is already loaded.** `_part_selected_cb` in
   `viewpoint_generation_node.py` treats `set_mesh_file()`'s "Mesh file and
   units already set." as a load failure. It logs an error and skips the
   STALE/SELECTED warnings and `_apply_plm_context()`. This predates the
   extraction and was left alone, as planner-node behaviour. Should the
   callback treat "already set" as success? It's about a three-line change.
   *Default taken: not changed.*
