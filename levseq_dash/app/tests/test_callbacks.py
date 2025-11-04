from contextvars import copy_context

import pytest
from dash import html, no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
from dash.exceptions import CallbackException, PreventUpdate

from levseq_dash.app import global_strings as gs


def run_callback_route_page(pathname):
    from levseq_dash.app.main_app import route_page

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "url.pathname"}]}))
    return route_page(pathname=pathname)


@pytest.mark.parametrize(
    "pathname",
    [
        "/",
        gs.nav_experiment_path,
        gs.nav_upload_path,
        gs.nav_find_seq_path,
        gs.nav_about_path,
        gs.nav_explore_path,
        "any-other-random-string",
    ],
)
def test_callback_route_page(pathname, mock_load_config_from_test_data_path):
    ctx = copy_context()
    output = ctx.run(run_callback_route_page, pathname)
    assert isinstance(output, html.Div)


# ------------------------------------------------
def run_callback_update_explore_page_buttons(selected_rows):
    from levseq_dash.app.main_app import update_explore_page_buttons

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-all-experiments.selectedRows"}]}))
    return update_explore_page_buttons(selected_rows=selected_rows)


@pytest.mark.parametrize(
    "selected_rows, output_0, output_1, output_2, output_3",
    [
        ([{"experiment_id": 2}], 2, True, False, False),
        ([{"experiment_id": 2}, {"experiment_id": 4}], no_update, True, True, False),
        (None, no_update, True, True, True),
    ],
)
def test_callback_update_explore_page_buttons(
    mock_load_config_from_test_data_path, selected_rows, output_0, output_1, output_2, output_3
):
    ctx = copy_context()
    output = ctx.run(run_callback_update_explore_page_buttons, selected_rows)
    assert len(output) == 4
    assert output[0] == output_0
    assert output[1] == output_1
    assert output[2] == output_2
    assert output[3] == output_3


# ------------------------------------------------


def run_callback_enable_submit_experiment(experiment, structure, valid_substrate, valid_product):
    from levseq_dash.app.main_app import enable_submit_experiment

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-exp-upload-csv.data"}]}))
    return enable_submit_experiment(
        experiment_success=experiment,
        structure_success=structure,
        valid_substrate=valid_substrate,
        valid_product=valid_product,
    )


@pytest.mark.parametrize(
    "experiment, structure, substrate, product, result",
    [
        ("valid", "valid", True, True, False),  # Button enabled -> disabled=False
        (None, "valid", True, True, True),  # Missing experiment -> disabled=True
        ("valid", None, True, True, True),  # Missing structure -> disabled=True
        ("valid", "valid", False, True, True),  # Invalid substrate -> disabled=True
        ("valid", "valid", True, False, True),  # Invalid product -> disabled=True
        ("valid", None, False, False, True),  # Multiple invalid -> disabled=True
    ],
)
def test_callback_enable_submit_experiment_all_valid(
    mock_load_config_from_test_data_path, mocker, experiment, structure, substrate, product, result
):
    """Test enable_submit_experiment when all inputs are valid and data modification is enabled."""
    mocker.patch("levseq_dash.app.main_app.settings.is_data_modification_enabled", return_value=True)
    ctx = copy_context()
    output = ctx.run(
        run_callback_enable_submit_experiment,
        experiment=experiment,
        structure=structure,
        valid_substrate=substrate,
        valid_product=product,
    )
    assert output == result


# ------------------------------------------------
def run_callback_save_table_filter_state(filter_model):
    from levseq_dash.app.main_app import save_table_filter_state

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-all-experiments.filterModel"}]}))
    return save_table_filter_state(filter_model=filter_model)


def test_callback_save_table_filter_state(mock_load_config_from_test_data_path):
    filter_data = {"experiment_name": {"filterType": "text"}}
    ctx = copy_context()
    # it should return the same filter back
    output = ctx.run(run_callback_save_table_filter_state, filter_data)
    assert output == filter_data


