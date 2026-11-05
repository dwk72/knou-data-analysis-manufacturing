"""Reconstructed reproducible demo of the submitted KNOU multivariate coursework.

The submitted assignment used additional CSV files that are not publicly available.
This demonstration deliberately uses scikit-learn's bundled Iris dataset instead.
The numerical results must not be represented as the original assignment results.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.decomposition import FactorAnalysis, PCA
from sklearn.preprocessing import StandardScaler


def analyze(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    iris = load_iris(as_frame=True)
    feature_frame = iris.data.copy()
    features = list(feature_frame.columns)
    scaled = StandardScaler().fit_transform(feature_frame)

    correlation = feature_frame.corr()
    correlation.to_csv(output_dir / "correlation.csv", encoding="utf-8-sig")

    pca = PCA().fit(scaled)
    scores = pca.transform(scaled)
    pd.DataFrame(scores[:, :2], columns=["PC1", "PC2"]).assign(
        species=iris.target_names[iris.target.to_numpy()]
    ).to_csv(output_dir / "pca_scores.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(
        pca.components_.T,
        index=features,
        columns=[f"PC{i+1}" for i in range(len(features))],
    ).to_csv(output_dir / "pca_components.csv", encoding="utf-8-sig")

    # A demonstrative unrotated two-factor model; no claim of the coursework's factor solution.
    fa = FactorAnalysis(n_components=2, random_state=42).fit(scaled)
    pd.DataFrame(
        fa.components_.T, index=features, columns=["Factor1", "Factor2"]
    ).to_csv(output_dir / "factor_loadings.csv", encoding="utf-8-sig")

    cumulative = np.cumsum(pca.explained_variance_ratio_)
    report = {
        "dataset": "scikit-learn Iris (demonstration, not coursework source)",
        "rows": len(feature_frame),
        "variables": len(features),
        "pca_first_two_explained_variance_ratio": float(cumulative[1]),
        "outputs": ["correlation.csv", "pca_scores.csv", "pca_components.csv", "factor_loadings.csv"],
    }
    summary = (
        "# Reconstructed multivariate demo: execution report\n\n"
        "- Data: scikit-learn bundled Iris dataset. This is NOT the source dataset of the submitted KNOU assignment.\n"
        f"- Observations: {report['rows']}\n"
        f"- Numerical variables: {report['variables']}\n"
        f"- PCA variance explained by PC1+PC2: {report['pca_first_two_explained_variance_ratio']:.4f}\n"
        "- Factor analysis: two-factor unrotated teaching demonstration, not a validated latent construct.\n"
        "- Correlation and loadings are descriptive; they do not establish manufacturing root causes.\n"
    )
    (output_dir / "REPORT.md").write_text(summary, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "output")
    args = parser.parse_args()
    result = analyze(args.output_dir)
    print(f"Rows: {result['rows']}; first two PCs explain {result['pca_first_two_explained_variance_ratio']:.4f}")
    print(f"Saved report: {args.output_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
