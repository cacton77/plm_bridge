# Questions for Colin

I worked unattended, so every question below was settled by a safe default
for now. The default is stated with each one. Most important first.

1. **Re-selecting the part that is already loaded (ViewpointGeneration).**
   `_part_selected_cb` in `viewpoint_generation_node.py` treats
   `set_mesh_file()`'s "Mesh file and units already set." as a load failure.
   It then logs "Failed to load selected model" and skips both
   `_apply_plm_context()` and the STALE/SELECTED warnings. Plan loading is
   still correct, because the plan is loaded before the mesh. This predates
   the extraction. Should "already set" count as success? It's about a
   three-line change.
   *Default: not changed.*

2. **May I test `POST documents/parentId/{engItemId}` on the tenant?**
   `GET documents/parentId/{id}?parentRelName=SpecificationDocument&parentDirection=from`
   exists and validates its parent (`docs/backends/dx3.md`), so its POST
   counterpart may be the Document-to-item link the integration has been
   missing. Testing it creates one `TEST_PLM_BRIDGE_` Document **attached to
   a real engineering item** (for example "Test"), which falls outside the
   test-run rules. If it works, `list_related_documents()` should use the GET
   route, and dx3 can declare `link_attachment` (cross-cell plan discovery).
   *Default: not tried.*

3. **Merging the inspection-docker `plm-bridge` branch.** It edits the
   committed layout (`src/shared.repos`, root `docker-compose.yaml`,
   `.env.example`, `docs/3dx_integration/`). Your uncommitted working copy
   moves those to `ros2_ws/src/` and `docker/`, and also edits two of the
   moved docs. Do you want the branch rebased onto your reorganisation once
   it's committed, or will you carry the five small edits across yourself?
   *Default: left on the old layout.*

4. **License.** `LICENSE` is a placeholder; which license should it be?
   *Default: none (private, all rights reserved).*

5. **Tenant identifiers already in public history.** inspection-docker's
   `main` and `feature-3dx-integration` already publish the tenant id,
   hostnames, organization and collaborative-space name (`.env.example`, the
   3DX docs). The `plm-bridge` branch removes them from the tip only.
   Rewriting public history is your call.
   *Default: not rewritten.*

6. **Test Documents on the tenant.** Six `TEST_PLM_BRIDGE_*` Documents were
   created (ids in REPORT.md section 8), and two from August are listed in
   `docs/backends/dx3.md`. I didn't delete anything. Delete them, or keep the
   contract-recording one (`TEST_PLM_BRIDGE_CONTRACT_PLAN`) for re-recording?
   *Default: kept.*

7. **Onshape (Phase 3).** When it's time, should the backend port the spike's
   mass-property fingerprint as the change token, and blob elements in the
   part's document for plans? Those are the spike's findings, with blob
   round-trips still open. *Default: deferred.*

8. **Parameter prefix.** The node is now `plm_bridge`, but its core
   parameters kept the `catalog.` prefix, so nothing that sets them breaks.
   Rename them to `plm_bridge.`/`core.` now, or later together with the
   `catalog` topic namespace? *Default: unchanged.*
