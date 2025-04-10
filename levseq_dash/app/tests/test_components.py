import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar
import pytest
from dash import html

from levseq_dash.app import column_definitions as cd
from levseq_dash.app import (
    components,
    graphs,
    utils,
)
from levseq_dash.app import global_strings as gs
from levseq_dash.app.layout import (
    layout_bars,
    layout_experiment,
    layout_landing,
    layout_matching_sequences,
    layout_upload,
)


def test_get_label():
    assert isinstance(components.get_label_fixed_for_form("random_string"), dbc.Label)


def test_get_top_variant_column_defs(experiment_ep_pcr_with_user_cas):
    df_filtered_with_ratio = utils.calculate_group_mean_ratios_per_cas_and_plate(
        experiment_ep_pcr_with_user_cas.data_df
    )
    d = cd.get_top_variant_column_defs(df_filtered_with_ratio)
    assert len(d) == 6


def test_get_matched_sequences_column_defs():
    d = cd.get_matched_sequences_column_defs()
    assert len(d) == 18


def test_get_matched_sequences_exp_hot_cold_data_column_defs():
    d = cd.get_matched_sequences_exp_hot_cold_data_column_defs()
    assert len(d) == 9


# def test_get_all_experiments_column_defs(experiment_ep_pcr_with_user_cas):
#     #TODO
#     df = data_mgr.get_lab_experiments_with_meta_data()
#     d = components.get_all_experiments_column_defs(df)
#     assert len(d) == 6


def test_get_table_experiment_top_variants():
    table = components.get_table_experiment_top_variants()
    assert isinstance(table, dag.AgGrid)  # Ensure it's an AgGrid component
    assert table.id == "id-table-exp-top-variants"  # Check ID
    assert "rowSelection" in table.dashGridOptions  # Ensure row selection exists
    assert table.dashGridOptions["rowSelection"] == "single"  # Should be single selection


# Test if `get_table_all_experiments` returns a valid AgGrid component
def test_get_table_all_experiments():
    table = components.get_table_all_experiments()
    assert isinstance(table, dag.AgGrid)  # Ensure it's an AgGrid component
    assert table.id == "id-table-all-experiments"  # Check ID
    assert "rowSelection" in table.dashGridOptions  # Ensure row selection exists
    assert table.dashGridOptions["rowSelection"] == "multiple"  # Should be multiple selection


# Test if `get_protein_viewer` returns a valid MolstarViewer component
def test_get_protein_viewer():
    viewer = components.get_protein_viewer()
    assert isinstance(viewer, dash_molstar.MolstarViewer)  # Ensure it's a MolstarViewer
    assert viewer.id == "id-viewer"  # Check ID
    # assert viewer.style["height"] == "600px"  # Ensure height is set


def test_get_form():
    assert isinstance(layout_upload.get_form(), dbc.Form)


def test_get_navar():
    assert isinstance(layout_bars.get_navbar(), html.Div)


def test_get_sidebar():
    assert isinstance(layout_bars.get_sidebar(), html.Div)


def test_get_landing_page():
    assert isinstance(layout_landing.get_landing_page(), html.Div)


def test_get_experiment_page():
    assert isinstance(layout_experiment.get_experiment_page(), html.Div)


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("N56T_T45R_D32R", "N56T<br>T45R<br>D32R"),
        ("F67R_A5N", "F67R<br>A5N"),
        ("N56T_T45R_D32R_Y78T", "4Mut*"),  # More than 3 mutations
        ("X_Y_Z_W_V", "5Mut*"),  # More than 3 mutations
        ("single", "single"),  # Only one mutation
    ],
)
def test_format_mutation_annotation(input_text, expected_output):
    assert graphs.format_mutation_annotation(input_text) == expected_output