def test_callback_save_table_filter_state_none(mock_load_config_from_test_data_path):
    """Test save_table_filter_state with None."""
    ctx = copy_context()
    # there should be no update with no filter set yet
    output = ctx.run(run_callback_save_table_filter_state, None)
    assert output == no_update


# ------------------------------------------------
def run_callback_on_download_selected_experiments(selected_rows):
    from levseq_dash.app.main_app import on_download_selected_experiments

    context_value.set(
        AttributeDict(**{"triggered_inputs": [{"prop_id": "id-button-download-all-experiments.n_clicks"}]})
    )
    return on_download_selected_experiments(n_clicks=1, selected_rows=selected_rows)


def test_callback_on_download_selected_experiments(disk_manager_from_test_data):
    """Test downloading selected experiments."""
    selected_rows = [
        {
            "experiment_id": "flatten_ep_processed_xy_cas",
            "experiment_name": "Test Experiment",
        }
    ]
    ctx = copy_context()
    output = ctx.run(run_callback_on_download_selected_experiments, selected_rows)

    assert output is not None
    assert output["content"] is not None
    assert "EnzEngDB_Experiments_" in output["filename"]
    assert output["filename"].endswith(".zip")


@pytest.mark.parametrize(
    "selected_rows",
    [
        None,  # no selection
        [],  # empty list
    ],
)
def test_callback_on_download_selected_experiments_no_selection(disk_manager_from_test_data, selected_rows):
    """Test downloading with no selection raises PreventUpdate."""
    ctx = copy_context()
    with pytest.raises(PreventUpdate):
        ctx.run(run_callback_on_download_selected_experiments, selected_rows)


# ------------------------------------------------
def run_callback_redirect_to_experiment_page_after_upload(experiment_id):
    from levseq_dash.app.main_app import redirect_to_experiment_page_after_upload

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-uploaded-experiment-redirect.data"}]}))
    return redirect_to_experiment_page_after_upload(experiment_id=experiment_id)


@pytest.mark.parametrize("experiment_id", ["flatten_ep_processed_xy_cas", "flatten_ssm_processed_xy_cas"])
def test_callback_redirect_to_experiment_page_after_upload(disk_manager_from_test_data, experiment_id):
    """Test redirect after experiment upload."""

    ctx = copy_context()
    output = ctx.run(run_callback_redirect_to_experiment_page_after_upload, experiment_id)

    assert len(output) == 4
    assert output[0] == gs.nav_experiment_path
    assert isinstance(output[1], html.Div)
    assert output[2] == experiment_id
    assert output[3] is None  # Clear redirect store


def test_callback_redirect_to_experiment_page_after_upload_none(disk_manager_from_test_data):
    """Test redirect when experiment_id is None."""
    ctx = copy_context()
    with pytest.raises(PreventUpdate):
        ctx.run(run_callback_redirect_to_experiment_page_after_upload, None)


# ------------------------------------------------
def run_callback_on_button_run_seq_matching(results_are_cleared):
    from levseq_dash.app.main_app import on_button_run_seq_matching

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-button-run-seq-matching.n_clicks"}]}))
    return on_button_run_seq_matching(n_clicks=1, results_are_cleared=results_are_cleared)


def test_callback_on_button_run_seq_matching(mock_load_config_from_test_data_path):
    """Test on_button_run_seq_matching callback."""
    ctx = copy_context()
    output = ctx.run(run_callback_on_button_run_seq_matching, False)
    assert len(output) == 3
    assert output[0] == []  # Clear alert
    assert output[2] is True  # Set flag to true


def test_callback_on_button_run_seq_matching_already_cleared(mock_load_config_from_test_data_path):
    """Test on_button_run_seq_matching when already cleared."""
    ctx = copy_context()
    with pytest.raises(PreventUpdate):
        ctx.run(run_callback_on_button_run_seq_matching, True)
