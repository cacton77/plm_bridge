# tools

Diagnostics against a live 3DX tenant. They need the `DX_*` environment and
network access. All are read-only (GET requests on parts in the configured
scope) except the cleanup tool, which says so:

| Script | Answers |
|---|---|
| `dx3_probe_attributes.py` | Which engineering attributes the REST API exposes per part (`dsmveng:EngItemMask.Details` -> `dseno:EnterpriseAttributes`, `dsxcad:Part/{id}/dsxcad:xCADAttributes`) |
| `dx3_probe_document_parent.py` | Whether `documents/parentId/{id}` (the Documents API's parent-relationship route) exists and validates its parent |
| `dx3_delete_test_documents.py` | **Writes.** Lists (dry run) or deletes the `TEST_PLM_BRIDGE_*` Documents test runs leave behind; titles are checked before deleting, deletions are confirmed by reading back |

```bash
python3 tools/dx3_probe_attributes.py
```

Results from 2026-10-30 are in `docs/backends/dx3.md`.
