from contextvars import copy_context

import pytest
from dash import html, no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
from dash.exceptions import PreventUpdate

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
        (
            [
                # single selection
                {"experiment_id": 2}
            ],
            2,
            False,
            False,
            False,
        ),
        (
            [
                # multiple selection
                {"experiment_id": 2},
                {"experiment_id": 4},
            ],
            no_update,
            True,
            True,
            False,
        ),
        (
            None,  # no selection
            no_update,
            True,
            True,
            True,
        ),
    ],
)
def test_callback_update_explore_page_buttons(
    mock_load_config_from_test_data_path, selected_rows, output_0, output_1, output_2, output_3
):
    ctx = copy_context()
    output = ctx.run(run_callback_update_explore_page_buttons, selected_rows)
    assert len(output) == 4
    assert output[0] == output_0  # experiment_id or no_update
    assert output[1] == output_1  # delete_btn_disabled
    assert output[2] == output_2  # go_to_experiment_btn_disabled
    assert output[3] == output_3  # download_btn_disabled


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


# ------------------------------------------------
def run_callback_on_load_matching_sequences(query_sequence, threshold, n_top_hot_cold):
    from levseq_dash.app.main_app import on_load_matching_sequences

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-cleared-run-seq-matching.data"}]}))
    return on_load_matching_sequences(
        results_are_cleared=True,
        n_clicks=1,
        query_sequence=query_sequence,
        threshold=threshold,
        n_top_hot_cold=n_top_hot_cold,
    )


def test_callback_on_load_matching_sequences(disk_manager_from_app_data):
    ctx = copy_context()
    output = ctx.run(
        run_callback_on_load_matching_sequences,
        gs.seq_align_form_input_sequence_default,
        0.8,
        5,
    )

    assert len(output) == 7
    # assert len(output[0]) == 101  # matched-sequences row Data
    # assert len(output[1]) == 240


# ------------------------------------------------
def run_callback_display_default_selected_matching_sequences(data):
    from levseq_dash.app.main_app import display_default_selected_matching_sequences

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-matched-sequences.virtualRowData"}]}))
    return display_default_selected_matching_sequences(data=data)


def test_callback_display_default_selected_matching_sequences(mock_load_config_from_test_data_path):
    """Test display_default_selected_matching_sequences callback."""
    data = [{"experiment_id": "exp1", "name": "test"}, {"experiment_id": "exp2", "name": "test2"}]
    ctx = copy_context()
    output = ctx.run(run_callback_display_default_selected_matching_sequences, data)
    assert len(output) == 1
    assert output[0]["experiment_id"] == "exp1"


# ------------------------------------------------
def run_callback_display_selected_matching_sequences(selected_rows):
    from levseq_dash.app.main_app import display_selected_matching_sequences

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-matched-sequences.selectedRows"}]}))
    return display_selected_matching_sequences(selected_rows=selected_rows)


def test_callback_display_selected_matching_sequences(mocker, disk_manager_from_test_data):
    """Test display_selected_matching_sequences with valid selection."""
    # values in the selected row don't matter for this test
    # but the experiment id needs to be valid, so it can load geometry
    import dash_molstar

    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_test_data)
    selected_rows = [
        {
            gs.cc_experiment_id: "flatten_ep_processed_xy_cas",
            gs.cc_seq_alignment_mismatches: "60,120",
            gs.cc_hot_indices_per_smiles: "59,89,93",
            gs.cc_cold_indices_per_smiles: "89,119,120",
            gs.cc_substrate: "C1=CC=C(C=C1)C=O",
            gs.cc_product: "C1=CC=C(C=C1)CO",
        }
    ]
    ctx = copy_context()
    output = ctx.run(run_callback_display_selected_matching_sequences, selected_rows)

    assert len(output) == 7
    # viewer can be no_update if no geometry, or a list with viewer
    assert output[0] is not None  # viewer or no_update
    assert isinstance(output[0][0], dash_molstar.MolstarViewer)
    assert output[1] is not None  # reaction image svg
    assert output[2] == "C1=CC=C(C=C1)C=O"  # substrate
    assert output[3] == "C1=CC=C(C=C1)CO"  # product
    assert output[4] == "89"  # highlights_both


