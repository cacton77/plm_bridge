"""The catalog's one route to CAD loading.

Thumbnail rendering is the only thing in the catalog that reads geometry, and
it does so through this module alone. The loader is `cad_loader`, an optional
dependency (`pip install plm_bridge[thumbnails]`); without it, previews are
simply not rendered.
"""

from cad_loader.step_loader import load_step  # noqa: F401
