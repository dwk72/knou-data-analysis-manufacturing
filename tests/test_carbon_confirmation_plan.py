"""Validation for a PROPOSED, not performed, activated-carbon trial matrix."""
from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "carbon_materials_process_quality"
sys.path.insert(0, str(ROOT))
from analyze import fetch_source, parse_csv  # noqa: E402
sys.path.insert(0, str(ROOT / "03_confirmation_plan"))
from design_experiment import (  # noqa: E402
    DAYS,
    FEEDSTOCKS,
    LEVEL_NAMES,
    build_matrix,
    entry_template,
    generate,
    support_levels,
)


class ConfirmationPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = parse_csv(fetch_source().decode("utf-8-sig"))

    def test_K_C_level_quantiles_are_supported(self):
        cohort, levels = support_levels(self.frame)
        self.assertEqual(len(cohort), 49)
        self.assertEqual(levels, {"LOW": 2.946, "CENTER": 3.322, "HIGH": 3.764})
        for v in levels.values():
            self.assertGreaterEqual(v, float(cohort["[input] K/C"].min()))
            self.assertLessEqual(v, float(cohort["[input] K/C"].max()))

    def test_design_balanced_for_each_day_and_feedstock(self):
        _, levels = support_levels(self.frame)
        plan = build_matrix(levels)
        self.assertEqual(len(plan), 12)
        self.assertEqual(len(set(r["experiment_id"] for r in plan)), 12)
        for day in DAYS:
            rows = [r for r in plan if r["planned_day"] == day]
            self.assertEqual(len(rows), 6)
            self.assertEqual(set(r["randomized_order_in_day"] for r in rows), set(range(1, 7)))
            self.assertEqual(
                set((r["feedstock_lot_placeholder"], r["K_C_level"]) for r in rows),
                set((feed, level) for feed in FEEDSTOCKS for level in LEVEL_NAMES),
            )
        self.assertEqual(
            Counter((r["feedstock_lot_placeholder"], r["K_C_level"]) for r in plan),
            Counter({(feed, level): 2 for feed in FEEDSTOCKS for level in LEVEL_NAMES}),
        )
        self.assertTrue(all(r["experiment_status"] == "PROPOSED_NOT_EXECUTED" for r in plan))

    def test_no_fabricated_results_in_template(self):
        _, levels = support_levels(self.frame)
        rows = entry_template(build_matrix(levels))
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(r["run_status"] == "NOT_RUN" for r in rows))
        self.assertTrue(all(r["BET_measurement_1_m2_g"] == "" for r in rows))
        self.assertTrue(all(r["BET_measurement_2_m2_g"] == "" for r in rows))
        self.assertTrue(all(r["K_C_actual_dimensionless"] == "" for r in rows))

    def test_output_artifacts_and_source_summary(self):
        with tempfile.TemporaryDirectory() as t:
            output = Path(t)
            evidence, plan = generate(self.frame, output)
            self.assertEqual(evidence["preparation_runs"], 12)
            self.assertEqual(evidence["source_cohort_n"], 49)
            self.assertEqual(evidence["expected_bet_analytical_measurements_if_executed"], 24)
            self.assertEqual(evidence["stage"], "NOT_EXECUTED_EXPERIMENT_PROPOSAL")
            data = json.loads((output / "DESIGN_EVIDENCE.json").read_text("utf-8"))
            self.assertEqual(data["proposed_k_c_levels"], {"LOW": 2.946, "CENTER": 3.322, "HIGH": 3.764})
            with (output / "DESIGN_MATRIX.csv").open("r", encoding="utf-8") as file:
                self.assertEqual(len(list(csv.DictReader(file))), 12)
            with (output / "MEASUREMENT_LOG_TEMPLATE.csv").open("r", encoding="utf-8") as file:
                self.assertEqual(len(list(csv.DictReader(file))), 12)
            self.assertEqual(len(plan), 12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
