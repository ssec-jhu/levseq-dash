import os
import time
from contextvars import copy_context

import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

from levseq_dash.app import global_strings as gs

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def run_callback_on_load_experiment_page(pathname, experiment_id):
    from levseq_dash.app.main_app import on_load_experiment_page

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "url.pathname"}]}))

    # Time the function execution
    result = on_load_experiment_page(pathname=pathname, experiment_id=experiment_id)

    return result


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_callback_on_load_experiment_page_random_experiment(mocker, path_exp_ep_data, tmp_path):
    from levseq_dash.app.tests.conftest import load_config_mock_string
    from levseq_dash.app.tests.mutation_simulator import generate_temp_test_experiment_files

    base_csv_path = path_exp_ep_data[0]
    csv_path, experiment_id = generate_temp_test_experiment_files(tmp_path, base_csv_path, num_plates=500)
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": str(tmp_path)},
    }
    ctx = copy_context()
    start_time = time.time()
    result = ctx.run(run_callback_on_load_experiment_page, gs.nav_experiment_path, experiment_id)
    execution_time = time.time() - start_time
    TIME_RESULTS.append((f"RND {len(result[1])} rows", execution_time))


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_callback_on_load_experiment_page_big_experiment(mocker, disk_manager_from_app_data):
    # Mock the singleton instance to use our test data manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_app_data)

    # TESTING WITH THE TEV DATA
    experiment_id = "MYLAB-b50e7cb2-6e94-4022-9e9d-ff3fa3d4078f"

    ctx = copy_context()
    start_time = time.time()
    result = ctx.run(run_callback_on_load_experiment_page, gs.nav_experiment_path, experiment_id)
    execution_time = time.time() - start_time
    assert result is not None
    assert len(result[1]) == 159133  # TEV has a lot of rows
    TIME_RESULTS.append((f"TEV {len(result[1])} rows", execution_time))


TIME_RESULTS = []


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_print_timing_summary():
    """Print a summary of all timing results from the performance tests."""
    print("\n\n" + "=" * 50)
    print("PERFORMANCE TEST TIMING SUMMARY")
    print("=" * 50)
    for test_id, duration in TIME_RESULTS:
        print(f"  {test_id}: {duration:.4f} seconds")
