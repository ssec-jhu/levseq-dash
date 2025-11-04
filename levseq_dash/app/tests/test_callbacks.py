from contextvars import copy_context

import pytest
from dash import html, no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
from dash.exceptions import CallbackException, PreventUpdate

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import graphs


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


# ------------------------------------------------
def run_callback_load_explore_page(filter_store):
    from levseq_dash.app.main_app import load_explore_page

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-all-experiments.columnDefs"}]}))
    return load_explore_page(temp_text=None, filter_store=filter_store)


def test_callback_load_explore_page(disk_manager_from_test_data):
    """Test load_explore_page callback."""
    ctx = copy_context()
    output = ctx.run(run_callback_load_explore_page, None)
    assert len(output) == 2
    assert isinstance(output[0], list)  # rowData
    assert len(output[0]) > 0  # Should have experiments


def test_callback_load_explore_page_with_filter(disk_manager_from_test_data):
    """Test load_explore_page with filter store."""
    filter_data = {"experiment_name": {"filterType": "text", "type": "contains", "filter": "test"}}
    ctx = copy_context()
    output = ctx.run(run_callback_load_explore_page, filter_data)
    assert output[1] == filter_data  # Filter should be preserved


# ------------------------------------------------
def run_callback_set_assay_list(assay_list):
    from levseq_dash.app.main_app import set_assay_list

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-list-assay.options"}]}))
    return set_assay_list(assay_list=assay_list)


def test_callback_set_assay_list(disk_manager_from_test_data):
    """Test set_assay_list callback."""
    ctx = copy_context()
    output = ctx.run(run_callback_set_assay_list, [])
    assert len(output) == 3
    assert output[0] == "Mass Spectrometry"


# ------------------------------------------------
def run_callback_validate_substrate_smiles(substrate):
    from levseq_dash.app.main_app import validate_substrate_smiles

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-input-substrate.value"}]}))
    return validate_substrate_smiles(substrate=substrate)


def run_callback_validate_product_smiles(product):
    from levseq_dash.app.main_app import validate_product_smiles

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-input-product.value"}]}))
    return validate_product_smiles(product=product)


@pytest.mark.parametrize(
    "smiles, valid",
    [
        ("C1=CC=CC=C1", True),  # no selection
        ("invalid_smiles_123", False),
    ],
)
def test_callback_validate_substrate_smiles(mock_load_config_from_test_data_path, smiles, valid):
    """Test validate_substrate_smiles  and validate_product_smiles."""
    ctx = copy_context()
    output = ctx.run(run_callback_validate_substrate_smiles, smiles)
    assert output[0] == valid

    output = ctx.run(run_callback_validate_product_smiles, smiles)
    assert output[0] == valid


# ------------------------------------------------
def run_callback_toggle_sidebar(sidebar_class):
    from levseq_dash.app.main_app import toggle_sidebar

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-menu-icon.n_clicks"}]}))
    return toggle_sidebar(toggle_clicks=1, sidebar_class=sidebar_class)


@pytest.mark.parametrize(
    "sidebar_class, output",
    [
        ("thin-sidebar expanded", "thin-sidebar collapsed"),  # no selection
        ("thin-sidebar collapsed", "thin-sidebar expanded"),
    ],
)
def test_callback_toggle_sidebar_collapse(mock_load_config_from_test_data_path, sidebar_class, output):
    """Test toggle_sidebar to collapse."""
    ctx = copy_context()
    output = ctx.run(run_callback_toggle_sidebar, sidebar_class)
    assert output == output


# ------------------------------------------------
def run_callback_update_heatmap(selected_plate, selected_smiles, selected_stat_property, rowData, store_data):
    from levseq_dash.app.main_app import update_heatmap

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-list-plates.value"}]}))
    return update_heatmap(
        selected_plate=selected_plate,
        selected_smiles=selected_smiles,
        selected_stat_property=selected_stat_property,
        rowData=rowData,
        store_data=store_data,
    )