@pytest.mark.parametrize(
    "cas, plate, property",
    [
        ("345905-97-7", "20240422-ParLQ-ep1-300-1", gs.c_fitness_value),
        ("345905-97-7", "20240422-ParLQ-ep1-300-2", gs.c_fitness_value),
        ("345905-97-7", "20240422-ParLQ-ep1-500-1", gs.c_fitness_value),
        ("345905-97-7", "20240422-ParLQ-ep1-500-2", gs.c_fitness_value),
        ("345905-97-7", "20240502-ParLQ-ep2-300-1", gs.c_fitness_value),
        ("345905-97-7", "20240502-ParLQ-ep2-300-2", gs.c_fitness_value),
        ("345905-97-7", "20240502-ParLQ-ep2-300-3", gs.c_fitness_value),
        ("345905-97-7", "20240502-ParLQ-ep2-500-1", gs.c_fitness_value),
        ("345905-97-7", "20240502-ParLQ-ep2-500-2", gs.c_fitness_value),
        ("345905-97-7", "20240502-ParLQ-ep2-500-3", gs.c_fitness_value),
        ("395683-37-1", "20240422-ParLQ-ep1-300-1", gs.c_fitness_value),
        ("395683-37-1", "20240422-ParLQ-ep1-300-2", gs.c_fitness_value),
        ("395683-37-1", "20240422-ParLQ-ep1-500-1", gs.c_fitness_value),
        ("395683-37-1", "20240422-ParLQ-ep1-500-2", gs.c_fitness_value),
        ("395683-37-1", "20240502-ParLQ-ep2-300-1", gs.c_fitness_value),
        ("395683-37-1", "20240502-ParLQ-ep2-300-2", gs.c_fitness_value),
        ("395683-37-1", "20240502-ParLQ-ep2-300-3", gs.c_fitness_value),
        ("395683-37-1", "20240502-ParLQ-ep2-500-1", gs.c_fitness_value),
        ("395683-37-1", "20240502-ParLQ-ep2-500-2", gs.c_fitness_value),
        ("395683-37-1", "20240502-ParLQ-ep2-500-3", gs.c_fitness_value),
        ("345905-97-7", "20240422-ParLQ-ep1-300-1", gs.c_alignment_probability),
        ("345905-97-7", "20240422-ParLQ-ep1-300-2", gs.c_alignment_probability),
        ("345905-97-7", "20240422-ParLQ-ep1-500-1", gs.c_alignment_probability),
        ("345905-97-7", "20240422-ParLQ-ep1-500-2", gs.c_alignment_probability),
        ("345905-97-7", "20240502-ParLQ-ep2-300-1", gs.c_alignment_probability),
        ("345905-97-7", "20240502-ParLQ-ep2-300-2", gs.c_alignment_probability),
        ("345905-97-7", "20240502-ParLQ-ep2-300-3", gs.c_alignment_probability),
        ("345905-97-7", "20240502-ParLQ-ep2-500-1", gs.c_alignment_probability),
        ("345905-97-7", "20240502-ParLQ-ep2-500-2", gs.c_alignment_probability),
        ("345905-97-7", "20240502-ParLQ-ep2-500-3", gs.c_alignment_probability),
        ("395683-37-1", "20240422-ParLQ-ep1-300-1", gs.c_alignment_probability),
        ("395683-37-1", "20240422-ParLQ-ep1-300-2", gs.c_alignment_probability),
        ("395683-37-1", "20240422-ParLQ-ep1-500-1", gs.c_alignment_probability),
        ("395683-37-1", "20240422-ParLQ-ep1-500-2", gs.c_alignment_probability),
        ("395683-37-1", "20240502-ParLQ-ep2-300-1", gs.c_alignment_probability),
        ("395683-37-1", "20240502-ParLQ-ep2-300-2", gs.c_alignment_probability),
        ("395683-37-1", "20240502-ParLQ-ep2-300-3", gs.c_alignment_probability),
        ("395683-37-1", "20240502-ParLQ-ep2-500-1", gs.c_alignment_probability),
        ("395683-37-1", "20240502-ParLQ-ep2-500-2", gs.c_alignment_probability),
        ("395683-37-1", "20240502-ParLQ-ep2-500-3", gs.c_alignment_probability),
        ("345905-97-7", "20240422-ParLQ-ep1-300-1", gs.c_alignment_count),
        ("345905-97-7", "20240422-ParLQ-ep1-300-2", gs.c_alignment_count),
        ("345905-97-7", "20240422-ParLQ-ep1-500-1", gs.c_alignment_count),
        ("345905-97-7", "20240422-ParLQ-ep1-500-2", gs.c_alignment_count),
        ("345905-97-7", "20240502-ParLQ-ep2-300-1", gs.c_alignment_count),
        ("345905-97-7", "20240502-ParLQ-ep2-300-2", gs.c_alignment_count),
        ("345905-97-7", "20240502-ParLQ-ep2-300-3", gs.c_alignment_count),
        ("345905-97-7", "20240502-ParLQ-ep2-500-1", gs.c_alignment_count),
        ("345905-97-7", "20240502-ParLQ-ep2-500-2", gs.c_alignment_count),
        ("345905-97-7", "20240502-ParLQ-ep2-500-3", gs.c_alignment_count),
        ("395683-37-1", "20240422-ParLQ-ep1-300-1", gs.c_alignment_count),
        ("395683-37-1", "20240422-ParLQ-ep1-300-2", gs.c_alignment_count),
        ("395683-37-1", "20240422-ParLQ-ep1-500-1", gs.c_alignment_count),
        ("395683-37-1", "20240422-ParLQ-ep1-500-2", gs.c_alignment_count),
        ("395683-37-1", "20240502-ParLQ-ep2-300-1", gs.c_alignment_count),
        ("395683-37-1", "20240502-ParLQ-ep2-300-2", gs.c_alignment_count),
        ("395683-37-1", "20240502-ParLQ-ep2-300-3", gs.c_alignment_count),
        ("395683-37-1", "20240502-ParLQ-ep2-500-1", gs.c_alignment_count),
        ("395683-37-1", "20240502-ParLQ-ep2-500-2", gs.c_alignment_count),
        ("395683-37-1", "20240502-ParLQ-ep2-500-3", gs.c_alignment_count),
    ],
)
def test_creat_heatmap_figure_general(experiment_ep_pcr, cas, plate, property):
    df = experiment_ep_pcr.data_df
    fig = graphs.creat_heatmap(df, plate_number=plate, property=property, cas_number=cas)

    # must have annotations
    annotations = fig["data"][0]["text"]
    assert annotations.shape == (8, 12)
    # check hover date
    hover = fig["data"][0]["hovertemplate"]
    assert "Mut:" in hover
    assert "Well:" in hover

    custom_data = fig["data"][0]["customdata"]
    assert custom_data.shape == (8, 12)

    # Check if the colorbar is placed at the top
    assert fig.layout.coloraxis.colorbar.orientation == "h"  # Horizontal colorbar

    # Check margin removal
    assert fig.layout.margin.l == 0
    assert fig.layout.margin.r == 0
    assert fig.layout.margin.b == 0