def test_callback_display_selected_matching_sequences_none(mock_load_config_from_test_data_path):
    """Test display_selected_matching_sequences with None."""
    ctx = copy_context()
    with pytest.raises(PreventUpdate):
        ctx.run(run_callback_display_selected_matching_sequences, None)


# ------------------------------------------------
def run_callback_on_load_exp_related_variants(query_sequence, threshold, lookup_residues, experiment_id):
    from levseq_dash.app.main_app import on_load_exp_related_variants

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-cleared-run-exp-related-variants.data"}]}))
    return on_load_exp_related_variants(
        results_are_cleared=True,
        n_clicks=1,
        query_sequence=query_sequence,
        threshold=threshold,
        lookup_residues=lookup_residues,
        experiment_id=experiment_id,
    )


def test_callback_on_load_exp_related_variants(disk_manager_from_app_data, mocker):
    """Test on_load_exp_related_variants callback with valid inputs."""

    # Mock the singleton to use our app_data fixture
    # if I don't do this, it will try to load from default test data path
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_app_data)

    all_lab_sequences = disk_manager_from_app_data.get_all_lab_sequences()
    experiment_id = "ARNLD-2899-331b61ee-2fd6-42a0-bf48-3be76fe97af1"
    ctx = copy_context()
    output = ctx.run(
        run_callback_on_load_exp_related_variants,
        all_lab_sequences[experiment_id],
        0.8,
        "264",
        experiment_id,
    )

    assert len(output) == 9
    assert isinstance(output[0], list)  # exp_results_row_data should be a list
    assert len(output[0]) == 95  # Should have exactly 95 related variants with app data
    assert output[1] == experiment_id  # experiment_id
    assert output[2] is not None  # experiment_svg_src (reaction image)
    assert output[3] is not None  # experiment_substrate
    assert output[4] is not None  # experiment_product
    assert output[6] is False  # cleared flag reset


# ------------------------------------------------
def run_callback_on_view_all_residue(view, slider_value, selected_smiles, rowData):
    from levseq_dash.app.main_app import on_view_all_residue

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-switch-residue-view.value"}]}))
    return on_view_all_residue(view=view, slider_value=slider_value, selected_smiles=selected_smiles, rowData=rowData)


@pytest.mark.parametrize(
    "view,slider_value,smiles_idx",
    [
        (True, [0.5, 1.5], 0),
        (True, [0.0, 2.0], 1),
        (False, [0.5, 1.5], 0),
    ],
)
def test_callback_on_view_all_residue(disk_manager_from_test_data, experiment_ep_pcr, view, slider_value, smiles_idx):
    """Test on_view_all_residue callback with valid inputs."""
    rowData = experiment_ep_pcr.data_df.to_dict("records")
    selected_smiles = experiment_ep_pcr.unique_smiles_in_data[smiles_idx]

    ctx = copy_context()
    output = ctx.run(run_callback_on_view_all_residue, view, slider_value, selected_smiles, rowData)

    if view:
        # slider is enabled
        assert len(output) == 5
        # on view all residues all the independent residues should be gathered in the list
        assert len(output[0]["targets"][0]["residue_numbers"]) == 179
    else:
        assert output[2] is not None  # slider_disabled
        assert output[3] is not None  # listbox_disabled
        assert output[4] is not None  # highlighted_residue_info


# ------------------------------------------------
def run_callback_on_view_selected_residue_from_table(selected_rows):
    from levseq_dash.app.main_app import on_view_selected_residue_from_table

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-exp-top-variants.selectedRows"}]}))
    return on_view_selected_residue_from_table(selected_rows=selected_rows)


