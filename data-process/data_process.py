import argparse
from pathlib import Path

import pandas as pd


NUMERIC_COLS = ["reaction_time", "value_difference", "CV"]
CATEGORICAL_COLS = ["category", "correct"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean experiment CSV data for DDM modeling.")
    parser.add_argument("--input", dest="input_path", help="Path to the raw csv file.")
    parser.add_argument("--output", dest="output_path", help="Path to save cleaned csv file.")
    parser.add_argument(
        "--experiment-id",
        type=int,
        default=1,
        help="Experiment id used when --input/--output are not provided (default: 1).",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="Display diagnostic plots while processing data.",
    )
    return parser.parse_args()


def _load_plot_dependencies() -> tuple:
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Plotting dependencies are missing. Install matplotlib and seaborn to use --show-plots."
        ) from exc
    return plt, sns


def _plot_missing(df: pd.DataFrame, title: str, show_plots: bool) -> None:
    if not show_plots:
        return

    plt, sns = _load_plot_dependencies()
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap="viridis", yticklabels=False)
    plt.title(title)
    plt.show()


def _plot_box(df: pd.DataFrame, title: str, show_plots: bool) -> None:
    if not show_plots:
        return

    numeric_cols = [col for col in NUMERIC_COLS if col in df.columns]
    if not numeric_cols:
        return

    plt, sns = _load_plot_dependencies()
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df[numeric_cols])
    plt.title(title)
    plt.show()


def clean_data(df: pd.DataFrame, show_plots: bool = False) -> pd.DataFrame:
    print("数据预览：")
    print(df.head())

    print("\n缺失值统计：")
    print(df.isnull().sum())
    _plot_missing(df, "缺失值热图", show_plots)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())

    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0])

    print("\n缺失值处理后统计：")
    print(df.isnull().sum())
    _plot_missing(df, "缺失值处理后的热图", show_plots)

    _plot_box(df, "箱型图 - 异常值检测", show_plots)

    for col in [col for col in NUMERIC_COLS if col in df.columns]:
        mean = df[col].mean()
        std = df[col].std()
        df = df[df[col].between(mean - 3 * std, mean + 3 * std)]

    _plot_box(df, "箱型图 - 异常值处理后的数据", show_plots)

    print("清洗后的数据预览：")
    print(df.head())
    return df


def main() -> None:
    args = parse_args()

    input_path = Path(args.input_path or f"exp{args.experiment_id}.csv")
    output_path = Path(args.output_path or f"cleaned_exp{args.experiment_id}.csv")

    df = pd.read_csv(input_path)
    cleaned_df = clean_data(df, show_plots=args.show_plots)
    cleaned_df.to_csv(output_path, index=False)
    print(f"清洗后的数据已保存到: {output_path}")


if __name__ == "__main__":
    main()
