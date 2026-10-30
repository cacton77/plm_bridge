"""plm_bridge: a local parts catalog over one or more PLM systems.

Keeps a SQLite index of the parts each configured backend reports, caches
their STEP files and thumbnails, and exchanges inspection plans and results
with the PLM record. No ROS imports; the ROS node is in `plm_bridge_ros`.

    core/       -- Catalog (reconciliation, plans, runs), CatalogDB, paths,
                   CoreConfig, the plan contract. Imports only backends.base.
    backends/   -- the PLMBackend protocol (base), the registry, a fake, and
                   dx3/ (3DEXPERIENCE: client, config, backend, JMS events)
    factory     -- builds a Catalog from the environment via the registry
    cli         -- the `plm-bridge` command
    picker/     -- the browser part picker (Flask), driven by callbacks
    thumbnails  -- local preview rendering (through cad, the loader shim)

Import from the submodules directly; nothing is re-exported here.
"""
