"""Tests for cohort-aware exploration of public Nottingham activated-carbon data."""
from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "carbon_materials_process_quality"
sys.path.insert(0, str(BASE))
from analyze import BET, TEMP, fetch_source, parse_csv  # noqa: E402
sys.path.insert(0, str(BASE / "02_process_relationships"))
from analyze_relationships import (  # noqa: E402
    LIT_VARS, PROJECT_VARS, cohort_inputs, fit_ols, get_results,
)


class CarbonProcessRelationshipsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frame = parse_csv(fetch_source().decode("utf-8-sig"))

    def test_cohorts_are_not_mixed(self):
        literature = cohort_inputs(self.frame, "Literature")
        project = cohort_inputs(self.frame, "MAST3RBoost")
        self.assertEqual(len(literature), 176)
        self.assertEqual(len(project), 49)
        self.assertEqual(project[TEMP].nunique(), 1)
        self.assertEqual(project[TEMP].iloc[0], 800)

    def test_primary_literature_temperature_support(self):
        core = cohort_inputs(self.frame, "Literature", common_bands=True)
        self.assertEqual(len(core), 162)
        self.assertEqual(set(core[TEMP].unique()), {600, 700, 800})
        self.assertEqual((core[TEMP] == 600).sum(), 43)
        self.assertEqual((core[TEMP] == 700).sum(), 43)
        self.assertEqual((core[TEMP] == 800).sum(), 76)
        # Preserve the unusual observation, don't silently turn it to 800.
        self.assertEqual((self.frame[TEMP] == 80).sum(), 1)

    def test_ols_design_is_estimable_but_not_causal(self):
        lit = fit_ols(cohort_inputs(self.frame, "Literature", True), LIT_VARS)
        proj = fit_ols(cohort_inputs(self.frame, "MAST3RBoost"), PROJECT_VARS)
        self.assertEqual(lit["rank"], lit["parameters"])
        self.assertEqual(proj["rank"], proj["parameters"])
        for result in (lit, proj):
            self.assertTrue(math.isfinite(result["r2_in_sample"]))
            self.assertGreaterEqual(result["r2_in_sample"], 0)
            self.assertLessEqual(result["r2_in_sample"], 1)

    def test_derived_outputs_are_structured(self):
        output = BASE / "02_process_relationships" / "results"
        with (output / "summary.json").open(encoding="utf-8") as stream:
            result = json.load(stream)
        self.assertEqual(result["literature"]["primary_n"], 162)
        self.assertEqual(result["MAST3RBoost"]["n"], 49)
        self.assertFalse(result["MAST3RBoost"]["temperature_effect_estimable"])
        self.assertGreater(
            result["literature"]["bootstrap_95"]["valid_repetitions"], 480
        )
        self.assertGreater(
            result["MAST3RBoost"]["bootstrap_95"]["valid_repetitions"], 480
        )
        self.assertTrue((output / "REPORT.md").is_file())
        self.assertTrue((output / "figures" / "literature_temperature_bet.svg").is_file())
        self.assertTrue((output / "figures" / "fixed800_composition_bet.svg").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
