"""End-to-end reproducibility check of the synthetic manufacturing batch example.

Runs *the repository's own* generator and integration script in a clean,
isolated temporary directory. Compares each published CSV against generated
CSV cell by cell, accepting only insignificant numeric formatting differences.
"""

from __future__ import annotations

import csv
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "07_manufacturing_extension"
SOURCE_FILES = (
    "batch_master.csv",
    "material.csv",
    "process_condition.csv",
    "quality_result.csv",
)
OUTPUT_FILES = (
    "integrated_master.csv",
    "analysis_ready_complete_cases.csv",
    "outlier_summary.csv",
    "data_quality_summary.csv",
)
EXPECTED_METRICS = {
    "integrated_rows": 800,
    "integrated_source_columns": 19,
    "missing_cells": 25,
    "rows_with_missing": 24,
    "complete_case_rows": 776,
    "rows_with_iqr_outlier": 61,
    "rows_flagged_for_review": 83,
    "quality_OK": 650,
    "quality_NG": 150,
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def numeric_equal(left: str, right: str) -> bool:
    if left == right:
        return True
    if not left or not right:
        return False
    try:
        a, b = float(left), float(right)
    except ValueError:
        return False
    return math.isfinite(a) and math.isfinite(b) and math.isclose(
        a, b, rel_tol=1e-11, abs_tol=1e-11
    )


class ReproducibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="knou_mfg_repro_")
        cls.root = Path(cls.temp_dir.name) / "07_manufacturing_extension"
        (cls.root / "01_data_integration").mkdir(parents=True)
        shutil.copy2(PROJECT / "generate_synthetic_data.py", cls.root / "generate_synthetic_data.py")
        shutil.copy2(
            PROJECT / "01_data_integration" / "integrate_and_validate.py",
            cls.root / "01_data_integration" / "integrate_and_validate.py",
        )
        commands = (
            [sys.executable, str(cls.root / "generate_synthetic_data.py")],
            [sys.executable, str(cls.root / "01_data_integration" / "integrate_and_validate.py")],
        )
        cls.execution = []
        for cmd in commands:
            completed = subprocess.run(
                cmd, cwd=cls.root, text=True, capture_output=True, check=False
            )
            cls.execution.append(completed)
            if completed.returncode:
                raise RuntimeError(
                    "Pipeline stage failed: " + " ".join(cmd)
                    + "\nSTDOUT:\n" + completed.stdout
                    + "\nSTDERR:\n" + completed.stderr
                )

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temp_dir"):
            cls.temp_dir.cleanup()

    def assert_same_csv(self, expected: Path, actual: Path) -> None:
        header_e, records_e = read_csv(expected)
        header_a, records_a = read_csv(actual)
        self.assertEqual(header_e, header_a, f"Column schema mismatch: {expected.name}")
        self.assertEqual(len(records_e), len(records_a), f"Row count mismatch: {expected.name}")
        for index, (row_e, row_a) in enumerate(zip(records_e, records_a), start=2):
            for field in header_e:
                self.assertTrue(
                    numeric_equal(row_e[field], row_a[field]),
                    f"{expected.name}, CSV line {index}, field {field}: "
                    f"expected {row_e[field]!r}, generated {row_a[field]!r}",
                )

    def test_source_csvs_recreated(self) -> None:
        for file_name in SOURCE_FILES:
            with self.subTest(file=file_name):
                self.assert_same_csv(
                    PROJECT / "data" / file_name,
                    self.root / "data" / file_name,
                )

    def test_output_csvs_recreated(self) -> None:
        for file_name in OUTPUT_FILES:
            with self.subTest(file=file_name):
                self.assert_same_csv(
                    PROJECT / "01_data_integration" / "output" / file_name,
                    self.root / "01_data_integration" / "output" / file_name,
                )

    def test_expected_quality_summary_metrics(self) -> None:
        _, rows = read_csv(self.root / "01_data_integration" / "output" / "data_quality_summary.csv")
        reported = {row["metric"]: int(row["value"]) for row in rows}
        self.assertEqual(reported, EXPECTED_METRICS)

    def test_unique_ids_and_no_row_loss(self) -> None:
        source = self.root / "data"
        for file_name in SOURCE_FILES:
            _, rows = read_csv(source / file_name)
            ids = [row["batch_id"] for row in rows]
            self.assertEqual(len(ids), 800)
            self.assertEqual(len(ids), len(set(ids)))
        _, integrated = read_csv(self.root / "01_data_integration" / "output" / "integrated_master.csv")
        self.assertEqual(len(integrated), 800)
        _, complete = read_csv(self.root / "01_data_integration" / "output" / "analysis_ready_complete_cases.csv")
        self.assertEqual(len(complete), 776)


if __name__ == "__main__":
    unittest.main(verbosity=2)
