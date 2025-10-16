import os
import time

import numpy as np
import plotly_express as px
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis
from levseq_dash.app.utils import utils

TIME_COLORSCALE = []
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def data_bars_group_mean_colorscale_optm(
    df,
    value_col=gs.cc_ratio,
    min_col="min_group_ratio",
    max_col="max_group_ratio",
    color_scale=px.colors.diverging.RdBu,
):
    """
    Generate Dash AG Grid cell styles with a color gradient bar.
    """
    styles = []

    # Fast early return if required columns don't exist or are entirely null
    if value_col not in df.columns or min_col not in df.columns or max_col not in df.columns:
        return styles

    # Fast check: if the entire ratio column is null/NaN, return empty styles
    if df[value_col].isna().all() or df[value_col].isnull().all():
        return styles

    # Also check if min/max columns are entirely null, which would make coloring meaningless
    if df[min_col].isna().all() or df[max_col].isna().all():
        return styles

    if gs.hashtag_parent not in df[gs.c_substitutions].values:
        return styles

    n_bins = 96
    color_scale = px.colors.sample_colorscale(px.colors.diverging.RdBu, [i / n_bins for i in range(n_bins)])
    color_scale.reverse()
    n_colors = len(color_scale)

    valid_mask = df[value_col].notna() & df[min_col].notna() & df[max_col].notna()

    filtered = df.loc[valid_mask, [value_col, min_col, max_col]]

    if filtered.empty:
        return styles

    ratios = filtered[value_col].to_numpy(dtype=float)
    mins = filtered[min_col].to_numpy(dtype=float)
    maxs = filtered[max_col].to_numpy(dtype=float)
    denom = maxs - mins

    with np.errstate(divide="ignore", invalid="ignore"):
        norm = np.divide(
            ratios - mins,
            denom,
            out=np.full_like(ratios, 0.5, dtype=float),
            where=denom != 0,
        )

    norm = np.clip(norm, 0.0, 1.0)
    color_indices = np.clip((norm * (n_colors - 1)).astype(int), 0, n_colors - 1)
    bar_colors = [color_scale[i] for i in color_indices]
    bar_widths = np.clip((norm * 100).astype(int), 0, 100)
    text_colors = np.where(bar_widths > 89, "white", "black")

    backgrounds = [
        f"""
            linear-gradient(90deg,
            {color} 0%,
            {color} {width}%,
            white {width}%,
            white 100%)
        """
        for color, width in zip(bar_colors, bar_widths)
    ]
    conditions = [f"params.value == {ratio}" for ratio in ratios]

    styles.extend(
        [
            {
                "condition": condition,
                "style": {
                    "background": background,
                    "color": text_color,
                },
            }
            for condition, background, text_color in zip(conditions, backgrounds, text_colors)
        ]
    )

    return styles


def test_data_bars_group_mean_colorscale(mocker, disk_manager_from_app_data):
    """Test data_bars_group_mean_colorscale method."""

    # Get the data path from the disk manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_app_data)

    failure_count = 0
    for exp in disk_manager_from_app_data.get_all_lab_experiments_with_meta_data():
        experiment_id = exp["experiment_id"]
        exp = disk_manager_from_app_data.get_experiment(experiment_id)
        try:
            df_with_ratio = utils.calculate_group_mean_ratios_per_smiles_and_plate(exp.data_df)

            start_time = time.time()
            styles = vis.data_bars_group_mean_colorscale(df_with_ratio)
            execution_time = time.time() - start_time

            start_time = time.time()
            styles_optm = data_bars_group_mean_colorscale_optm(df_with_ratio)
            execution_time_optm = time.time() - start_time

            assert styles is not None
            assert styles_optm is not None

            assert styles == styles_optm

            # Store timing data with row count
            row_count = len(exp.data_df)
            TIME_COLORSCALE.append((f"{experiment_id}", execution_time, execution_time_optm, row_count))

        except Exception as e:
            # if there is an exception, print it and continue with the next experiment but the test must fail
            failure_count += 1
            print(f"Exception at {experiment_id}: {e}")  # Debugging: Print exception details

    assert failure_count == 0


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_print_colorscale_summary():
    """Print a summary of all timing results from the performance tests."""
    print("\n\n" + "=" * 100)
    print("PERFORMANCE TEST RESULTS")
    print("=" * 100)
    print(f"\nTotal files tested: {len(TIME_COLORSCALE)}")
    print("\n{:<50} {:>8} {:>20}".format("File", "Rows", "Time Difference"))
    print("-" * 100)

    # sort based on time
    TIME_COLORSCALE.sort(key=lambda x: x[1] - x[2], reverse=True)

    for test_id, duration, duration_optm, row_count in TIME_COLORSCALE:
        # Determine which function is best (within 0.1ms tolerance)

        # Calculate time difference relative to original (baseline)
        time_diff = duration - duration_optm  # positive = optimized is faster

        if time_diff > 0:
            # Optimized is faster - saved time
            time_diff_str = f"-{time_diff * 1000:.2f}ms"
        else:
            # Optimized is slower - added time
            time_diff_str = f"+{abs(time_diff) * 1000:.2f}ms *SLOWER"

        print(f"{test_id:<50} {row_count:>8}  {time_diff_str:>20}")
