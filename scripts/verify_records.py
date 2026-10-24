"""Check deposited hashes and descriptive arithmetic, without native experiments."""
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
KEYS = ('dataset', 'nlist', 'tag', 'workload', 'mode')
TIMED = ('active_seconds', 'joint_seconds', 'index_load_seconds', 'query_label_load_seconds', 'base_load_seconds', 'label_compute_seconds', 'warmup_seconds', 'peak_rss_mib', 'process_wall_seconds')
COUNTERS = ('scanned_vectors', 'scanned_lists', 'replayed_prefixes', 'cache_capacity_bytes', 'label_distance_evaluations')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def load_csv(name):
    with (ROOT / 'data' / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def same_number(actual, expected, context):
    require(math.isfinite(float(actual)) and math.isclose(float(actual), float(expected), rel_tol=1e-12, abs_tol=1e-12), f'{context}: {actual} != {expected}')

def main():
    manifest = json.loads((ROOT / 'FILE_MANIFEST.json').read_text(encoding='utf-8'))
    paths = [item['path'] for item in manifest['files']]
    require(len(paths) == len(set(paths)), 'Duplicate manifest path')
    for item in manifest['files']:
        path = (ROOT / item['path']).resolve()
        require(ROOT.resolve() in path.parents, 'Manifest path outside release')
        require(path.stat().st_size == item['bytes'], f'Size mismatch: {item["path"]}')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], f'Hash mismatch: {item["path"]}')
    runs, aggregates, comparisons, risks = [load_csv(name) for name in ('runs.csv', 'aggregate.csv', 'comparisons.csv', 'final-query-risk.csv')]
    require((len(runs), len(aggregates), len(comparisons), len(risks)) == (228, 76, 14, 4), 'Unexpected row counts')
    workload_counts = dict(Counter(row['workload'] for row in runs))
    require(workload_counts == {'single': 144, 'alpha4': 36, 'mixed16': 36, 'fresh': 12}, 'Unexpected workload counts')
    groups = defaultdict(list)
    for row in runs:
        require(all(value != '' for value in row.values()), 'Missing process record value')
        groups[tuple(row[key] for key in KEYS)].append(row)
    indexed = {tuple(row[key] for key in KEYS): row for row in aggregates}
    require(len(indexed) == 76 and set(indexed) == set(groups), 'Duplicate/missing aggregate key')
    aggregate_values_checked = 0
    for key, observations in groups.items():
        require(len(observations) == 3 and {r['rep'] for r in observations} == {'0', '1', '2'}, f'Incomplete repetitions: {key}')
        row = indexed[key]
        require(all(value != '' for value in row.values()), 'Missing aggregate value')
        for field in TIMED:
            values = [float(r[field]) for r in observations]
            require(all(math.isfinite(x) and x >= 0 for x in values), f'Invalid timing/memory: {key}/{field}')
            for suffix, value in (('', median(values)), ('_min', min(values)), ('_max', max(values))):
                same_number(row[field + suffix], value, str(key) + '/' + field + suffix)
                aggregate_values_checked += 1
        for field in COUNTERS:
            values = {int(r[field]) for r in observations}
            require(len(values) == 1 and min(values) >= 0, f'Nondeterministic counter: {key}/{field}')
            require(int(row[field]) == next(iter(values)), f'Counter mismatch: {key}/{field}')
            aggregate_values_checked += 1
    seen_comparisons = set()
    comparison_values_checked = 0
    for row in comparisons:
        key = tuple(row[k] for k in KEYS[:4])
        require(key not in seen_comparisons, 'Duplicate comparison')
        seen_comparisons.add(key)
        frontier = indexed[key + ('frontier',)]
        controls = [r for k, r in indexed.items() if k[:4] == key and k[-1] != 'frontier']
        best = min(controls, key=lambda r: float(r['active_seconds']))
        ordinary = min((r for r in controls if r['mode'] in ('complete', 'batch')), key=lambda r: float(r['active_seconds']))
        require(row['best_control'] == best['mode'] and row['ordinary_cache_control'] == ordinary['mode'], f'Control mismatch: {key}')
        ftime, btime, otime = (float(r['active_seconds']) for r in (frontier, best, ordinary))
        expected = {'best_control_active': btime, 'frontier_active': ftime, 'best_control_over_frontier': btime / ftime, 'frontier_time_reduction_fraction': 1 - ftime / btime, 'ordinary_cache_over_frontier': otime / ftime, 'best_control_vectors': best['scanned_vectors'], 'frontier_vectors': frontier['scanned_vectors'], 'ordinary_cache_vectors': ordinary['scanned_vectors'], 'frontier_replayed_prefixes': frontier['replayed_prefixes']}
        for field, value in expected.items():
            same_number(row[field], value, str(key) + '/' + field)
            comparison_values_checked += 1
        require(row['range_separated'] == str(float(frontier['active_seconds_max']) < float(best['active_seconds_min'])), f'Range flag mismatch: {key}')
        fresh_fields = ('joint_complete_over_frontier', 'complete_joint', 'frontier_joint', 'joint_range_separated')
        if row['workload'] == 'fresh':
            fj, oj = float(frontier['joint_seconds']), float(ordinary['joint_seconds'])
            for field, value in (('joint_complete_over_frontier', oj / fj), ('complete_joint', oj), ('frontier_joint', fj)):
                same_number(row[field], value, str(key) + '/' + field)
                comparison_values_checked += 1
            require(row['joint_range_separated'] == str(float(frontier['joint_seconds_max']) < float(ordinary['joint_seconds_min'])), 'Joint range flag mismatch')
        else:
            require(all(row[field] == '' for field in fresh_fields), 'Unexpected non-fresh joint comparison')
    require(seen_comparisons == {k[:4] for k in indexed if k[-1] == 'frontier'}, 'Missing frontier comparison')
    risk_summary = json.loads((ROOT / 'validation' / 'final-query-check-summary.json').read_text(encoding='utf-8-sig'))
    historic = {(r['dataset'], str(r['nlist']), float(r['gamma'])): r for r in risk_summary['risk']}
    risk_keys = {(r['dataset'], r['nlist'], float(r['gamma'])) for r in risks}
    require(len(risk_keys) == 4 and risk_keys == set(historic), 'Risk summary key mismatch')
    for row in risks:
        source = historic[(row['dataset'], row['nlist'], float(row['gamma']))]
        for field, value in row.items():
            if field == 'dataset':
                require(value == source[field], 'Risk dataset mismatch')
            else:
                same_number(value, source[field], 'risk/' + field)
        require(int(row['nq']) == 8976 and int(row['k']) == 100, 'Final-query scope mismatch')
        same_number(float(row['mean_recall']) + float(row['empirical_mean_fnr']), 1, 'Recall/FNR identity')
        require(int(row['strict_label_boundary_queries']) + int(row['tied_label_boundary_queries']) == 8976, 'Label-boundary count mismatch')
    require((ROOT / 'plotting' / 'evidence' / 'demand-calibration-workload-20261023--aggregate.csv').read_bytes() == (ROOT / 'data' / 'aggregate.csv').read_bytes(), 'Plot CSV differs from release CSV')
    plotted = json.loads((ROOT / 'plotting' / 'RESULTS.json').read_text(encoding='utf-8-sig'))
    plotted_index = {tuple(str(r[k]) for k in KEYS): r for r in plotted['aggregate']}
    require(set(plotted_index) == set(indexed), 'Plot aggregate key mismatch')
    for key, row in indexed.items():
        for field, value in row.items():
            if field in KEYS:
                require(value == str(plotted_index[key][field]), 'Plot key mismatch')
            else:
                same_number(value, plotted_index[key][field], 'plot/' + field)
    provenance = json.loads((ROOT / 'PROVENANCE.json').read_text(encoding='utf-8'))
    for item in provenance['inherited_files']:
        require(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], 'Inherited file mismatch')
    print(json.dumps({'status': 'PASS', 'manifest_files_checked': len(paths), 'runs': len(runs), 'aggregate_cells': len(aggregates), 'workload_counts': workload_counts, 'repetitions_per_cell': 3, 'aggregate_numeric_values_checked': aggregate_values_checked, 'comparison_rows': len(comparisons), 'comparison_numeric_values_checked': comparison_values_checked, 'final_query_summaries': len(risks), 'inherited_files_byte_preserved': len(provenance['inherited_files']), 'scope': 'Deposited file integrity and summary arithmetic; no native experiments or query bootstrap rerun'}, indent=2))

if __name__ == '__main__':
    main()
