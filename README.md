# Experimental Records for Scan Scheduling for Exact Risk Calibration in Approximate Nearest Neighbor Search

Version **1.0.0**. This data deposit accompanies the manuscript **Scan Scheduling for Exact Risk Calibration in Approximate Nearest Neighbor Search**, by Yaoyang Chen, Yicheng Zhao, Xiangjiang Zhou, and Jiachen Li. This deposit does not imply that the manuscript has been accepted or published.

**Versioned download and citation link:** https://github.com/luxury221/scan-scheduling-risk-calibration-data/releases/tag/v1.0.0

## Contents

| File or directory | Contents |
| --- | --- |
| `data/runs.csv` | 228 existing process-level timing records: 144 single-target, 72 multi-request, and 12 fresh-label runs |
| `data/aggregate.csv` | 76 method/workload cells, with three process repetitions per cell |
| `data/comparisons.csv` | 14 descriptive comparisons against frontier |
| `data/final-query-risk.csv` | Four summaries of evaluations on the 8,976 final GloVe queries |
| `DATA_DICTIONARY.md` | Column definitions, units, grouping keys, and missing-value conventions |
| `EXPERIMENT_CONFIGURATION.json` | Methods, request sequences, platform, and measurement boundaries |
| `plotting/` | Existing plotting inputs and scripts |
| `validation/` | Archived validation summaries from the completed study |
| `scripts/verify_records.py` | Standalone verification of file hashes and published summary arithmetic |
| `PROVENANCE.json`, `FILE_MANIFEST.json` | Source-byte preservation and SHA-256 checksums |
| `CITATION.cff` | Author and dataset citation metadata |

The CSVs and inherited plotting/validation files are copied without changing their bytes from the completed submission supplement. No new performance experiment, query bootstrap, or tuning was carried out to prepare this deposit. The dataset type is **original experimental records**: SIFT and GloVe themselves are external reference benchmarks and are not redistributed here.

## Verify the records

Python 3.9 or later is sufficient; no third-party Python package is needed for verification. From the repository root:

```console
python -B scripts/verify_records.py
```

The verifier checks the 228/76 record counts, all three repetitions per cell, every reported aggregate median/minimum/maximum, deterministic work counters, comparison arithmetic, and correspondence between the final-risk CSV and the archived risk summary. It also checks all manifest file hashes. This verifies the deposited summaries; it does not rerun the native ANN experiments or independently re-establish archived per-query checks.

## Recreate descriptive timing plots

The plotting scripts require NumPy and Matplotlib. Install them in an environment of your choice, then run from the repository root:

```console
python -B -c "from pathlib import Path; [Path(p).mkdir(parents=True, exist_ok=True) for p in ('plotting/figures', 'plotting/tmp', 'plotting/cache/matplotlib')]"
python -B plotting/make_figures.py
python -B plotting/plot_results_archived.py
```

The first script writes the main and gamma-zero single-target panels under `plotting/figures/`. The archived script writes single-target, multi-request, and fresh-label plots under `plotting/`. `make_concept_figure.py` draws illustrative example streams rather than experimental measurements. Generated figure file bytes are not promised to match the manuscript PDF across library versions.

## Interpretation and scope

Timing medians and observed minimum-to-maximum ranges summarize **three separate process observations per cell**. They are not confidence intervals or significance tests. The bootstrap intervals in `final-query-risk.csv` instead concern query resampling conditional on one fixed calibration split; they are not a test of a new statistical risk guarantee.

The 8,976 final GloVe queries have already been evaluated. They must not be described as untouched data or used for subsequent tuning. Deployment agreement refers to identifier-distance pairs after sorting by identifier and to per-query physical work counts, rather than to the original API return order. Historical validation filenames and keys are retained as archived provenance, not as new claims of an unused test split.

This release supports inspection, recomputation of timing summaries, and plotting. It does **not** contain the SIFT/GloVe vector collections, prebuilt indexes, label/certificate binaries, the native ConANN/Faiss dependency environment, native implementation drivers, or full historical per-query arrays. Native drivers remain supplied separately in the manuscript supplementary materials. The native upstream revision used in the study is `aa76fbc2e2aaec822ddca525baf4916da46a653b`.

The study evaluates execution of a fixed exact risk-calibration rule. Its measurements include counterexamples, multi-target reuse costs, and fresh-label preparation boundaries; they do not establish a new risk guarantee or universal speedup.

## Authors and citation

All authors are affiliated with the School of Mathematics and Statistics, Chongqing University of Posts and Telecommunications, Chongqing, China. Corresponding author: **Yaoyang Chen**, 2024213800@stu.cqupt.edu.cn. Use `CITATION.cff` or cite this dataset title, the four authors, version 1.0.0, and the versioned release URL above. This GitHub release has **no registered DOI**.

## Rights and assistance

See `RIGHTS.md`. Public sharing has been approved by the authors; no separate data or software reuse license has been selected. Third-party benchmark and dependency rights remain with their respective holders.

OpenAI Codex assisted with implementation, experiment organization, plotting code, and release preparation. Exact model/runtime identifiers are unavailable in the accompanying research records. The authors reported completing their review of the code, references, experimental results, and manuscript text and approved public sharing of the supplied code and records.
