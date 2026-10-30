# cad_loader

Loads CAD models for inspection planning: STEP files with their B-rep
topology, and every tessellated mesh format Open3D reads. No ROS imports; it
installs with pip as well as with colcon.

```python
from cad_loader.step_loader import load_step
from cad_loader.mesh_io import read_mesh_file, mesh_file_units

result = load_step('part.stp')            # always metres
result.mesh                               # open3d TriangleMesh, welded
result.brep_faces                         # one BRepFace per B-rep face
result.tri_to_brep                        # triangle index -> face id
result.face_adjacency                     # face id -> edge-sharing face ids

mesh, error = read_mesh_file(path)        # any of .stl .obj .ply .off .stp .step
scale_units = mesh_file_units(path, 'mm') # 'm' for STEP, the configured units otherwise
```

## Install

```bash
colcon build --packages-select cad_loader         # in a ROS workspace
pip install './cad_loader[step]'                  # anywhere; [step] adds cadquery-ocp
```

Dependencies: `numpy`, `open3d`; STEP needs the OCP bindings (`cadquery-ocp`,
7.x or 8.x).

## Rules for model files

Never call `o3d.io.read_triangle_mesh()` on a path that could be a model an
operator selected. It cannot parse STEP and signals that by returning an
*empty mesh*, not an error, so the caller silently displays nothing. Use
`read_mesh_file()`, and scale the result by
`mesh_file_units(path, configured_units)`, not by the configured units: for
a STEP file it is always `'m'`.

## STEP loading invariants

If you touch `step_loader.py`, preserve these:

- **The vertex weld stays** (`merge_close_vertices`). OpenCascade tessellates
  each B-rep face with its own vertex pool; without the weld, adjacent faces
  share no vertex indices and a mesh segmenter cannot grow a region across a
  face boundary.
- **Rebuild `tri_to_brep` and `BRepFace.triangle_indices` after the weld**,
  because welding renumbers and can drop triangles.
- **STEP geometry is always returned in metres.** OpenCascade converts every
  STEP to its working unit (mm, pinned via `xstep.cad.unit`) whatever the file
  declares, so a caller-supplied unit can never be right or wrong for STEP;
  `load_step()` ignores its `units` argument. Absolute tessellation
  deflections are configured in metres and converted to OCC's mm.
- **Keep the OCP 7/8 import fallbacks** in `_import_occ()`: OCP 8 moved the
  TopTools collection typedefs to `OCP.collections` and renamed
  `TopoDS.Face_s` to `TopoDS.Face`.
- **B-rep face identity comes from OCC's own shape map**, not Python `id()`
  or `hash()`: OCP returns a fresh wrapper object per access, so Python
  identity differs between two handles to the same face.

## Tests

```bash
python3 -m pytest cad_loader/test     # generates a STEP box with OpenCascade; skips without OCP
```
