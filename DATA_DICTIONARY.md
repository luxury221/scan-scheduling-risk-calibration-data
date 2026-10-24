# Data dictionary

CSV files are UTF-8 with a header row. Decimal points use `.`. Empty comparison fields mean not applicable, not zero; other deposited CSV cells must be nonempty. `tag` must be read as a string to preserve `01`.

## runs.csv

One row per process repetition. Group key: `(dataset, nlist, tag, workload, mode)`; `rep` distinguishes the three processes. Calibration workloads use 512 queries and k=100.

| Column | Definition |
| --- | --- |
| `active_seconds` | Active calibration wall time in seconds, including state construction/destruction, coarse ordering, scans, accounting, scheduling, caching, mapping, and sorting; excludes input loading, warmup, and output. |
| `base_load_seconds` | Seconds spent reading the base vector collection in a fresh-label run; zero where this stage is not executed. |
| `cache_capacity_bytes` | Reported allocated observation/curve cache capacity in bytes; not total process memory. |
| `dataset` | Benchmark identifier: sift or glove. |
| `index_load_seconds` | Seconds spent loading the prebuilt index. |
| `initial_full_scan_seconds` | Initial full observation-generation time reported by complete/batch, in seconds; zero for methods without this stage. Not separately aggregated in aggregate.csv. |
| `joint_seconds` | Direct wall time from before index/input loading through calibration-state destruction, including warmup and fresh labels/certificates when requested; excludes index construction and final output. |
| `label_compute_seconds` | Seconds spent computing fresh exact labels and certificates; zero when precomputed inputs are used. |
| `label_distance_evaluations` | Count of exact distance evaluations for fresh-label generation; zero when no fresh-label generation is requested. |
| `mode` | Executor identifier: complete, batch, merge, bits, value, or frontier. |
| `nlist` | Number of inverted lists in the index: 256, 1024, or 4096. |
| `peak_rss_mib` | Maximum process resident set size in MiB, converted from the process timing record. |
| `process_wall_seconds` | External job-process elapsed time in seconds; its boundary differs from the internal active and joint timers. |
| `query_label_load_seconds` | Seconds for query and, when applicable, precomputed label/certificate loading and checking. In fresh runs this stage loads queries before separate base reading and exact labeling. |
| `rep` | Process repetition identifier, 0, 1, or 2; each method/workload cell has exactly these three observations. |
| `replayed_prefixes` | Count of cached logical prefix observations reprocessed by the scheduler; does not count new physical vector scans. |
| `scanned_lists` | Sum of physical lists scanned across calibration queries, including lookahead and crossing lists. |
| `scanned_vectors` | Sum of physical vectors scanned across calibration queries, including lookahead and crossing lists. |
| `tag` | String code for the single-target gamma setting: "01" means 0.01 and "0" means 0. Preserve leading zero. Request sequences are defined by workload. |
| `warmup_seconds` | Seconds spent in the initial warmup query, outside active calibration time but inside joint time. |
| `workload` | single: one target; alpha4: four risk targets; mixed16: 16 requests across four gammas; fresh: one target with fresh exact labels/certificates. See EXPERIMENT_CONFIGURATION.json. |

## aggregate.csv

One row per grouping key above. Key columns have the same definitions as in runs.csv. For each of the following fields, the unsuffixed value is the median of the three repetitions, `_min` is their minimum, and `_max` is their maximum:

`active_seconds`, `joint_seconds`, `index_load_seconds`, `query_label_load_seconds`, `base_load_seconds`, `label_compute_seconds`, `warmup_seconds`, `peak_rss_mib`, `process_wall_seconds`.

`scanned_vectors`, `scanned_lists`, `replayed_prefixes`, `cache_capacity_bytes`, and `label_distance_evaluations` must be identical across repetitions and are copied once. No `rep` or `initial_full_scan_seconds` column is included. Do not add component medians to construct joint time.

## comparisons.csv

One row per `(dataset, nlist, tag, workload)` containing frontier. Those four key columns retain their runs.csv definitions.

| Column | Definition |
| --- | --- |
| `best_control` | Control other than frontier with the lowest observed median active time within this setting; selected descriptively. |
| `best_control_active` | Selected control median active time, seconds. |
| `best_control_over_frontier` | best_control_active / frontier_active; values above 1 favor frontier. |
| `best_control_vectors` | Physical vector scan count of the selected fastest control. |
| `complete_joint` | Complete median joint time in seconds, present only for fresh workload. |
| `frontier_active` | Frontier median active time, seconds. |
| `frontier_joint` | Frontier median joint time in seconds, present only for fresh workload. |
| `frontier_replayed_prefixes` | Frontier cached logical prefix replay count. |
| `frontier_time_reduction_fraction` | 1 - frontier_active / best_control_active; multiply by 100 for percent reduction. Negative means frontier is slower. |
| `frontier_vectors` | Frontier physical vector scan count. |
| `joint_complete_over_frontier` | Complete median joint time / frontier median joint time, only for fresh workload. |
| `joint_range_separated` | True exactly when frontier maximum joint time is below the complete minimum; only for fresh workload. Not a significance test. |
| `ordinary_cache_control` | Faster observed median active time among the available complete and batch controls. |
| `ordinary_cache_over_frontier` | Ordinary full-cache control median active time / frontier median active time. |
| `ordinary_cache_vectors` | Physical vector count for the selected ordinary full-cache control. |
| `range_separated` | True exactly when frontier maximum active time is below the selected best control minimum active time. This flag is directional and is not a significance test. |

## final-query-risk.csv

One row per `(dataset, nlist, gamma)` on the already-used final-query set. These query-level summaries are separate from the three-process timing ranges.

| Column | Definition |
| --- | --- |
| `dataset` | glove in all four deposited final-query summaries. |
| `nlist` | Number of inverted lists. |
| `gamma` | Score mapping parameter. |
| `nq` | Number of evaluated final queries, 8,976 in every row. |
| `k` | Number of exact reference neighbors, 100. |
| `alpha` | Risk target as a fraction, 0.05. |
| `threshold_bits` | Unsigned integer representation of the selected IEEE-754 float32 threshold bits, not the numeric threshold itself. |
| `empirical_mean_fnr` | Mean query false-negative rate on the already-used final-query set. |
| `mean_recall` | Mean query recall; equals 1 - empirical_mean_fnr. |
| `recall_p05` | Fifth percentile of per-query recall. |
| `recall_median` | Median per-query recall. |
| `recall_min` | Minimum per-query recall. |
| `empty_queries` | Number of queries returning no candidates. |
| `strict_label_boundary_queries` | Number of queries whose exact k-th and (k+1)-th neighbor distances have a strict gap. |
| `tied_label_boundary_queries` | Number of queries whose exact k-th and (k+1)-th neighbor distances tie. |
| `scanned_vectors` | Total deployed physical vector scans across the final queries. |
| `mean_scanned_fraction` | Mean fraction of the base collection physically scanned per query. |
| `mean_returned_lists` | Mean number of accepted lists per deployed query. |
| `mean_scanned_lists` | Mean number of physically scanned lists, including crossing/lookahead work. |
| `fnr_query_bootstrap95_low` | Archived lower endpoint of the 95% query-bootstrap interval for mean false-negative rate, conditional on the fixed calibration split. |
| `fnr_query_bootstrap95_high` | Archived upper endpoint of that conditional query-bootstrap interval. |
