"""Read-only: what does GET documents/parentId/{id} return? Prints structure only."""
import sys
from plm_bridge.backends.dx3.backend import DX3Backend
from plm_bridge.backends.dx3.client import DXClient
from plm_bridge.backends.dx3.config import DX3Settings, DXConfig
config, settings = DXConfig.from_env(), DX3Settings.from_env()
client = DXClient(config); client.ensure_login()
space = config.space_url.rstrip('/') + '/resources/v1/modeler'
part = next(p for p in DX3Backend(config, settings, client).list_scope(settings.bookmark_scope) if p.geometry_available is not False)
for rel in ('SpecificationDocument', 'Reference Document'):
    for direction in ('from', 'to'):
        r = client._request('GET', f'{space}/documents/parentId/{part.part_id}',
                            params={'parentRelName': rel, 'parentDirection': direction})
        try:
            body = r.json()
        except ValueError:
            body = None
        shape = {k: (type(v).__name__, len(v) if isinstance(v, (list, dict)) else v if isinstance(v, (bool, int)) else '')
                 for k, v in (body or {}).items() if k != 'csrf'}
        print(rel, direction, r.status_code, r.headers.get('content-type', '')[:30], shape)
# A nonsense parent id, to tell a working route from one that answers 200 to anything.
r = client._request('GET', f'{space}/documents/parentId/{"0" * 32}', params={'parentRelName': 'SpecificationDocument', 'parentDirection': 'from'})
print('unknown parent', r.status_code, (r.json() if 'json' in r.headers.get('content-type', '') else r.text[:80]) and {k: v for k, v in r.json().items() if k in ('success', 'statusCode', 'error', 'message', 'data')} if 'json' in r.headers.get('content-type','') else '')
client.close()
