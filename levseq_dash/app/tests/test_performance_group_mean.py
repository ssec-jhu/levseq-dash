import os
import time

import numpy as np
import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.utils import utils

TIME_GROUP_MEAN = []
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def calculate_group_mean_ratios_per_smiles_and_plate_optm(df):
    """Optimized version using vectorized operations in pandas"""
    group_cols = [gs.c_smiles, gs.c_plate]
    value_col = gs.c_fitness_value

    # Check if ratio column already exists and has values - if so, skip calculation
    if gs.cc_ratio in df.columns and not df[gs.cc_ratio].isna().all():
        return df

    # --------------------------------
    # Clean up the fitness value column - OPTIMIZED
    # --------------------------------
    # Convert to numeric - this is the main operation
    numeric_vals = pd.to_numeric(df[value_col], errors="coerce")

    # Only check for "trac" in rows that failed numeric conversion (became NaN)
    # This avoids string operations on already-numeric data
    nan_mask = numeric_vals.isna()
    if nan_mask.any():
        # Only convert to string and check the NaN values
        trac_mask = df.loc[nan_mask, value_col].astype(str).str.contains("trac", case=False, na=False, regex=False)
        # Set trac values to 0.001, others to 0
        numeric_vals.loc[nan_mask] = 0.0
        numeric_vals.loc[nan_mask[nan_mask].index[trac_mask]] = 0.001
    else:
        # No NaN values, just fill with 0
        numeric_vals = numeric_vals.fillna(0)

    df[value_col] = numeric_vals

    # Compute mean ONLY for rows where parent_col == parent_value, per group and that the parent is not 0
    # if a prent has 0 fitness value that group combo is ignored
    parent_mean = (
        df[(df[gs.c_substitutions] == "#PARENT#") & (df[value_col] > 0)]
        .groupby(group_cols, sort=False)[value_col]  # sort=False saves time
        .mean()
        .reset_index()
        .rename(columns={value_col: "mean"})
    )

    # Check if the mean column is all 0, NaN, or null - if so, return early
    if len(parent_mean) == 0 or parent_mean["mean"].isna().all() or np.isclose(parent_mean["mean"], 0).all():
        df[gs.cc_ratio] = None
        return df

    # Merge is highly optimized in pandas - use it
    df = df.merge(parent_mean, on=group_cols, how="left")

    # Compute fitness ratio relative to the mean - OPTIMIZED
    # Vectorized ratio calculation with rounding in one step
    # Only compute where mean exists and is not zero
    valid_mask = df["mean"].notna() & (df["mean"] != 0)
    df[gs.cc_ratio] = np.where(valid_mask, (df[value_col] / df["mean"]).round(3), np.nan)

    # Compute min/max in single agg call, then merge
    group_stats_ratio = (
        df.groupby(group_cols, sort=False)[gs.cc_ratio].agg(min_group_ratio="min", max_group_ratio="max").reset_index()
    )

    # Single merge for both min and max
    df = df.merge(group_stats_ratio, on=group_cols, how="left")

    return df


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_calculate_group_mean_ratios_per_smiles_and_plate(mocker, disk_manager_from_app_data):
    """
    This test was written to gradually optimize the group mean ratio calculation.
    In the final release the code will be the optimized version.
    """

    # Get the data path from the disk manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_app_data)

    failure_count = 0
    for exp in disk_manager_from_app_data.get_all_lab_experiments_with_meta_data():
        experiment_id = exp["experiment_id"]
        exp = disk_manager_from_app_data.get_experiment(experiment_id)
        try:
            start_time = time.time()
            result = utils.calculate_group_mean_ratios_per_smiles_and_plate(exp.data_df)
            execution_time = time.time() - start_time

            start_time = time.time()
            result_optm = calculate_group_mean_ratios_per_smiles_and_plate_optm(exp.data_df)
            execution_time_optm = time.time() - start_time

            # start_time = time.time()
            # result_combo = utils.calculate_group_mean_ratios_per_smiles_and_plate_combo(exp.data_df)
            # execution_time_combo = time.time() - start_time

            assert result is not None
            assert result_optm is not None
            # assert result_combo is not None

            if "mean" in result.columns:
                assert result[gs.cc_ratio].equals(result_optm[gs.cc_ratio])
                # assert result[gs.cc_ratio].equals(result_combo[gs.cc_ratio])

            # Store timing data with row count
            row_count = len(exp.data_df)
            TIME_GROUP_MEAN.append((f"{experiment_id}", execution_time, execution_time_optm, row_count))

        except Exception as e:
            # if there is an exception, print it and continue with the next experiment but the test must fail
            failure_count += 1
            print(f"Exception at {experiment_id}: {e}")  # Debugging: Print exception details

    assert failure_count == 0


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_print_timing_group_mean_summary():
    """Print a summary of all timing results from the performance tests."""
    print("\n\n" + "=" * 100)
    print("PERFORMANCE TEST RESULTS")
    print("=" * 100)
    print(f"\nTotal files tested: {len(TIME_GROUP_MEAN)}")
    print("\n{:<50} {:>8} {:>20}".format("File", "Rows", "Time Difference"))
    print("-" * 100)

    # combo_wins = 0
    # optimized_wins = 0
    # combo_ties_optimized = 0
    # all_same = 0

    for test_id, duration, duration_optm, row_count in TIME_GROUP_MEAN:
        # Determine which function is best (within 0.1ms tolerance)
        tolerance = 0.0001

        # Compare all three
        times = {
            "original": duration,
            "optimized": duration_optm,
        }

        min_time = min(times.values())

        # Calculate time difference relative to original (baseline)
        time_diff = duration - duration_optm  # positive = optimized is faster

        if time_diff > 0:
            # Optimized is faster - saved time
            time_diff_str = f"-{time_diff * 1000:.2f}ms"
        else:
            # Optimized is slower - added time
            time_diff_str = f"+{time_diff * 1000:.2f}ms *SLOWER"

        print(f"{test_id:<50} {row_count:>8}  {time_diff:>20}")
