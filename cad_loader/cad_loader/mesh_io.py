"""Reading model files into Open3D meshes, STEP included.

Never call `o3d.io.read_triangle_mesh()` on a model an operator selected: it
cannot parse STEP and signals that failure by returning an *empty mesh*
rather than raising, so the caller silently displays nothing. Use
`read_mesh_file()`, which dispatches on the extension and returns
`(mesh, error)` in the file's own units, and scale the result by
`mesh_file_units(path, configured_units)`, not by the configured units: for a
STEP file it is always `'m'`.
"""

import os

import open3d as o3d

# Tessellated STEP meshes, keyed by (path, mtime, size). Tessellation is far
# more expensive than reading an STL, and viewers re-read the model file every
# time the results change, so a large assembly would otherwise be
# re-tessellated on every recompute. Entries are handed out as copies, since
# callers scale the mesh they receive.
_STEP_CACHE = {}
_STEP_CACHE_LIMIT = 4

STEP_EXTENSIONS = ('.stp', '.step')
# STEP meshes come back from the loader in metres whatever the file declares
# (see step_loader's module docs); mirrors step_loader.STEP_MESH_UNITS, which
# is not imported here so this module never pulls in OpenCascade.
STEP_MESH_UNITS = 'm'


def mesh_file_units(file_path: str, units: str) -> str:
    """The units a model file's geometry is really in, given the configured ones.

    For tessellated formats that is whatever the caller configured, since those
    files carry no units. A STEP file declares its own, and OpenCascade converts
    them on read, so its geometry is always in `STEP_MESH_UNITS` and the
    configured value is ignored. Callers that scale what `read_mesh_file()`
    returns must scale by this, not by the configured units.
    """
    if os.path.splitext(file_path or '')[1].lower() in STEP_EXTENSIONS:
        return STEP_MESH_UNITS
    return units


def read_mesh_file(file_path: str):
    """Read any supported model file into an Open3D mesh, in the file's own units.

    For a STEP file "its own units" are always metres; scale by
    `mesh_file_units()` rather than the configured units.

    Open3D reads tessellated formats (STL/OBJ/PLY/OFF) but cannot parse STEP,
    which it fails on silently by returning an empty mesh. This dispatches on
    the extension and tessellates STEP through OpenCascade instead.

    The returned geometry is *unscaled*, matching what `read_triangle_mesh`
    would give: the caller applies its own unit conversion.

    Args:
        file_path: Path to an .stl/.obj/.ply/.off/.stp/.step file.

    Returns:
        tuple: (mesh, error). mesh is None on failure, with error explaining why.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension in STEP_EXTENSIONS:
        try:
            stat = os.stat(file_path)
        except OSError as e:
            return None, f'Could not stat STEP file {file_path}: {e}'
        key = (os.path.abspath(file_path), stat.st_mtime, stat.st_size)
        cached = _STEP_CACHE.get(key)
        if cached is None:
            from cad_loader.step_loader import load_step_mesh
            mesh, error = load_step_mesh(file_path)
            if mesh is None:
                return None, error
            if len(_STEP_CACHE) >= _STEP_CACHE_LIMIT:
                _STEP_CACHE.pop(next(iter(_STEP_CACHE)))
            _STEP_CACHE[key] = mesh
            cached = mesh
        # A copy, because callers scale what they are handed and would
        # otherwise compound that scaling into the cached mesh.
        return o3d.geometry.TriangleMesh(cached), ''

    try:
        mesh = o3d.io.read_triangle_mesh(file_path)
    except Exception as e:
        return None, f'Could not load mesh file {file_path}: {e}'
    if mesh.is_empty():
        return None, f'Mesh file {file_path} is empty or invalid.'
    return mesh, ''