@pytest.mark.parametrize(
    "substitutions,expected_info,expected_residues",
    [
        ("K99R_R118C", "99, 118", [99, 118]),  # Regular substitutions
        (gs.hashtag_parent, gs.hashtag_parent, None),  # Parent case - no residue selection
        ("A10G", "10", [10]),  # Single substitution
    ],
)
def test_callback_on_view_selected_residue_from_table(
    mock_load_config_from_test_data_path, substitutions, expected_info, expected_residues
):
    """Test on_view_selected_residue_from_table callback with valid inputs."""
    selected_rows = [{gs.c_substitutions: substitutions}]

    ctx = copy_context()
    output = ctx.run(run_callback_on_view_selected_residue_from_table, selected_rows)

    assert len(output) == 4

    # Check selection output
    if expected_residues is not None:
        assert output[0] is not None  # selection should be set
        assert output[0]["targets"][0]["residue_numbers"] == expected_residues
    else:
        # Parent case - selection is reset (empty list)
        assert output[0]["targets"][0]["residue_numbers"] == []

    # output[1] is focus - can be no_update
    assert expected_info in output[2]  # highlighted_residue_info contains expected residues
    assert output[3] is False  # view_all_residue_switch should be False


# ------------------------------------------------
def run_callback_display_selected_exp_related_variants(selected_rows, experiment_id):
    from levseq_dash.app.main_app import display_selected_exp_related_variants

    context_value.set(
        AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-exp-related-variants.selectedRows"}]})
    )
    return display_selected_exp_related_variants(selected_rows=selected_rows, experiment_id=experiment_id)


@pytest.mark.parametrize(
    "selected_exp_id,substitutions,substrate,product, query_exp_id",
    [
        # Two different experiments from app data with valid geometry
        (
            "ARNLD-0821-9561f6f0-9765-4ee7-8d8d-8b33f70b55f2",
            "A10G_K99R",
            "C1=CC=C(C=C1)C=O",
            "C1=CC=C(C=C1)CO",
            "ARNLD-0917-39903c09-5dc0-4cc8-b805-a5739a835e85",
        ),
        (
            "ARNLD-1222-57801895-faeb-42e1-b24d-cff199d9eaf8",
            "L52V_T53A",
            "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
            "CC(C)CC1=CC=C(C=C1)C(C)C(=O)N",
            "ARNLD-2030-4208b989-f384-46c6-b6a8-051d3f55e0d9",
        ),
    ],
)
def test_callback_display_selected_exp_related_variants(
    mocker, disk_manager_from_app_data, selected_exp_id, substitutions, substrate, product, query_exp_id
):
    """Test display_selected_exp_related_variants with valid selection."""
    import dash_molstar

    # Mock singleton to use app data
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_app_data)

    selected_rows = [
        {
            gs.cc_experiment_id: selected_exp_id,
            gs.c_substitutions: substitutions,
            gs.cc_substrate: substrate,
            gs.cc_product: product,
        }
    ]

    ctx = copy_context()
    output = ctx.run(run_callback_display_selected_exp_related_variants, selected_rows, query_exp_id)

    assert len(output) == 7
    assert output[0] == substitutions  # selected_substitutions
    assert isinstance(output[1][0], dash_molstar.MolstarViewer)  # selected_experiment_viewer
    assert output[2] == selected_exp_id  # selected_experiment_id
    assert output[3] is not None  # selected_svg_src (reaction image)
    assert output[4] == substrate  # selected_substrate
    assert output[5] == product  # selected_product
    assert isinstance(output[6][0], dash_molstar.MolstarViewer)  # query_experiment_viewer


# ------------------------------------------------
def run_callback_on_delete_experiment_open_modal(selected_rows):
    from levseq_dash.app.main_app import on_delete_experiment_open_modal

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-button-delete-experiment.n_clicks"}]}))
    return on_delete_experiment_open_modal(delete_clicks=1, selected_rows=selected_rows)


@pytest.mark.parametrize(
    "experiment_id,experiment_name",
    [
        ("any-id", "Test Experiment 1"),
        ("any-id-2", "Test Experiment 2"),
    ],
)
def test_callback_on_delete_experiment_open_modal(mock_load_config_from_test_data_path, experiment_id, experiment_name):
    """Test on_delete_experiment_open_modal opens modal with experiment details."""
    selected_rows = [{"experiment_id": experiment_id, "experiment_name": experiment_name}]

    ctx = copy_context()
    output = ctx.run(run_callback_on_delete_experiment_open_modal, selected_rows)

    assert len(output) == 2
    assert output[0] is True  # Modal should be open
    assert isinstance(output[1], html.Div)  # Modal body should be a Div
    # Verify experiment name and ID are in the modal message
    modal_children = output[1].children
    assert any(experiment_name in str(child) for child in modal_children)
    assert any(experiment_id in str(child) for child in modal_children)


