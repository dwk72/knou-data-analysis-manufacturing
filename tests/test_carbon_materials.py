"""Regression tests for the independent carbon-materials research dataset module.

The original publisher's source is accessed at runtime; raw CSV is not committed.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "carbon_materials_process_quality"
sys.path.insert(0, str(HERE))
import analyze  # noqa: E402


class CarbonMaterialsTest(unittest.TestCase):
    def test_source_metadata_and_license(self):
        self.assertEqual(analyze.EXPECTED_MD5, "0e38bd5c6a66dc8ff62f5831a90b55b0")
        self.assertIn("23311682", analyze.RECORD_URL)

    def test_md5_rejects_wrong_data(self):
        with self.assertRaises(ValueError):
            analyze.verify_md5(b"not-the-publisher-file")

    def test_schema_and_row_grain(self):
        content = analyze.fetch_source()
        analyze.verify_md5(content)
        frame = analyze.parse_csv(content.decode("utf-8-sig"))
        self.assertEqual(len(frame), 237)
        self.assertEqual(frame["ID"].nunique(), 237)
        self.assertEqual(len(frame.columns), 35)  # 34 original + cohort
        self.assertEqual(frame["source_group"].value_counts()["Literature"], 188)
        self.assertEqual(frame["source_group"].value_counts()["MAST3RBoost"], 49)

    def test_coverage_and_aggregate_outputs(self):
        content = analyze.fetch_source()
        frame = analyze.parse_csv(content.decode("utf-8-sig"))
        summary = analyze.profile(frame)
        self.assertEqual(summary["cohorts"]["Literature"]["bet_observed"], 176)
        self.assertEqual(summary["cohorts"]["MAST3RBoost"]["bet_observed"], 49)
        self.assertEqual(sum(x["bet_observed"] for x in summary["cohorts"].values()), 225)
        self.assertEqual(summary["cohorts"]["Literature"]["coverage"]["H2_uptake"], 0)
        self.assertEqual(summary["cohorts"]["MAST3RBoost"]["coverage"]["H2_uptake"], 48)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            analyze.plot(frame, out / "figures")
            self.assertTrue((out / "figures" / "temperature_vs_bet.svg").is_file())
            self.assertTrue((out / "figures" / "coverage_by_cohort.svg").is_file())
            self.assertIn("활성탄 제조조건", analyze.report(summary))
            (out / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            self.assertEqual(json.loads((out / "summary.json").read_text())["samples"], 237)


if __name__ == "__main__":
    unittest.main(verbosity=2)
