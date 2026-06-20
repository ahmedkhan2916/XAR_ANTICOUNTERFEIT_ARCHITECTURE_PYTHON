import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_AI_PATH = (
    PROJECT_ROOT
    / "Datasets"
    / "GeminiAiPerfectDaylightA12"
    / "GeminiAiPerfectDaylightA12_OutputResult.json"
)
DEFAULT_GENUINE_PATH = (
    PROJECT_ROOT
    / "Datasets"
    / "GenuineDaylightA12"
    / "GenuineDaylightA12_OutputResult.json"
)
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parent / "ai_vs_genuine_comparison3.png"

METRICS = (
    ("bleedScore", "Bleed Score"),
    ("lineContinuity", "Line Continuity"),
    ("dotCircularity", "Dot Circularity"),
    ("edgeTurbulence", "Edge Turbulence"),
    ("localVariance", "Local Variance"),
)


def load_result(path):
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    physical_data = data.get("statistics", {}).get("PhysicalPrintData")
    stability_report = data.get("physicalStabilityReport")
    if not isinstance(physical_data, dict) or not isinstance(
        stability_report, dict
    ):
        raise ValueError(f"{path} is missing physical analysis data")

    return physical_data, stability_report


def metric_values(physical_data, stability_report, metric):
    statistics = physical_data.get(metric)
    cv_key = f"{metric}CV"
    if not statistics or cv_key not in stability_report:
        raise ValueError(f"Missing {metric} statistics or {cv_key}")

    return {
        "mean": statistics["mean"],
        "std": statistics["std"],
        "cv": stability_report[cv_key],
    }


def add_value_labels(axis, bars):
    for bar in bars:
        value = bar.get_height()
        axis.annotate(
            f"{value:.3f}",
            (bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def plot_comparison(ai_path, genuine_path, output_path):
    ai_physical, ai_report = load_result(ai_path)
    genuine_physical, genuine_report = load_result(genuine_path)

    sns.set_theme(style="whitegrid")
    figure, axes = plt.subplots(3, 2, figsize=(15, 16))
    axes = axes.flatten()
    colors = {"Mean": "#FF2727", "Standard deviation": "#55EF14"}

    for axis, (metric, title) in zip(axes, METRICS):
        ai = metric_values(ai_physical, ai_report, metric)
        genuine = metric_values(genuine_physical, genuine_report, metric)
        positions = np.arange(2)
        width = 0.34

        mean_bars = axis.bar(
            positions - width / 2,
            [ai["mean"], genuine["mean"]],
            width,
            label="Mean",
            color=colors["Mean"],
        )
        std_bars = axis.bar(
            positions + width / 2,
            [ai["std"], genuine["std"]],
            width,
            label="Standard deviation",
            color=colors["Standard deviation"],
        )

        axis.set_title(title, fontsize=13, fontweight="bold")
        axis.set_xticks(positions, ["AI", "Genuine"])
        axis.set_ylabel("Metric value")
        axis.set_ylim(bottom=0)
        add_value_labels(axis, mean_bars)
        add_value_labels(axis, std_bars)

        cv_axis = axis.twinx()
        cv_percent = [ai["cv"] * 100, genuine["cv"] * 100]
        cv_axis.plot(
            positions,
            cv_percent,
            color="#FFB938",
            marker="o",
            linewidth=2,
            markersize=7,
            label="CV",
        )
        cv_axis.set_ylabel("Coefficient of variation (%)", color="#FFB938")
        cv_axis.tick_params(axis="y", colors="#FFB938")
        cv_axis.set_ylim(bottom=0)
        for position, value in zip(positions, cv_percent):
            cv_axis.annotate(
                f"{value:.2f}%",
                (position, value),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                color="#000000",
                fontsize=9,
                fontweight="bold",
            )

    axes[-1].axis("off")
    figure.suptitle(
        "AI vs Genuine Physical Print Metrics",
        fontsize=18,
        fontweight="bold",
        y=0.995,
    )
    figure.text(
        0.5,
        0.975,
        "Bars compare mean and standard deviation; red markers show CV percentage.",
        ha="center",
        fontsize=11,
    )
    figure.legend(
        handles=[
            Patch(color=colors["Mean"], label="Mean"),
            Patch(color=colors["Standard deviation"], label="Standard deviation"),
            Line2D(
                [0],
                [0],
                color="#FFB938",
                marker="o",
                linewidth=2,
                label="CV",
            ),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.958),
        ncol=3,
        frameon=True,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.925))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    print(f"Graph saved to: {output_path}")

    plt.close(figure)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Plot AI and Genuine physical statistics from result JSON files."
    )
    parser.add_argument("--ai", type=Path, default=DEFAULT_AI_PATH)
    parser.add_argument("--genuine", type=Path, default=DEFAULT_GENUINE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    plot_comparison(
        arguments.ai,
        arguments.genuine,
        arguments.output,
    )
