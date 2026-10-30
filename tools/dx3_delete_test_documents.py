"""Delete the Documents that test runs left on a 3DX tenant.

    python3 tools/dx3_delete_test_documents.py                 # dry run: list them
    python3 tools/dx3_delete_test_documents.py --delete
    python3 tools/dx3_delete_test_documents.py --delete \\
        --id <docId> --expect-title '<exact title>'            # one more, pinned

Finds Documents whose title starts with --prefix (default TEST_PLM_BRIDGE_)
through the Documents search. The search is fuzzy, so only exact prefix
matches are kept. Documents given with --id are deleted only when their
current title equals --expect-title. Each title is read again just before
deleting, and each deletion is confirmed by reading the Document back. The
catalog itself never deletes anything; this is test hygiene only.
"""

import argparse
import sys

from plm_bridge.backends.dx3.client import DXClient
from plm_bridge.backends.dx3.config import DXConfig


def title_of(client, docs, doc_id):
    """(status, title) of one Document; title None when it does not exist."""
    response = client._request('GET', f'{docs}/{doc_id}')
    try:
        data = response.json().get('data') or []
    except ValueError:
        data = []
    title = (data[0].get('dataelements') or {}).get('title') if data else None
    return response.status_code, title


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--prefix', default='TEST_PLM_BRIDGE_')
    parser.add_argument('--id', action='append', default=[], help='Also delete this Document')
    parser.add_argument('--expect-title', action='append', default=[],
                        help='Exact current title of each --id (same order)')
    parser.add_argument('--delete', action='store_true', help='Delete (default: dry run)')
    args = parser.parse_args(argv)
    if len(args.id) != len(args.expect_title):
        parser.error('every --id needs an --expect-title')

    config = DXConfig.from_env()
    client = DXClient(config)
    ok, message = client.ensure_login()
    if not ok:
        print(message)
        return 2
    docs = config.space_url.rstrip('/') + '/resources/v1/modeler/documents'

    targets = {}
    response = client._request('GET', f'{docs}/search',
                               params={'searchStr': args.prefix, '$top': '500'})
    for item in response.json().get('data') or []:
        title = (item.get('dataelements') or {}).get('title') or ''
        if title.startswith(args.prefix):
            targets[item['id']] = title
    targets.update(dict(zip(args.id, args.expect_title)))

    failures = 0
    for doc_id, expected in sorted(targets.items(), key=lambda kv: kv[1]):
        status, title = title_of(client, docs, doc_id)
        if title != expected:
            print(f'SKIP {doc_id}: title is {title!r}, expected {expected!r}')
            failures += 1
            continue
        if not args.delete:
            print(f'would delete {doc_id}  {title}')
            continue
        response = client._request('DELETE', f'{docs}/{doc_id}')
        after_status, after_title = title_of(client, docs, doc_id)
        gone = after_title is None
        print(f"{'deleted' if gone else 'NOT DELETED'} {doc_id}  {title}  "
              f'(DELETE {response.status_code}; read back {after_status})')
        failures += 0 if gone else 1
    client.close()
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
