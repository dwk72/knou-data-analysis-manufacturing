"""SQLite manufacturing extension reproducibility checks."""

from __future__ import annotations

import csv
import math
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "07_manufacturing_extension"
SQL_PROJECT = PROJECT / "03_sql_analysis"
PUBLISHED_OUTPUT = SQL_PROJECT / "output"

OUTPUT_FILES = (
    "01_join_sample.csv",
    "02_equipment_kpi.csv",
    "03_material_lot_kpi.csv",
    "04_before_after_drift.csv",
    "05_rolling_40_ng_rate.csv",
    "06_equipment_energy_rank.csv",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def numeric_equal(left: str, right: str) -> bool:
    if left == right:
        return True
    if not left or not right:
        return False

    try:
        a = float(left)
        b = float(right)
    except ValueError:
        return False

    return math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-11)


class ManufacturingSqlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="knou_mfg_sql_")
        cls.temp_root = Path(cls.temp_dir.name)
        cls.database = cls.temp_root / "manufacturing.db"
        cls.output_dir = cls.temp_root / "output"

        completed = subprocess.run(
            [
                sys.executable,
                str(SQL_PROJECT / "build_and_query.py"),
                "--database",
                str(cls.database),
                "--output-dir",
                str(cls.output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        if completed.returncode:
            raise RuntimeError(
                "SQL analysis failed\n"
                + completed.stdout
                + "\n"
                + completed.stderr
            )

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temp_dir"):
            cls.temp_dir.cleanup()

    def assert_same_csv(self, expected: Path, actual: Path) -> None:
        header_e, rows_e = read_csv(expected)
        header_a, rows_a = read_csv(actual)

        self.assertEqual(header_e, header_a)
        self.assertEqual(len(rows_e), len(rows_a))

        for row_e, row_a in zip(rows_e, rows_a):
            for field in header_e:
                self.assertTrue(
                    numeric_equal(row_e[field], row_a[field]),
                    f"{expected.name} / {field}: "
                    f"{row_e[field]!r} != {row_a[field]!r}",
                )

    def test_database_integrity(self) -> None:
        connection = sqlite3.connect(self.database)

        try:
            for table_name in (
                "batch_master",
                "material",
                "process_condition",
                "quality_result",
            ):
                count = connection.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()[0]
                self.assertEqual(count, 800)

            self.assertEqual(
                connection.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall(),
                [],
            )
        finally:
            connection.close()

    def test_published_sql_outputs_recreated(self) -> None:
        for file_name in OUTPUT_FILES:
            with self.subTest(file=file_name):
                self.assert_same_csv(
                    PUBLISHED_OUTPUT / file_name,
                    self.output_dir / file_name,
                )

    def test_window_result_tail(self) -> None:
        _, rows = read_csv(
            self.output_dir / "05_rolling_40_ng_rate.csv"
        )
        self.assertEqual(len(rows), 800)

        last = rows[-1]
        self.assertEqual(last["batch_id"], "B0800")
        self.assertEqual(int(last["window_batches"]), 40)
        self.assertAlmostEqual(
            float(last["rolling_40_ng_rate_pct"]),
            40.00,
            places=2,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
