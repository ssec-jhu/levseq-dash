import base64
import os
import time
from contextvars import copy_context

import pytest
from dash._callback_context import context_value
from dash._utils import AttributeDict

from levseq_dash.app.data_manager.experiment import MutagenesisMethod

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

TIME_RESULTS = []


def run_callback_on_upload_experiment_file(dash_upload_string_contents, filename, last_modified):
    """Helper function to run the upload experiment file callback in isolation."""
    from levseq_dash.app.main_app import on_upload_experiment_file

    # Set up callback context
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-button-upload-data.contents"}]}))

    # Execute the callback
    result = on_upload_experiment_file(
        dash_upload_string_contents=dash_upload_string_contents, filename=filename, last_modified=last_modified
    )
    return result


def run_callback_on_upload_structure_file(dash_upload_string_contents, filename, last_modified):
    """Helper function to run the upload structure file callback in isolation."""
    from levseq_dash.app.main_app import on_upload_structure_file

    # Set up callback context
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-button-upload-structure.contents"}]}))

    # Execute the callback
    result = on_upload_structure_file(
        dash_upload_string_contents=dash_upload_string_contents, filename=filename, last_modified=last_modified
    )
    return result


def run_callback_on_submit_experiment(
    n_clicks,
    experiment_name,
    experiment_date,
    substrate,
    product,
    assay,
    mutagenesis_method,
    experiment_doi,
    additional_info,
    geometry_content_base64_encoded_string,
    experiment_content_base64_encoded_string,
):
    """Helper function to run the on_submit_experiment callback in isolation."""
    from levseq_dash.app.main_app import on_submit_experiment

    # Set up callback context to simulate the button click
    context_value.set(
        AttributeDict(
            **{"triggered_inputs": [{"prop_id": "id-button-submit.n_clicks"}], "triggered_id": "id-button-submit"}
        )
    )

    # Execute the callback
    result = on_submit_experiment(
        n_clicks=n_clicks,
        experiment_name=experiment_name,
        experiment_date=experiment_date,
        substrate=substrate,
        product=product,
        assay=assay,
        mutagenesis_method=mutagenesis_method,
        experiment_doi=experiment_doi,
        experiment_additional_info=additional_info,
        geometry_content_base64_encoded_string=geometry_content_base64_encoded_string,
        experiment_content_base64_encoded_string=experiment_content_base64_encoded_string,
    )
    return result


def read_file_for_upload(path_exp_ep_data):
    csv_file_path = path_exp_ep_data[0]
    cif_file_path = path_exp_ep_data[1]

    with open(csv_file_path, "rb") as f:
        csv_content = f.read()
    with open(cif_file_path, "rb") as f:
        cif_content = f.read()

    # Create the dash upload format: "data:text/csv;base64,{base64_content}"
    csv_base64 = base64.b64encode(csv_content).decode("utf-8")
    cif_base64 = base64.b64encode(cif_content).decode("utf-8")

    return [csv_base64, cif_base64]


def test_callback_on_upload_experiment_file_alert(mocker, path_exp_ep_data, tmp_path):
    """Test the on_upload_experiment_file callback with timing."""
    import dash_bootstrap_components as dbc

    from levseq_dash.app.tests.conftest import load_config_mock_string

    # Mock the data manager configuration
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": str(tmp_path)},
    }

    base64_contents = read_file_for_upload(path_exp_ep_data)
    dash_upload_contents_incorrect = f"{base64_contents[0]}"

    # Time the upload callback execution
    ctx = copy_context()
    result = ctx.run(run_callback_on_upload_experiment_file, dash_upload_contents_incorrect, "random test name", "time")

    assert result is not None
    assert isinstance(result[0], dbc.Alert)


def test_callback_on_upload_experiment_file(mocker, path_exp_ep_data, disk_manager_from_temp_data):
    """Test the on_upload_experiment_file callback with timing."""

    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_temp_data)

    base64_contents = read_file_for_upload(path_exp_ep_data)
    dash_upload_contents = f"data:text/csv;base64,{base64_contents[0]}"

    # Time the upload callback execution
    ctx = copy_context()
    start_time = time.time()
    result = ctx.run(run_callback_on_upload_experiment_file, dash_upload_contents, "filename", "time")
    execution_time = time.time() - start_time

    # Verify the callback succeeded
    assert result is not None
    assert len(result) == 2  # Should return (info, base64_encoded_string)
    assert result[1] is not None  # base64_encoded_string should not be None

    TIME_RESULTS.append((f"on_upload_experiment_file", execution_time))


def test_callback_on_upload_experiment_file_empty(mocker, path_exp_ep_data, tmp_path):
    """Test the on_upload_experiment_file callback with timing."""
    ctx = copy_context()
    result = ctx.run(run_callback_on_upload_experiment_file, None, "randon", "time")
    assert result is not None


