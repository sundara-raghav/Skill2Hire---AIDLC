"""
Report Generation Module

Generates Markdown evaluation report per business-logic-model.md section 5.4:
- Model name and version
- Training date and duration
- Cross-validation scores (mean ± std)
- Test set metrics (all 5)
- Confusion matrix
- Feature importance (tree models)
- Performance threshold validation
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.logger import setup_logger

logger = setup_logger()


def generate_evaluation_report(metrics, version, dataset_size, duration, report_dir):
    """
    Generate Markdown evaluation report.

    Args:
        metrics (dict): Model metrics keyed by model name
        version (str): Version string (e.g. 'v1')
        dataset_size (int): Total dataset records
        duration (float): Training duration in seconds
        report_dir (str): Output directory

    Returns:
        str: Path to generated report file
    """
    os.makedirs(report_dir, exist_ok=True)

    best = max(metrics, key=lambda k: (
        metrics[k].get('f1_score', 0),
        metrics[k].get('accuracy', 0),
        metrics[k].get('roc_auc', 0)
    )) if metrics else 'N/A'

    lines = [
        f"# ML Pipeline Evaluation Report — {version}",
        "",
        f"**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC  ",
        f"**Version**: {version}  ",
        f"**Dataset Size**: {dataset_size} records  ",
        f"**Training Duration**: {duration:.2f}s  ",
        f"**Best Model (F1-Score)**: {best}  ",
        f"**Accuracy Threshold**: {Config.ACCURACY_THRESHOLD * 100:.0f}%  ",
        "",
        "---",
        "",
        "## Model Comparison",
        "",
        "| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Threshold |",
        "|-------|----------|-----------|--------|----------|---------|-----------|",
    ]

    for name, m in metrics.items():
        threshold = "[PASS]" if m.get('performance_threshold_met', False) else "[FAIL]"
        lines.append(
            f"| {name} | {m.get('accuracy', 'N/A')} | {m.get('precision', 'N/A')} | "
            f"{m.get('recall', 'N/A')} | {m.get('f1_score', 'N/A')} | "
            f"{m.get('roc_auc', 'N/A')} | {threshold} |"
        )

    lines += [
        "",
        "## Cross-Validation Scores (F1, 5-Fold Stratified)",
        "",
        "| Model | CV Mean | CV Std |",
        "|-------|---------|--------|",
    ]
    for name, m in metrics.items():
        if 'cv_f1_mean' in m:
            lines.append(f"| {name} | {m['cv_f1_mean']} | {m['cv_f1_std']} |")

    lines += ["", "## Confusion Matrices", ""]
    for name, m in metrics.items():
        cm = m.get('confusion_matrix')
        if cm and len(cm) == 2:
            lines += [
                f"### {name}",
                "",
                "| | Predicted Not Placed | Predicted Placed |",
                "|---|---|---|",
                f"| **Actual Not Placed** | {cm[0][0]} | {cm[0][1]} |",
                f"| **Actual Placed** | {cm[1][0]} | {cm[1][1]} |",
                "",
            ]

    # Feature importance for tree models (RULE-ME-005)
    tree_models_with_fi = {
        name: m for name, m in metrics.items()
        if 'feature_importance' in m
    }
    if tree_models_with_fi:
        lines += ["## Feature Importance (Top 10)", ""]
        for name, m in tree_models_with_fi.items():
            fi = m['feature_importance']
            top10 = list(fi.items())[:10]
            lines += [
                f"### {name}",
                "",
                "| Feature | Importance |",
                "|---------|------------|",
            ]
            for feat, imp in top10:
                lines.append(f"| {feat} | {imp:.6f} |")
            lines.append("")

    lines += ["## Recommendations", ""]
    if metrics:
        best_f1 = metrics[best].get('f1_score', 0)
        best_acc = metrics[best].get('accuracy', 0)
        if best_acc >= Config.ACCURACY_THRESHOLD:
            lines.append(f"- [PASS] Deploy **{best}** as primary model (F1={best_f1}, Accuracy={best_acc})")
        else:
            lines.append(
                f"- [WARN] Best model **{best}** accuracy {best_acc:.4f}"
                f" below {Config.ACCURACY_THRESHOLD} threshold"
            )
            lines.append("- Consider retraining with more data or tuned hyperparameters")

        failing = [n for n, m in metrics.items() if not m.get('performance_threshold_met', False)]
        if failing:
            lines.append(f"- Models below threshold: {', '.join(failing)}")

    report_path = os.path.join(report_dir, f'evaluation_report_{version}.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    logger.info(f"Evaluation report saved to {report_path}")
    return report_path
