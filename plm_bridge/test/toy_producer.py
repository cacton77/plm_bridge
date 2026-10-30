"""A toy plan producer: the producer's side of the plan contract, for tests.

The bridge never opens a plan file; a producer writes them and describes
them. ViewpointGeneration is the real producer; this is the same contract
reduced to what the tests need, so the bridge's tests do not depend on it:

* `write_plan()` embeds the context the bridge published and adds only
  `stage`, `generated_at` and `software_version`;
* `describe_plan()` answers the `DescribePlans` contract.

Plans here look like ViewpointGeneration's results (meshes -> regions ->
clusters) only so the toy can count something; the bridge never looks.
"""

import json
import os
from datetime import datetime, timezone

SCHEMA_VERSION = '3.0'
STAGES = ('segmented', 'clustered', 'projected', 'ordered')


def stage_rank(stage):
    try:
        return STAGES.index(stage)
    except ValueError:
        return -1


def results_for(stage, regions=2, clusters_per_region=2, mesh_file='/models/part.stp'):
    """A minimal plan at the given stage."""
    region_list = []
    for r in range(regions):
        region = {'id': r, 'clusters': []}
        if stage in ('clustered', 'projected', 'ordered'):
            for c in range(clusters_per_region):
                cluster = {'id': c}
                if stage in ('projected', 'ordered'):
                    cluster['viewpoint'] = {'position': [0, 0, 1]}
                region['clusters'].append(cluster)
        if stage == 'ordered':
            region['order'] = {'greedy': {'order': list(range(clusters_per_region))}}
        region_list.append(region)
    return {'meshes': [{'file': mesh_file, 'regions': region_list}]}


def infer_stage(results):
    regions = ((results or {}).get('meshes') or [{}])[0].get('regions') or []
    if not regions:
        return 'empty'
    if any(isinstance(r.get('order'), dict) for r in regions):
        return 'ordered'
    if any('viewpoint' in c for r in regions for c in r.get('clusters') or []):
        return 'projected'
    if any(r.get('clusters') for r in regions):
        return 'clustered'
    return 'segmented'


def _counts(results):
    regions = ((results or {}).get('meshes') or [{}])[0].get('regions') or []
    clusters = [c for r in regions for c in r.get('clusters') or []]
    return {'num_regions': len(regions), 'num_clusters': len(clusters),
            'num_viewpoints': sum(1 for c in clusters if 'viewpoint' in c)}


def _text(counts):
    bits = [f'{counts[k]} {label}' for k, label in (
        ('num_regions', 'regions'), ('num_clusters', 'clusters'),
        ('num_viewpoints', 'viewpoints')) if counts.get(k)]
    return ', '.join(bits) or 'empty'


def _utc(timestamp=None):
    moment = (datetime.fromtimestamp(timestamp, timezone.utc) if timestamp is not None
              else datetime.now(timezone.utc))
    return moment.strftime('%Y-%m-%dT%H:%M:%SZ')


def write_plan(directory, results, stage=None, timestamp=None):
    """Write a plan into the directory the bridge named, as a producer does.

    Returns:
        tuple: (str path, str message)
    """
    stage = stage or infer_stage(results)
    context = dict(results.get('plm_context') or {})
    context.update({'stage': stage, 'generated_at': _utc(),
                    'software_version': 'toy-producer@1'})
    results['schema_version'] = SCHEMA_VERSION
    results['plm_context'] = context
    os.makedirs(str(directory), exist_ok=True)
    stamp = timestamp or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = os.path.join(str(directory), f'{stage}_{stamp}.json')
    counter = 2
    while os.path.exists(path):
        path = os.path.join(str(directory), f'{stage}_{stamp}-{counter}.json')
        counter += 1
    with open(path, 'w') as handle:
        json.dump(results, handle)
    return path, f'Plan saved to {path}.'


def describe_plan(path):
    """The DescribePlans contract for one file."""
    description = {'path': str(path), 'valid': False, 'stage': '', 'stage_rank': -1,
                   'summary_json': '{}', 'summary_text': '', 'change_token': '',
                   'generated_at': '', 'message': ''}
    try:
        with open(path) as handle:
            results = json.load(handle)
    except (OSError, ValueError) as e:
        description['message'] = str(e)
        return description
    counts = _counts(results)
    if not counts['num_regions']:
        description['message'] = 'Not a plan: it holds no regions.'
        return description
    context = results.get('plm_context') or {}
    stage = context.get('stage') or infer_stage(results)
    description.update({
        'valid': True, 'stage': stage, 'stage_rank': stage_rank(stage),
        'summary_json': json.dumps(counts, sort_keys=True), 'summary_text': _text(counts),
        'change_token': context.get('change_token') or context.get('cestamp') or '',
        'generated_at': context.get('generated_at') or _utc(os.stat(path).st_mtime),
    })
    return description
