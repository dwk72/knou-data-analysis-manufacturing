"""Cohort-aware exploratory relationships in activated-carbon manufacturing research.

Original source: Nottingham/Nanolayers, Zenodo v2, DOI 10.5281/zenodo.23311682.
This analysis deliberately does not publish row-level source data, assert
causality, or claim an industrial operating optimum.

Design (prespecified):
- Literature (188 samples): show observed BET by activation-temperature
  strata; exploratory adjusted OLS only on common 600/700/800 °C bands.
- MAST3RBoost (49 samples): all 800 °C, so there is NO identifiable
  temperature effect. Explore K/C, O/C and N/C at fixed reported T.
- Report descriptive, adjusted, bootstrap and repeated-CV evidence separately.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyze import BET, TEMP, KC, fetch_source, parse_csv, verify_md5  # noqa: E402

O_C = "[input] O/C"
N_C = "[input] N/C"
POROGEN = "[input] Porogen"
CORE_TEMPS = (600.0, 700.0, 800.0)
DISPLAY_TEMPS = (600.0, 700.0, 800.0, 900.0)
LIT_VARS = ("temp_per_100C", "K_C", "O_C", "N_C", "Porogen")
PROJECT_VARS = ("K_C", "O_C", "N_C")
LABELS = {
    "temp_per_100C": "Temperature (+100 °C)",
    "K_C": "K/C ratio (+1)",
    "O_C": "O/C ratio (+1)",
    "N_C": "N/C ratio (+1)",
    "Porogen": "Porogen (1 vs 0)",
}


def cohort_inputs(df: pd.DataFrame, group: str, common_bands: bool = False):
    subset = df.loc[df["source_group"] == group].copy()
    if common_bands:
        subset = subset.loc[subset[TEMP].isin(CORE_TEMPS)]
    subset = subset.loc[subset[BET].notna()].copy()
    subset["temp_per_100C"] = (subset[TEMP] - 600.0) / 100.0
    subset["K_C"] = subset[KC]
    subset["O_C"] = subset[O_C]
    subset["N_C"] = subset[N_C]
    subset["Porogen"] = subset[POROGEN]
    return subset


def pearson_or_none(frame: pd.DataFrame, x: str) -> float | None:
    valid = frame[[x, BET]].dropna()
    if len(valid) < 3 or valid[x].nunique() < 2 or valid[BET].nunique() < 2:
        return None
    return float(valid[x].corr(valid[BET]))


def fit_ols(frame: pd.DataFrame, predictors: tuple[str, ...]) -> dict:
    clean = frame[[BET, *predictors]].dropna()
    n, p = len(clean), len(predictors) + 1
    if n < max(p + 4, 12):
        raise ValueError("Insufficient independent sample rows for specified fit")
    X = np.column_stack([np.ones(n), clean[list(predictors)].to_numpy(float)])
    y = clean[BET].to_numpy(float)
    rank = int(np.linalg.matrix_rank(X))
    if rank < p:
        raise ValueError(f"Design matrix rank deficient: {rank}/{p}")
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    pred = X @ coef
    rss = float(((y - pred) ** 2).sum())
    tss = float(((y - y.mean()) ** 2).sum())
    # Condition number on standardized input columns, not arbitrary units.
    xs = X[:, 1:]
    scales = xs.std(axis=0)
    if np.any(scales <= 0):
        raise ValueError("A prespecified predictor has no observed variation")
    z = (xs - xs.mean(axis=0)) / scales
    condition = float(np.linalg.cond(np.column_stack([np.ones(n), z])))
    return {
        "n": n,
        "rank": rank,
        "parameters": p,
        "predictors": list(predictors),
        "coefficients": {name: round(float(v), 4)
                         for name, v in zip(("intercept", *predictors), coef)},
        "r2_in_sample": round(1 - rss / tss, 4),
        "mae_in_sample": round(float(np.abs(y - pred).mean()), 2),
        "standardized_condition_number": round(condition, 2),
    }


def bootstrap_intervals(
    frame: pd.DataFrame,
    predictors: tuple[str, ...],
    n_rep: int = 600,
    seed: int = 20261106,
) -> dict:
    clean = frame[[BET, *predictors]].dropna()
    x = np.column_stack([np.ones(len(clean)), clean[list(predictors)].to_numpy(float)])
    y = clean[BET].to_numpy(float)
    rng = np.random.default_rng(seed)
    coefs = []
    for _ in range(n_rep):
        ids = rng.integers(0, len(clean), size=len(clean))
        xi = x[ids]
        if np.linalg.matrix_rank(xi) < x.shape[1]:
            continue
        coefs.append(np.linalg.lstsq(xi, y[ids], rcond=None)[0])
    if len(coefs) < int(n_rep * .8):
        raise ValueError("Too many rank-deficient bootstrap replicates")
    estimates = np.asarray(coefs)
    names = ("intercept", *predictors)
    return {
        "method": "pairs bootstrap, 95% percentile interval; observational association only",
        "requested_repetitions": n_rep,
        "valid_repetitions": int(len(coefs)),
        "intervals": {
            name: [round(float(v), 4) for v in np.quantile(estimates[:, i], [.025, .975])]
            for i, name in enumerate(names)
        },
    }


def repeated_cv(
    frame: pd.DataFrame,
    predictors: tuple[str, ...],
    n_rep: int = 15,
    folds: int = 5,
    seed: int = 1042,
) -> dict:
    clean = frame[[BET, *predictors]].dropna()
    X = np.column_stack([np.ones(len(clean)), clean[list(predictors)].to_numpy(float)])
    y = clean[BET].to_numpy(float)
    if len(y) < folds * 3:
        raise ValueError("Too few observations for CV")
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(n_rep):
        fold_indices = np.array_split(rng.permutation(len(y)), folds)
        predicted = np.empty(len(y), dtype=float)
        baseline = np.empty(len(y), dtype=float)
        for valid in fold_indices:
            train_mask = np.ones(len(y), dtype=bool)
            train_mask[valid] = False
            x_train, y_train = X[train_mask], y[train_mask]
            if np.linalg.matrix_rank(x_train) < X.shape[1]:
                raise ValueError("CV fold design is rank deficient")
            beta = np.linalg.lstsq(x_train, y_train, rcond=None)[0]
            predicted[valid] = X[valid] @ beta
            baseline[valid] = y_train.mean()
        tss = float(np.square(y - y.mean()).sum())
        results.append({
            "model_mae": float(np.abs(y - predicted).mean()),
            "mean_baseline_mae": float(np.abs(y - baseline).mean()),
            "cv_r2": float(1 - np.square(y - predicted).sum() / tss),
        })
    return {
        "scheme": "15 repetitions of shuffled 5-fold CV, within source cohort",
        "n_repetitions": n_rep,
        "folds": folds,
        "median_cv_r2": round(float(np.median([x["cv_r2"] for x in results])), 3),
        "median_model_mae": round(float(np.median([x["model_mae"] for x in results])), 2),
        "median_mean_baseline_mae": round(
            float(np.median([x["mean_baseline_mae"] for x in results])), 2
        ),
        "caution": "Source studies, repeated formulations and provenance groups cannot be "
                   "independently blocked with the available metadata. "
                   "Sample-level CV may be optimistic.",
    }


def get_results(df: pd.DataFrame) -> dict:
    lit = cohort_inputs(df, "Literature")
    project = cohort_inputs(df, "MAST3RBoost")
    if len(project) != 49 or project[TEMP].nunique() != 1 or project[TEMP].iloc[0] != 800:
        raise ValueError("Fixed-temperature cohort assumption is not met")
    lit_primary = cohort_inputs(df, "Literature", common_bands=True)
    # Limited-support values retained in source; omitted from primary comparison,
    # not silently corrected or deleted from the whole input.
    temp_counts = [
        {
            "temperature_c": int(temp),
            "n_samples": int((df.loc[df.source_group == "Literature", TEMP] == temp).sum()),
            "n_measured_bet": int((lit[TEMP] == temp).sum()),
            "mean_bet_m2_g": round(float(lit.loc[lit[TEMP] == temp, BET].mean()), 2),
            "median_bet_m2_g": round(float(lit.loc[lit[TEMP] == temp, BET].median()), 2),
        }
        for temp in sorted(df.loc[df.source_group == "Literature", TEMP].dropna().unique())
    ]
    lit_model = fit_ols(lit_primary, LIT_VARS)
    # Robustness check: expand into sparse 850/900 C conditions, keeping the
    # exceptional 80 C and unsupported 500 C out of the main sensitivity fit.
    lit_extended = lit.loc[lit[TEMP].between(600, 900)].copy()
    lit_sensitivity = fit_ols(lit_extended, LIT_VARS)
    proj_model = fit_ols(project, PROJECT_VARS)
    return {
        "data_source": "https://zenodo.org/records/23311682",
        "doi": "10.5281/zenodo.23311682",
        "data_grain": "research material sample (not a production batch)",
        "literature": {
            "all_bet_samples": len(lit),
            "primary_common_temperature_values_c": list(CORE_TEMPS),
            "primary_n": len(lit_primary),
            "temp_group_summary": temp_counts,
            "unadjusted_pearson_r": {
                "temperature": pearson_or_none(lit, TEMP),
                "K_C": pearson_or_none(lit, KC),
                "O_C": pearson_or_none(lit, O_C),
                "N_C": pearson_or_none(lit, N_C),
            },
            "adjusted_model": lit_model,
            "sensitivity_600_to_900": lit_sensitivity,
            "bootstrap_95": bootstrap_intervals(lit_primary, LIT_VARS),
            "sample_level_repeated_cv": repeated_cv(lit_primary, LIT_VARS),
        },
        "MAST3RBoost": {
            "n": len(project),
            "temperature_c": 800,
            "temperature_effect_estimable": False,
            "unadjusted_pearson_r": {
                "K_C": pearson_or_none(project, KC),
                "O_C": pearson_or_none(project, O_C),
                "N_C": pearson_or_none(project, N_C),
            },
            "adjusted_model": proj_model,
            "predictor_pearson_correlations": {
                name: {
                    other: round(float(project[name].corr(project[other])), 4)
                    for other in PROJECT_VARS
                }
                for name in PROJECT_VARS
            },
            "bootstrap_95": bootstrap_intervals(project, PROJECT_VARS, seed=20261107),
            "sample_level_repeated_cv": repeated_cv(project, PROJECT_VARS, seed=1043),
        },
        "known_limits": [
            "Activation temperature is a constant in the 49 MAST3RBoost samples.",
            "A literature record at 80 C is unusual and is not silently changed.",
            "500 C and 850 C strata have only 1 and 2 literature records respectively.",
            "Literature group combines different studies, feedstocks and assays; "
            "study-level blocking and causal adjustment are unsupported.",
            "Correlations and adjusted coefficients are observational, not effects.",
            "CV at sample grain does not establish out-of-study generalization.",
        ],
    }


def make_charts(df: pd.DataFrame, figures: Path) -> None:
    figures.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.size": 10,
        "font.family": "DejaVu Sans",
        "svg.hashsalt": "nottingham-relationships-1",
    })
    lit = cohort_inputs(df, "Literature")
    rng = np.random.default_rng(124)
    fig, ax = plt.subplots(figsize=(9, 5.1))
    colors = ("#B8A7D6", "#8F77BE", "#7252B2", "#4D3087")
    for i, temp in enumerate(DISPLAY_TEMPS):
        sub = lit.loc[lit[TEMP] == temp, BET].to_numpy(float)
        x = np.full(len(sub), i) + rng.uniform(-.19, .19, size=len(sub))
        ax.scatter(x, sub, alpha=.62, s=26, color=colors[i], edgecolor="white", linewidth=.25)
        ax.scatter(i, np.median(sub), marker="_", s=260, linewidths=3, color="#263644")
        ax.text(i, max(sub) + 110, f"n={len(sub)}", ha="center", fontsize=9, color="#3D4150")
    ax.set_xticks(range(len(DISPLAY_TEMPS)), [f"{int(t)} °C" for t in DISPLAY_TEMPS])
    ax.set(xlabel="Reported activation temperature, literature cohort",
           ylabel="BET surface area (m²/g)",
           title="Literature cohort: BET by activation-temperature stratum")
    ax.grid(axis="y", alpha=.2)
    fig.text(.5, .01, "Source studies and materials vary; these contrasts are descriptive, not causal.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1))
    fig.savefig(figures/"literature_temperature_bet.svg", format="svg", metadata={"Date":None})
    plt.close(fig)

    project = cohort_inputs(df, "MAST3RBoost")
    fig, axes = plt.subplots(1, 2, figsize=(10.7, 4.85))
    for ax, col, lab in zip(axes, (KC, O_C), ("K/C ratio", "O/C ratio")):
        part = project[[col, BET]].dropna()
        xx = part[col].to_numpy(float)
        yy = part[BET].to_numpy(float)
        ax.scatter(xx, yy, color="#6948A8", alpha=.7, s=38)
        a, b = np.polyfit(xx, yy, 1)
        xx_line = np.linspace(xx.min(), xx.max(), 100)
        ax.plot(xx_line, a * xx_line + b, color="#C78554", linewidth=2,
                label="Unadjusted linear fit")
        ax.set(xlabel=lab, ylabel="BET surface area (m²/g)",
               title=f"{lab} vs BET (n={len(part)})")
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle("MAST3RBoost samples: reported activation temperature fixed at 800 °C")
    fig.text(.5, .01, "Univariate trends are not adjusted effects. Composition may be correlated.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.93))
    fig.savefig(figures/"fixed800_composition_bet.svg", format="svg", metadata={"Date":None})
    plt.close(fig)


def report(res: dict) -> str:
    lit = res["literature"]
    project = res["MAST3RBoost"]
    def rtxt(n):
        return "not identifiable" if n is None else f"{n:+.3f}"
    def coef_table(c):
        model, ci = c["adjusted_model"], c["bootstrap_95"]["intervals"]
        return [
            "| Predictor | Fitted association (m²/g per unit) | Bootstrap 95% interval |",
            "|---|---:|---:|",
            *[
                f"| {LABELS[k]} | {model['coefficients'][k]:+.2f} | "
                f"[{ci[k][0]:+.2f}, {ci[k][1]:+.2f}] |"
                for k in model["predictors"]
            ],
        ]
    return "\n".join([
        "# 탄소소재 제조조건과 BET: 출처 분리 탐색 분석",
        "",
        "> 관찰된 연구자료의 통계적 연관성만 분석합니다. 인과효과, 양산 최적 조건, 연구 간 일반화 성능은 검증되지 않았습니다.",
        "",
        "## 출처·관측단위",
        "",
        "- University of Nottingham / Nanolayers, Zenodo v2, DOI 10.5281/zenodo.23311682.",
        "- 단위: 활성탄 시료. 양산 Batch의 시계열이 아닙니다.",
        f"- 문헌 BET 관측 {lit['all_bet_samples']}개, 프로젝트 시료 {project['n']}개.",
        "- 원본 CSV는 직접 내려받아 처리하고, 수정된 행 단위 사본을 공개하지 않습니다.",
        "",
        "## 1. 문헌 시료: 활성화 온도와 BET",
        "",
        "| 보고 온도(°C) | 시료 수 | BET 측정 수 | 평균 BET(m²/g) | 중앙값 BET(m²/g) |",
        "|---:|---:|---:|---:|---:|",
        *[
            f"| {x['temperature_c']} | {x['n_samples']} | {x['n_measured_bet']} | "
            f"{x['mean_bet_m2_g']:.2f} | {x['median_bet_m2_g']:.2f} |"
            for x in lit["temp_group_summary"]
        ],
        "",
        "![문헌 온도별 BET 분포](./figures/literature_temperature_bet.svg)",
        "",
        "- 80 °C는 특이 기록이며 원자료를 임의로 800 °C로 고치지 않았습니다.",
        "- 500 °C 1개, 850 °C 2개 시료는 표본 지원이 적어 1차 모델에서 제외했습니다.",
        "- 900 °C도 10개 관측뿐이어서 기본 비교는 600·700·800 °C의 충분한 표본이 있는 집단에 제한했습니다.",
        f"- 전체 문헌 시료에서 온도와 BET의 단순 Pearson r = {rtxt(lit['unadjusted_pearson_r']['temperature'])}. "
        "다른 제조·원료 요인을 제거한 수치가 아닙니다.",
        f"- 1차 다중회귀 입력: 문헌 시료 {lit['primary_n']}개, "
        "활성화 온도(100 °C 단위), K/C, O/C, N/C, Porogen. 다음 계수는 이 표본 안에서의 조건부 연관성입니다.",
        "",
        *coef_table(lit),
        "",
        f"- 단순 OLS 설명력(훈련 표본 R²): {lit['adjusted_model']['r2_in_sample']:.3f}. "
        f"반복 5-fold CV 중앙 R²: {lit['sample_level_repeated_cv']['median_cv_r2']:.3f}.",
        f"- CV MAE: 모델 {lit['sample_level_repeated_cv']['median_model_mae']:.2f} m²/g, "
        f"훈련집단 평균 기준모델 {lit['sample_level_repeated_cv']['median_mean_baseline_mae']:.2f} m²/g.",
        "- 온도 범위를 600–900 °C로 넓힌 민감도 모델("
        + str(lit["sensitivity_600_to_900"]["n"])
        + "개 시료)에서 온도 100 °C당 조건부 연관 계수는 "
        + str(lit["sensitivity_600_to_900"]["coefficients"]["temp_per_100C"])
        + " m²/g입니다. 이것도 인과효과는 아닙니다.",
        "- 연구별 반복·동일 원료·측정법 구분키가 없으므로 교차검증에서도 연구 간 일반화 성능을 주장할 수 없습니다.",
        "",
        "## 2. MAST3RBoost 시료: 800 °C 고정 조건의 조성 비교",
        "",
        f"- 시료 {project['n']}개는 모두 활성화 온도가 800 °C이고 유지시간 등도 일정합니다.",
        "- 따라서 이 집단만으로는 활성화 온도 변화의 효과를 평가할 수 없습니다.",
        f"- K/C–BET 단순 Pearson r = {rtxt(project['unadjusted_pearson_r']['K_C'])}. "
        f"O/C–BET r = {rtxt(project['unadjusted_pearson_r']['O_C'])}. "
        f"N/C–BET r = {rtxt(project['unadjusted_pearson_r']['N_C'])}.",
        "",
        "![동일 온도 조건 조성 및 BET](./figures/fixed800_composition_bet.svg)",
        "",
        "- K/C, O/C, N/C를 사전 지정한 공변량으로 다중회귀를 구성했습니다. "
        "조성 간 동시 변동 때문에 단일 변수의 인과적 기여를 의미하지 않습니다.",
        "- 주의: O/C는 단순 상관계수에서 음(-)의 방향이지만, "
        "K/C와 N/C를 통제한 회귀에서는 양(+)의 계수로 부호가 역전됩니다. "
        "조성변수의 상관·선택된 공변량·생략 요인에 민감할 수 있으므로 "
        "O/C 증가가 물성을 개선한다고 해석하지 않습니다.",
        "",
        *coef_table(project),
        "",
        f"- 단순 OLS 설명력(훈련 표본 R²): {project['adjusted_model']['r2_in_sample']:.3f}. "
        f"반복 5-fold CV 중앙 R²: {project['sample_level_repeated_cv']['median_cv_r2']:.3f}.",
        f"- CV MAE: 모델 {project['sample_level_repeated_cv']['median_model_mae']:.2f} m²/g, "
        f"훈련집단 평균 기준모델 {project['sample_level_repeated_cv']['median_mean_baseline_mae']:.2f} m²/g.",
        "",
        "## 엔지니어의 판단",
        "",
        "1. 활성화 온도는 출처마다 다르게 설계됐습니다. 800 °C 고정 연구 시료에서는 온도 비교가 불가능합니다.",
        "2. 문헌의 원료 종류·제조 조건·BET 측정법이 혼재되어 온도-물성 관계를 공정 인과효과로 해석할 수 없습니다.",
        "3. 단순 상관과 다중회귀 계수, bootstrap 구간, CV 오차를 구분했습니다. 계수가 0에서 멀더라도 실험적 확인이 필요합니다.",
        "4. 시료 간 교차검증은 동일 연구 내 유사 조건이 다른 폴드에 들어갈 수 있어, 외부 연구·공장으로의 이전 성능을 입증하지 못합니다.",
        "5. Pilot/양산 적용 전에는 원료 LOT, furnace temperature profile, 가열 분위기, 장치 Scale, 체류시간, 제품 수율, BET 시험법, 에너지 원단위 및 독립 확인실험 자료가 필요합니다.",
        "",
        "## 구현 및 제한",
        "",
        "- 이번 작업은 공개 연구자료의 출처별 기초 비교·조건부 회귀·부트스트랩·샘플 기준 CV까지 구현했습니다.",
        "- 통계모형의 사용은 탐색적 평가 목적이며 공정조건 최적화나 생산효율 개선의 증거가 아닙니다.",
        "- 원래 문헌 시료에서 동종 실험 조건을 식별하는 연구별 ID가 제공되지 않아 study-blocked 검증을 수행하지 않았습니다.",
        "- CI 테스트는 원본 데이터 무결성·샘플 구조·결과 산출의 코드 재현성을 검증합니다.",
        "",
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, help="Unmodified Zenodo v2 CSV")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "results")
    args = parser.parse_args()
    raw = args.source.read_bytes() if args.source else fetch_source()
    verify_md5(raw)
    frame = parse_csv(raw.decode("utf-8-sig"))
    results = get_results(frame)
    args.output.mkdir(parents=True, exist_ok=True)
    make_charts(frame, args.output / "figures")
    (args.output / "summary.json").write_text(
        json.dumps(results, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output / "REPORT.md").write_text(report(results), encoding="utf-8")
    print("Source samples:", len(frame))
    print("Literature primary n:", results["literature"]["primary_n"])
    print("MAST3RBoost fixed temperature:", results["MAST3RBoost"]["temperature_c"])
    print("Results:", args.output)


if __name__ == "__main__":
    main()
