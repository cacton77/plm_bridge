# tools

Read-only diagnostics against a live 3DX tenant (they need the `DX_*`
environment and network access, and only issue GET requests on parts in the
configured scope):

| Script | Answers |
|---|---|
| `dx3_probe_attributes.py` | Which engineering attributes the REST API exposes per part (`dsmveng:EngItemMask.Details` -> `dseno:EnterpriseAttributes`, `dsxcad:Part/{id}/dsxcad:xCADAttributes`) |
| `dx3_probe_document_parent.py` | Whether `documents/parentId/{id}` (the Documents API's parent-relationship route) exists and validates its parent |

```bash
python3 tools/dx3_probe_attributes.py
```

Results from 2026-10-30 are in `docs/backends/dx3.md`.