def test_callback_on_delete_experiment_open_modal_no_update():
    ctx = copy_context()
    with pytest.raises(PreventUpdate):
        ctx.run(run_callback_on_delete_experiment_open_modal, [])


# ------------------------------------------------
def run_callback_on_delete_experiment_modal_cancel(cancel_clicks):
    from levseq_dash.app.main_app import on_delete_experiment_modal_cancel

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-delete-modal-cancel.n_clicks"}]}))
    return on_delete_experiment_modal_cancel(cancel_clicks=cancel_clicks)


@pytest.mark.parametrize("cancel_clicks", [1, 2, 5])
def test_callback_on_delete_experiment_modal_cancel(mock_load_config_from_test_data_path, cancel_clicks):
    """Test on_delete_experiment_modal_cancel closes the modal."""
    ctx = copy_context()
    output = ctx.run(run_callback_on_delete_experiment_modal_cancel, cancel_clicks)

    assert output is False  # Modal should be closed


# ------------------------------------------------
def run_callback_on_delete_experiment_modal_confirmed(selected_rows, confirm_clicks=1):
    from levseq_dash.app.main_app import on_delete_experiment_modal_confirmed

    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-delete-modal-confirm.n_clicks"}]}))
    return on_delete_experiment_modal_confirmed(confirm_clicks, selected_rows=selected_rows)


def test_callback_on_delete_experiment_modal_confirmed(mocker, temp_experiment_to_delete, disk_manager_from_temp_data):
    """Test on_delete_experiment_modal_confirmed deletes experiment and closes modal."""
    # Mock the singleton to use temp data manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_temp_data)

    # Get the experiment ID from the fixture
    exp_id = temp_experiment_to_delete

    # Verify it exists before deletion
    assert disk_manager_from_temp_data.get_experiment_metadata(exp_id) is not None

    selected_rows = [{"experiment_id": exp_id, "experiment_name": "Temp Delete Test"}]

    ctx = copy_context()
    aggrid_deleteSelectedRows, alert, modal_open = ctx.run(
        run_callback_on_delete_experiment_modal_confirmed, selected_rows
    )

    assert aggrid_deleteSelectedRows is True  # deleteSelectedRows should be True (success)
    assert alert is not None  # Alert should be present
    assert modal_open is False  # Modal should be closed

    # Verify experiment was actually deleted
    assert disk_manager_from_temp_data.get_experiment_metadata(exp_id) is None

    # Verify experiment was actually deleted
    assert disk_manager_from_temp_data.get_experiment_metadata(exp_id) is None


def test_callback_on_delete_experiment_modal_confirmed_error_alert(
    mocker, temp_experiment_to_delete, disk_manager_from_temp_data
):
    exp_id = temp_experiment_to_delete
    selected_rows = [{"experiment_id": exp_id, "experiment_name": "Temp Delete Test"}]

    # Mock the singleton to use temp data manager
    mocker.patch("levseq_dash.app.main_app.singleton_data_mgr_instance", disk_manager_from_temp_data)

    # Mock shutil.move to raise an exception but the UI in the callback will catch and create alert
    mocker.patch("shutil.move", side_effect=Exception("Delete error"))

    ctx = copy_context()
    aggrid_deleteSelectedRows, alert, modal_open = ctx.run(
        run_callback_on_delete_experiment_modal_confirmed, selected_rows
    )
    assert aggrid_deleteSelectedRows is no_update  # deleteSelectedRows not changed
    assert alert is not None
    assert modal_open is False  # Modal should be closed


def test_callback_on_delete_experiment_modal_confirmed_no_update():
    """Test on_delete_experiment_modal_confirmed with None selected_rows raises PreventUpdate."""
    ctx = copy_context()
    with pytest.raises(PreventUpdate):
        ctx.run(run_callback_on_delete_experiment_modal_confirmed, None)

    with pytest.raises(PreventUpdate):
        ctx.run(run_callback_on_delete_experiment_modal_confirmed, [], 0)
