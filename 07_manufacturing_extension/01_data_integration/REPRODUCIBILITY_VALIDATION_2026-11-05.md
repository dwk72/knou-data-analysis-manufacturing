# Manufacturing data pipeline: Reproducibility Validation

- Date: 2026-11-05 (KST)
- Result: **PASS**
- Verified GitHub Actions run: https://github.com/dwk72/knou-data-analysis-manufacturing/actions/runs/41981724270
- Tested commit: `31f8da56ce8bc4c196c02b5d015c977a88176489`
- Runtime: GitHub Actions `ubuntu-latest`, Python 3.11, `pandas==2.2.3`
- Test command: `python -m unittest discover -s tests -p "test_manufacturing_reproducibility.py" -v`
- Result: `Ran 4 tests ... OK`

## Reproduction procedure

The test uses a clean temporary directory and copies the two published scripts without editing them:

1. `generate_synthetic_data.py` regenerates all four original synthetic CSVs.
2. `01_data_integration/integrate_and_validate.py` rebuilds the integrated dataset and quality-check reports.
3. The test compares generated CSVs against the eight published files, including column names, row ordering, and every field.
4. All nine published quality-summary metrics are asserted independently.
5. Batch-ID uniqueness and the expected 800 integrated / 776 complete-case rows are checked.

Comparisons are exact for non-numeric cells. Numeric cells allow only floating-point tolerance `rel_tol=1e-11, abs_tol=1e-11` to accommodate harmless output-format differences. This is **semantic CSV equivalence**, not byte-for-byte checksum equality.

## Results

| Check | Result |
|---|---|
| Four source tables | 800 rows each, 0 duplicated IDs, all regenerated |
| Generated-source CSV comparison | PASS (4 files) |
| Generated-output CSV comparison | PASS (4 files) |
| Source variable count | 19 |
| Integrated records | 800 |
| Missing cells | 25 |
| Rows with missing values | 24 |
| Complete cases | 776 |
| Rows with IQR outlier candidates | 61 |
| Rows flagged REVIEW | 83 |
| Quality outcomes | OK 650, NG 150 |

## Defect found and repaired

The existing `data_quality_summary.csv` stored 9 metrics, while the previously committed `integrate_and_validate.py` generated only 6. On 2026-11-05, the Python script was adjusted to write all 9 documented metrics, including original source-column count and OK/NG counts, with descriptions aligned to the published summary. The clean GitHub Actions reproduction subsequently passed.

## Repeat locally

```bash
python -m pip install "pandas==2.2.3"
python -m unittest discover -s tests -p "test_manufacturing_reproducibility.py" -v
```

See [the test source](../../tests/test_manufacturing_reproducibility.py) and [GitHub Actions workflow](../../.github/workflows/manufacturing_reproducibility.yml).

## Interpretation and limits

- The test verifies **synthetic data-generation and data-quality integration reproducibility**, not validation of a real chemical process.
- The IQR flag denotes a review candidate, not a confirmed manufacturing anomaly or quality defect.
- It does not verify planned but unimplemented EDA, PCA, time-series quality modeling, or plant improvement claims.
- The report is limited to the indicated Python/pandas CI environment. Other platform/library versions were not tested here.
