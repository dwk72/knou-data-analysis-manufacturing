"""Proposed confirmation experiment for Nottingham activated-carbon research.

The design is a proposal, NOT experimental results. Its K/C target levels
are based on observed quartiles within the 49-sample MAST3RBoost cohort.
No row-level source data are published. Run from repo root:

    python carbon_materials_process_quality/03_confirmation_plan/design_experiment.py

The source v2 CSV is downloaded and verified using the existing analyze module.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from analyze import (  # noqa: E402
    KC,
    TEMP,
    fetch_source,
    parse_csv,
    verify_md5,
)

GROUP = "MAST3RBoost"
EXPECTED_N = 49
RANDOM_SEED = 20261106
FEEDSTOCKS = ("F-A", "F-B")
DAYS = ("D1", "D2")
LEVEL_NAMES = ("LOW", "CENTER", "HIGH")


def support_levels(df):
    """Get dose-ratio targets from research support, never by optimizing BET."""
    cohort = df.loc[df["source_group"] == GROUP]
    if len(cohort) != EXPECTED_N:
        raise ValueError("Cohort size changed; review the scientific design")
    if cohort[TEMP].nunique() != 1 or float(cohort[TEMP].iloc[0]) != 800:
        raise ValueError("Fixed-temperature assumption is no longer supported")
    vals = cohort[KC].dropna()
    if len(vals) != EXPECTED_N or not vals.between(0, float("inf")).all():
        raise ValueError("Invalid K/C source ratio")
    quantiles = [float(vals.quantile(q)) for q in (.25, .50, .75)]
    if not quantiles[0] < quantiles[1] < quantiles[2]:
        raise ValueError("Distinct K/C levels cannot be constructed")
    levels = {k: round(v, 3) for k, v in zip(LEVEL_NAMES, quantiles)}
    if len(set(levels.values())) != 3:
        raise ValueError("Rounded K/C targets are duplicated")
    return cohort, levels


def build_matrix(levels: dict, seed: int = RANDOM_SEED):
    """2 feedstock lots x 3 proposed K/C levels x 2 execution days = 12 preps."""
    if tuple(levels) != LEVEL_NAMES:
        raise ValueError("Unexpected level keys or ordering")
    rng = random.Random(seed)
    rows = []
    for day in DAYS:
        combos = [(lot, level) for lot in FEEDSTOCKS for level in LEVEL_NAMES]
        rng.shuffle(combos)
        for slot, (lot, level) in enumerate(combos, start=1):
            rows.append({
                "experiment_id": f"{day}-{slot:02d}",
                "planned_day": day,
                "randomized_order_in_day": slot,
                "feedstock_lot_placeholder": lot,
                "K_C_level": level,
                "K_C_target_dimensionless": f"{levels[level]:.3f}",
                "activation_temperature_target_C": "800",
                "dwell_time_target_hour": "1",
                "ramp_rate_target_C_min": "3",
                "porogen_indicator_target": "0",
                "compactivation_indicator_target": "0",
                "experiment_status": "PROPOSED_NOT_EXECUTED",
                "execution_authorization": "NO_GO_PENDING_FEASIBILITY_AND_SAFETY",
                "K_C_to_actual_dose_validated": "NO",
            })
    return rows


def entry_template(rows):
    """One result row per independent experimental preparation, not per BET run."""
    result = []
    for row in rows:
        result.append({
            "experiment_id": row["experiment_id"],
            "planned_day": row["planned_day"],
            "feedstock_lot": row["feedstock_lot_placeholder"],
            "K_C_level": row["K_C_level"],
            "K_C_target_dimensionless": row["K_C_target_dimensionless"],
            "K_C_actual_dimensionless": "",
            "actual_temperature_profile_file": "",
            "actual_dwell_time_hour": "",
            "actual_ramp_rate_C_min": "",
            "feedstock_COA_reference": "",
            "BET_measurement_1_m2_g": "",
            "BET_measurement_2_m2_g": "",
            "DR_pore_volume_cm3_g": "",
            "isolated_product_mass_g": "",
            "input_dry_precursor_mass_g": "",
            "residual_alkali_result_and_unit": "",
            "quality_measurement_method_revision": "",
            "deviation_or_issue": "",
            "run_status": "NOT_RUN",
        })
    return result


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("No experiment rows")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(df, output_dir: Path):
    cohort, levels = support_levels(df)
    matrix = build_matrix(levels)
    if len(matrix) != 12:
        raise AssertionError("Unexpected factorial design size")
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "DESIGN_MATRIX.csv", matrix)
    write_csv(output_dir / "MEASUREMENT_LOG_TEMPLATE.csv", entry_template(matrix))
    evidence = {
        "dataset": "University of Nottingham/Nanolayers activated carbon, Zenodo v2",
        "source": "https://zenodo.org/records/23311682",
        "source_cohort": GROUP,
        "source_cohort_n": int(len(cohort)),
        "source_temperature_unique_count": int(cohort[TEMP].nunique()),
        "source_temperature_C": 800,
        "source_k_c_observed_min": round(float(cohort[KC].min()), 3),
        "source_k_c_observed_max": round(float(cohort[KC].max()), 3),
        "source_k_c_quantiles": {
            "q25": round(float(cohort[KC].quantile(.25)), 5),
            "median": round(float(cohort[KC].quantile(.50)), 5),
            "q75": round(float(cohort[KC].quantile(.75)), 5),
        },
        "proposed_k_c_levels": levels,
        "preparation_runs": 12,
        "feedstock_lot_placeholder_count": 2,
        "independent_days": 2,
        "levels_count": 3,
        "intended_bet_technical_repeats_per_preparation": 2,
        "expected_bet_analytical_measurements_if_executed": 24,
        "random_seed": RANDOM_SEED,
        "stage": "NOT_EXECUTED_EXPERIMENT_PROPOSAL",
        "execution_authorization": "NO_GO_PENDING_FEASIBILITY_AND_SAFETY",
        "K_C_chemical_to_dose_mapping_verified": False,
        "experiment_power_calculated": False,
        "nominal_residual_degrees_of_freedom_under_fixed_day_lot_interaction_model": 5,
        "qualification": "Quartiles describe observed historical support; not optimized "
                         "recipe targets or independently validated control windows.",
    }
    (output_dir / "DESIGN_EVIDENCE.json").write_text(
        json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return evidence, matrix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, help="Unaltered original Zenodo v2 CSV")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
    )
    args = parser.parse_args()
    content = args.source.read_bytes() if args.source else fetch_source()
    verify_md5(content)
    df = parse_csv(content.decode("utf-8-sig"))
    evidence, rows = generate(df, args.output)
    print("Nottingham research cohort:", evidence["source_cohort_n"])
    print("Proposed K/C targets (not process recommendations):",
          evidence["proposed_k_c_levels"])
    print("Independent preparations proposed:", len(rows))
    print("Experiment execution authorization:", evidence["execution_authorization"])
    print("No experiments were performed and no quality measurements were invented.")


if __name__ == "__main__":
    main()