@pytest.mark.parametrize(
    "cas, plate, mutation,i,j",
    [
        ("345905-97-7", "20240422-ParLQ-ep1-300-1", "A14G", 4, 3),
        ("345905-97-7", "20240422-ParLQ-ep1-300-2", "Y185N", 2, 5),
        ("345905-97-7", "20240422-ParLQ-ep1-500-1", "L59Q", 4, 10),
        ("345905-97-7", "20240422-ParLQ-ep1-500-2", "K87E", 2, 0),
        ("345905-97-7", "20240502-ParLQ-ep2-300-1", "G189S", 0, 4),
        ("345905-97-7", "20240502-ParLQ-ep2-300-2", "K39E", 1, 4),
        ("345905-97-7", "20240502-ParLQ-ep2-300-3", "L173S", -1, -1),
        ("345905-97-7", "20240502-ParLQ-ep2-500-1", "V127A", 3, 3),
        ("345905-97-7", "20240502-ParLQ-ep2-500-2", "K120R", 4, 5),
        ("345905-97-7", "20240502-ParLQ-ep2-500-3", "F89L", 3, 5),
        ("395683-37-1", "20240422-ParLQ-ep1-300-1", "V28E", 4, 3),
        ("395683-37-1", "20240422-ParLQ-ep1-300-2", "F70L", 2, 5),
        ("395683-37-1", "20240422-ParLQ-ep1-500-1", "I67N", 4, 0),
        ("395683-37-1", "20240422-ParLQ-ep1-500-2", "K155E", 2, 0),
        ("395683-37-1", "20240502-ParLQ-ep2-300-1", "L97S", 0, 4),
        ("395683-37-1", "20240502-ParLQ-ep2-300-2", "E164D", 2, 7),
        ("395683-37-1", "20240502-ParLQ-ep2-300-3", "D128N", -1, -1),
        ("395683-37-1", "20240502-ParLQ-ep2-500-1", "L82P", 3, 3),
        # ("395683-37-1", "20240502-ParLQ-ep2-500-2", "L59P", 3, 1),
        ("395683-37-1", "20240502-ParLQ-ep2-500-3", "L82Q", 3, 5),
    ],
)
def test_creat_heatmap_figure_data(experiment_ep_pcr, cas, plate, mutation, i, j):
    df = experiment_ep_pcr.data_df
    fig = graphs.creat_heatmap(df, plate_number=plate, property=gs.c_fitness_value, cas_number=cas)

    # mutations should appear in custom data
    assert mutation in fig["data"][0]["customdata"]

    # must have annotations
    annotations = fig["data"][0]["text"]
    assert any(mutation in text for text in annotations)

    # Ensure 4Mut* appears where necessary
    if i == -1 and j == -1:
        assert not any("4Mut*" in text for text in annotations)
    else:
        assert annotations[i][j] == "4Mut*"


def test_get_seq_align_form():
    assert isinstance(layout_matching_sequences.get_seq_align_form(), html.Div)


def test_get_seq_align_layout():
    assert isinstance(layout_matching_sequences.get_seq_align_layout(), html.Div)