def test_callback_on_upload_structure_file(mocker, path_exp_ep_data, tmp_path):
    """Test the on_upload_structure_file callback with timing."""
    from levseq_dash.app.tests.conftest import load_config_mock_string

    # Mock the data manager configuration
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": str(tmp_path)},
    }

    # Read the test CIF file and encode it for upload
    base64_contents = read_file_for_upload(path_exp_ep_data)
    cif_base64 = base64_contents[1]
    dash_upload_contents = f"data:application/octet-stream;base64,{cif_base64}"

    # Time the upload callback execution
    ctx = copy_context()
    start_time = time.time()
    result = ctx.run(run_callback_on_upload_structure_file, dash_upload_contents, "filename", "last_modified")
    execution_time = time.time() - start_time

    # Verify the callback succeeded
    assert result is not None
    assert len(result) == 2  # Should return (info, base64_encoded_string)
    assert result[1] is not None  # base64_encoded_string should not be None

    # Verify the info contains the filename
    info = result[0]
    assert isinstance(info, list)
    assert len(info) > 0

    TIME_RESULTS.append((f"on_upload_structure_file", execution_time))


def test_callback_on_upload_structure_file_empty(mocker, path_exp_ep_data, tmp_path):
    """Test the on_upload_experiment_file callback with timing."""
    ctx = copy_context()
    result = ctx.run(run_callback_on_upload_structure_file, None, "randon", "time")
    assert result is not None


def test_callback_on_upload_structure_file_alert(mocker, path_exp_ep_data, tmp_path):
    """Test the on_upload_structure_file callback with timing."""
    import dash_bootstrap_components as dbc

    from levseq_dash.app.tests.conftest import load_config_mock_string

    # Mock the data manager configuration
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": str(tmp_path)},
    }

    # Read the test CIF file and encode it for upload
    base64_contents = read_file_for_upload(path_exp_ep_data)
    cif_base64 = base64_contents[1]
    dash_upload_contents_with_error = f"{cif_base64}"

    # Time the upload callback execution
    ctx = copy_context()
    result = ctx.run(
        run_callback_on_upload_structure_file, dash_upload_contents_with_error, "filename", "last_modified"
    )
    assert result is not None
    assert isinstance(result[0], dbc.Alert)


def test_on_submit_experiment_performance(mocker, path_exp_ep_data, disk_manager_from_temp_data):
    """Test on_submit_experiment functionality with timing."""

    # Mock the singleton data manager to use our temp data manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_temp_data)

    base64_contents = read_file_for_upload(path_exp_ep_data)

    # Set up experiment parameters
    experiment_name = "Test Experiment"
    experiment_date = "2024-01-01"
    substrate = "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
    product = "C1=CC=C(C=C1)C=O"
    assay = "Fluorescence Assay"
    mutagenesis_method = MutagenesisMethod.epPCR
    experiment_doi = "10.5281/zenodo.15203754"
    additional_info = "This is a test experiment for testing."

    # Time the on_submit_experiment execution
    ctx = copy_context()
    start_time = time.time()
    result = ctx.run(
        run_callback_on_submit_experiment,
        1,  # n_clicks (> 0 to trigger submission)
        experiment_name,
        experiment_date,
        substrate,
        product,
        assay,
        mutagenesis_method,
        experiment_doi,
        additional_info,
        base64_contents[1],  # geometry (CIF)
        base64_contents[0],  # experiment CSV
    )
    execution_time = time.time() - start_time

    # Verify the callback succeeded
    assert result is not None
    assert len(result) == 4  # Should return (alert, None, None)
    assert result[0] is not None  # alert should not be None

    # Extract experiment ID from the success message
    alert_content = result[0]
    # The success message format is "Experiment with UUID: {experiment_id} has been added successfully!"
    # We can verify the alert contains success indicators
    assert hasattr(alert_content, "children") or isinstance(alert_content, (str, list))

    # Verify experiment was actually added by checking the data manager
    all_experiments = disk_manager_from_temp_data.get_all_lab_experiments_with_meta_data()
    assert len(all_experiments) > 0

    # Find our experiment by name
    our_experiment = None
    for exp in all_experiments:
        if exp.get("experiment_name") == experiment_name:
            our_experiment = exp
            break

    assert our_experiment is not None
    assert our_experiment["experiment_name"] == experiment_name

    TIME_RESULTS.append((f"on_submit_experiment {experiment_name}", execution_time))


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Skipping test on Github")
def test_print_timing_summary():
    """Print a summary of all timing results from the performance tests."""
    print("\n\n" + "=" * 50)
    print("PERFORMANCE TEST TIMING SUMMARY")
    print("=" * 50)
    for test_id, duration in TIME_RESULTS:
        print(f"  {test_id}: {duration:.4f} seconds")
