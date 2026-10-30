# Backends

| Backend | Status | Notes |
|---|---|---|
| [`dx3`](dx3.md) | in use | 3DEXPERIENCE. What the tenant's REST API actually does, verified live. |
| `fake` | tests | In-memory; every capability can be switched on or off. |

A new backend must pass `plm_bridge/test/test_backend_contract.py`. See
"Adding a backend" in `plm_bridge/README.md`.
