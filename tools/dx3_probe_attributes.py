"""Read-only probes: engineering attributes and Document links on 3DX (dx3).

GET requests only, on the parts in the configured bookmark scope. Prints
status codes, attribute names and short values (owner names masked).
"""

import json
import os
import re
import sys

from plm_bridge.backends.dx3.backend import DX3Backend
from plm_bridge.backends.dx3.client import DXClient
from plm_bridge.backends.dx3.config import DX3Settings, DXConfig

config, settings = DXConfig.from_env(), DX3Settings.from_env()
client = DXClient(config)
ok, message = client.ensure_login()
if not ok:
    sys.exit(message)
space = config.space_url.rstrip('/') + '/resources/v1/modeler'
owner = config.security_context.split('.')[-1].replace(' Space', '')
mask_names = [re.compile(re.escape(t), re.I) for t in owner.split() if len(t) > 2]
mask_names.append(re.compile(re.escape(config.username), re.I))


def clean(value):
    text = json.dumps(value)[:60]
    for pattern in mask_names:
        text = pattern.sub('<name>', text)
    return text


def get(path, params=None):
    response = client._request('GET', space + path, params=params)
    try:
        body = response.json()
    except ValueError:
        body = None
    return response.status_code, body


backend = DX3Backend(config, settings, client)
parts = list(backend.list_scope(backend.scope))
print(f'{len(parts)} parts in scope')
for index, part in enumerate(parts):
    pid = part.part_id
    print(f'--- part {index} ({part.title})')
    status, body = get(f'/dseng/dseng:EngItem/{pid}', {'$mask': 'dsmveng:EngItemMask.Details'})
    member = (body or {}).get('member', [{}])[0] if body else {}
    attrs = member.get('dseno:EnterpriseAttributes') if isinstance(member, dict) else None
    print('  EngItemMask.Details', status, 'keys:', sorted(member)[:20] if member else None)
    print('  dseno:EnterpriseAttributes:', {k: clean(v) for k, v in (attrs or {}).items()})
    status, body = get(f'/dseng/dseng:EngItem/{pid}/dseng:EnterpriseReference')
    print('  dseng:EnterpriseReference', status, 'keys:',
          sorted(((body or {}).get('member') or [{}])[0]) if body else None)
    status, body = get(f'/dsxcad/dsxcad:Part/{pid}/dsxcad:xCADAttributes')
    xmember = ((body or {}).get('member') or [{}])[0] if body else {}
    xattrs = xmember.get('dsxcad:xCADAttributes') if isinstance(xmember, dict) else None
    print('  dsxcad:xCADAttributes', status,
          {k: clean(v) for k, v in (xattrs or {}).items()} if isinstance(xattrs, dict)
          else clean(xattrs) if xattrs else (clean(body)[:60] if body else None))
    if index == 0:
        for rel in ('SpecificationDocument', 'Reference Document', 'PLMDocConnection'):
            status, body = get(f'/documents/parentId/{pid}',
                               {'parentRelName': rel, 'parentDirection': 'from'})
            print(f'  documents/parentId ({rel})', status,
                  'items:', (body or {}).get('items') if body else None,
                  clean((body or {}).get('error') or (body or {}).get('message') or '')
                  if body else '')
client.close()
