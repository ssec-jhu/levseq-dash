import os
import time
from contextvars import copy_context

import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

from levseq_dash.app import global_strings as gs

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

TIME_RESULTS = []


def run_callback_on_load_experiment_page(pathname, experiment_id):
    from levseq_dash.app.main_app import on_load_experiment_page

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "url.pathname"}]}))

    # Time the function execution
    result = on_load_experiment_page(pathname=pathname, experiment_id=experiment_id)

    return result


def test_callback_on_load_experiment_page_random_experiment(mocker, path_exp_ep_data, tmp_path):
    from levseq_dash.app.data_manager.disk_manager import DiskDataManager
    from levseq_dash.app.tests.conftest import load_config_mock_string
    from levseq_dash.app.tests.mutation_simulator import generate_temp_test_experiment_files

    # we need to mock the config to use tmp_path first then create the experiment files
    # fixed a bug here where it was the other way
    # base_csv_path = path_exp_ep_data[0]
    # csv_path, experiment_id = generate_temp_test_experiment_files(tmp_path, base_csv_path, num_plates=500)

    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": str(tmp_path)},
    }

    # Create the test experiment files
    base_csv_path = path_exp_ep_data[0]
    csv_path, experiment_id = generate_temp_test_experiment_files(tmp_path, base_csv_path, num_plates=500)

    # Create a disk manager instance with the mocked config (which will use tmp_path)
    disk_mgr = DiskDataManager()

    # Mock the singleton instance to use our test data manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_mgr)

    ctx = copy_context()
    start_time = time.time()
    result = ctx.run(run_callback_on_load_experiment_page, gs.nav_experiment_path, experiment_id)
    execution_time = time.time() - start_time
    TIME_RESULTS.append((f"RND {len(result[1])} rows", execution_time))


def test_callback_on_load_experiment_page_epdata(mocker, disk_manager_from_test_data):
    # Mock the singleton instance to use our test data manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_test_data)

    # TESTING WITH THE TEV DATA
    experiment_id = "flatten_ep_processed_xy_cas"

    ctx = copy_context()
    start_time = time.time()
    result = ctx.run(run_callback_on_load_experiment_page, gs.nav_experiment_path, experiment_id)
    execution_time = time.time() - start_time
    assert result is not None
    assert len(result[2]) == 1920  # TEV has a lot of rows
    TIME_RESULTS.append((f"EPPROC {len(result[2])} rows", execution_time))


def test_callback_on_load_experiment_page_on_all_real_data_files(mocker, app_data_path, disk_manager_from_app_data):
    # Get the data path from the disk manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_app_data)

    failure_count = 0
    ctx = copy_context()
    # make a list of all the experiments in the disk manager and run the callback on each one

    for exp in disk_manager_from_app_data.get_all_lab_experiments_with_meta_data():
        experiment_id = exp["experiment_id"]
        try:
            start_time = time.time()
            result = ctx.run(run_callback_on_load_experiment_page, gs.nav_experiment_path, experiment_id)
            execution_time = time.time() - start_time
            assert result is not None
            assert len(result[2][0]) == 8  # Ensure there are 9 columns for the variants list
            TIME_RESULTS.append((f"{experiment_id}, {len(result[2])} rows ", execution_time))
        except Exception as e:
            # if there is an exception, print it and continue with the next experiment but the test must fail
            failure_count += 1
            print(f"Exception at {experiment_id}: {e}")  # Debugging: Print exception details

    assert failure_count == 0


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_print_timing_summary():
    """Print a summary of all timing results from the performance tests."""
    print("\n\n" + "=" * 50)
    print("PERFORMANCE TEST TIMING SUMMARY")
    print("=" * 50)
    # sort by duration
    TIME_RESULTS.sort(key=lambda x: x[1])
    for test_id, duration in TIME_RESULTS:
        print(f"  {test_id}, {duration:.4f} seconds")