@pytest.mark.parametrize(
    "plate, smiles, sel_property",
    [
        (0, 0, 1),  # different property selected
        (0, 1, 0),  # different smiles selected
        (1, 0, 0),  # different plate selected
    ],
)
def test_callback_update_heatmap(disk_manager_from_test_data, experiment_ep_pcr, plate, smiles, sel_property):
    """Test update_heatmap callback."""

    rowData = experiment_ep_pcr.data_df.to_dict("records")
    store_data = {
        "heatmap": {
            "plate": experiment_ep_pcr.plates[0],
            "smiles": experiment_ep_pcr.unique_smiles_in_data[0],
            "property": gs.experiment_heatmap_properties_list[0],
        }
    }

    new_plate = experiment_ep_pcr.plates[plate]
    new_smiles = experiment_ep_pcr.unique_smiles_in_data[smiles]
    new_property = gs.experiment_heatmap_properties_list[sel_property]

    ctx = copy_context()
    output = ctx.run(
        run_callback_update_heatmap,
        new_plate,
        new_smiles,
        new_property,
        rowData,
        store_data,
    )
    assert len(output) == 4
    assert output[0] is not None  # Figure
    # updated store
    assert output[3] == {"heatmap": {"plate": new_plate, "smiles": new_smiles, "property": new_property}}


# ------------------------------------------------
def run_callback_update_rank_plot(selected_plate, selected_smiles, rowData, store_data):
    from levseq_dash.app.main_app import update_rank_plot

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-list-plates-ranking-plot.value"}]}))
    return update_rank_plot(
        selected_plate=selected_plate, selected_smiles=selected_smiles, rowData=rowData, store_data=store_data
    )


@pytest.mark.parametrize(
    "plate, smiles",
    [(0, 1), (1, 0), (1, 1)],
)
def test_callback_update_rank_plot(disk_manager_from_test_data, experiment_ep_pcr, plate, smiles):
    """Test update_rank_plot callback."""
    rowData = experiment_ep_pcr.data_df.to_dict("records")

    store_data = {
        "rank_plot": {
            "plate": experiment_ep_pcr.plates[0],
            "smiles": experiment_ep_pcr.unique_smiles_in_data[0],
        }
    }

    new_plate = experiment_ep_pcr.plates[plate]
    new_smiles = experiment_ep_pcr.unique_smiles_in_data[smiles]

    ctx = copy_context()
    output = ctx.run(run_callback_update_rank_plot, new_plate, new_smiles, rowData, store_data)

    assert len(output) == 2
    assert output[0] is not None  # Figure
    # make sure store is updated
    assert output[1] == {"rank_plot": {"plate": new_plate, "smiles": new_smiles}}


# ------------------------------------------------
def run_callback_update_ssm_plot(selected_residue, selected_smiles, rowData, store_data):
    from levseq_dash.app.main_app import update_ssm_plot

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-list-ssm-residue-positions.value"}]}))
    return update_ssm_plot(
        selected_residue=selected_residue, selected_smiles=selected_smiles, rowData=rowData, store_data=store_data
    )


@pytest.mark.parametrize(
    "residue",
    [1, 2, 3, 4],
)
def test_callback_update_ssm_plot(disk_manager_from_test_data, experiment_ssm, residue):
    """Test update_ssm_plot callback."""

    df = experiment_ssm.data_df
    rowData = df.to_dict("records")

    list_ssm_positions = graphs.extract_single_site_mutations(df)

    store_data = {"ssm_plot": {"residue": list_ssm_positions[0], "smiles": experiment_ssm.unique_smiles_in_data[0]}}

    new_residue = list_ssm_positions[residue]

    ctx = copy_context()
    output = ctx.run(
        run_callback_update_ssm_plot, new_residue, experiment_ssm.unique_smiles_in_data[0], rowData, store_data
    )

    assert len(output) == 2
    assert output[0] is not None  # Figure
    # check the store value
    assert output[1] == {"ssm_plot": {"residue": new_residue, "smiles": experiment_ssm.unique_smiles_in_data[0]}}
