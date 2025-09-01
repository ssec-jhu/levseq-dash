import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar
import pytest
from dash import html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import column_definitions as cd
from levseq_dash.app.components import graphs, widgets
from levseq_dash.app.components.layout import (
    layout_about,
    layout_bars,
    layout_experiment,
    layout_explore,
    layout_landing,
    layout_matching_sequences,
    layout_upload,
)


def test_get_label():
    assert isinstance(widgets.get_label_fixed_for_form("random_string"), dbc.Label)


def test_get_matched_sequences_column_defs():
    d = cd.get_matched_sequences_column_defs()
    assert len(d) == 18


def test_get_matched_sequences_exp_hot_cold_data_column_defs():
    d = cd.get_matched_sequences_exp_hot_cold_data_column_defs()
    assert len(d) == 10


def test_get_table_experiment_top_variants():
    table = widgets.get_table_experiment_top_variants()
    assert isinstance(table, dag.AgGrid)  # Ensure it's an AgGrid component
    assert table.id == "id-table-exp-top-variants"  # Check ID
    assert "rowSelection" in table.dashGridOptions  # Ensure row selection exists
    assert table.dashGridOptions["rowSelection"] == "single"  # Should be single selection


# Test if `get_table_all_experiments` returns a valid AgGrid component
def test_get_table_all_experiments():
    table = widgets.get_table_all_experiments()
    assert isinstance(table, dag.AgGrid)  # Ensure it's an AgGrid component
    assert table.id == "id-table-all-experiments"  # Check ID
    assert "rowSelection" in table.dashGridOptions  # Ensure row selection exists
    assert table.dashGridOptions["rowSelection"] == "multiple"  # Should be multiple selection


# Test if `get_protein_viewer` returns a valid MolstarViewer component
def test_get_protein_viewer():
    viewer = widgets.get_protein_viewer()
    assert isinstance(viewer, dash_molstar.MolstarViewer)  # Ensure it's a MolstarViewer
    assert viewer.id == "id-viewer"  # Check ID


def test_get_form():
    assert isinstance(layout_upload.get_form(), dbc.Form)


def test_get_navar():
    assert isinstance(layout_bars.get_navbar(), html.Div)


def test_get_sidebar():
    assert isinstance(layout_bars.get_sidebar(), html.Div)


def test_get_landing_page():
    assert isinstance(layout_landing.get_layout(), html.Div)


def test_get_experiment_page():
    assert isinstance(layout_experiment.get_layout(), html.Div)


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("N56T_T45R_D32R", "N56T<br>T45R<br>D32R"),
        ("F67R_A5N", "F67R<br>A5N"),
        ("N56T_T45R_D32R_Y78T", "4Mut*"),  # More than 3 mutations
        ("X_Y_Z_W_V", "5Mut*"),  # More than 3 mutations
        ("single", "single"),  # Only one mutation
        (3, ""),
        (float("nan"), ""),  # dataframe procedures may result in a nan column
    ],
)
def test_format_mutation_annotation(input_text, expected_output):
    assert graphs.format_mutation_annotation(input_text) == expected_output


@pytest.mark.parametrize(
    "smiles, plate, property",
    [
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_count),
    ],
)
def test_creat_heatmap_figure_general(experiment_ep_pcr, smiles, plate, property):
    df = experiment_ep_pcr.data_df
    fig = graphs.creat_heatmap(df, plate_number=plate, property=property, smiles=smiles)

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
    "smiles, plate, mutation,i,j",
    [
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", "A14G", 4, 3),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", "Y185N", 2, 5),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", "L59Q", 4, 10),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", "K87E", 2, 0),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", "G189S", 0, 4),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", "K39E", 1, 4),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", "L173S", -1, -1),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", "V127A", 3, 3),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", "K120R", 4, 5),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", "F89L", 3, 5),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", "V28E", 4, 3),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", "F70L", 2, 5),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", "I67N", 4, 0),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", "K155E", 2, 0),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", "L97S", 0, 4),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", "E164D", 2, 7),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", "D128N", -1, -1),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", "L82P", 3, 3),
        # ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", "L59P", 3, 1),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", "L82Q", 3, 5),
    ],
)
def test_creat_heatmap_figure_data(experiment_ep_pcr, smiles, plate, mutation, i, j):
    df = experiment_ep_pcr.data_df
    fig = graphs.creat_heatmap(df, plate_number=plate, property=gs.c_fitness_value, smiles=smiles)

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


@pytest.mark.parametrize(
    "smiles, plate",
    [
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3"),
    ],
)
def test_create_rank_plot_figure_data(experiment_ep_pcr, smiles, plate):
    fig = graphs.creat_rank_plot(df=experiment_ep_pcr.data_df, plate_number=plate, smiles=smiles)
    count = 0
    for index in range(0, len(fig["data"])):
        count += len(fig["data"][index]["customdata"])
    assert count == 96


def test_get_seq_align_form():
    assert isinstance(layout_matching_sequences.get_seq_align_form(), html.Div)


def test_get_seq_align_layout():
    assert isinstance(layout_matching_sequences.get_layout(), html.Div)


def test_get_table_experiment_top_variants():
    table = widgets.get_table_experiment_top_variants()
    assert table.dashGridOptions["rowSelection"] == "single"
    assert table.defaultColDef["sortable"] is True


def test_get_table_experiment_related_variants():
    table = widgets.get_table_experiment_related_variants()
    assert table.dashGridOptions["pagination"] is True
    assert table.defaultColDef["filter"] is True


def test_get_alert_error():
    alert = widgets.get_alert("Test error message", error=True)
    assert alert.children == "Test error message"
    assert alert.className == "p-3 user-alert-error"


def test_get_alert():
    alert = widgets.get_alert("Test error message", error=False)
    assert alert.children == "Test error message"
    assert alert.className == "p-3 user-alert"


def test_get_label_fixed_for_form():
    label = widgets.get_label_fixed_for_form("Test Label", w=3)
    assert label.children == "Test Label"
    assert label.width == 3


def test_get_tooltip():
    tooltip = widgets.get_tooltip("test-target", "Test Tooltip", "top")
    assert tooltip.target == "test-target"
    assert tooltip.children == "Test Tooltip"
    assert tooltip.placement == "top"


def test_download_type_enum():
    assert widgets.DownloadType.ORIGINAL.value == 1
    assert widgets.DownloadType.FILTERED.value == 2


def test_get_radio_items_download_options():
    radio_id = "test-radio-id"
    components = widgets.get_radio_items_download_options(radio_id)

    # Check the RadioItems component
    radio_items = components[0]
    assert isinstance(radio_items, dbc.RadioItems)
    assert radio_items.id == radio_id
    assert radio_items.value == widgets.DownloadType.ORIGINAL.value
    assert len(radio_items.options) == 2

    # Check the first option
    option_1 = radio_items.options[0]
    assert "label" in option_1
    assert "value" in option_1
    assert option_1["value"] == widgets.DownloadType.ORIGINAL.value

    # Check the tooltips
    tooltip_1 = components[1]
    tooltip_2 = components[2]
    assert tooltip_1.target == f"{radio_id}_1"
    assert tooltip_2.target == f"{radio_id}_2"


def test_get_button_download():
    button_id = "test-button-id"
    components = widgets.get_button_download(button_id)

    # Check the Button component
    button = components[0]
    assert isinstance(button, dbc.Button)
    assert button.id == button_id
    assert button.n_clicks == 0

    # Check the Tooltip component
    tooltip = components[1]
    assert tooltip.target == button_id
    assert tooltip.children == gs.help_download


def test_about_page_layout():
    """Test if the about page layout is correctly generated."""
    assert isinstance(layout_about.get_layout(), html.Div)


def test_explore_layout():
    """Test if the about page layout is correctly generated."""
    assert isinstance(layout_explore.get_layout(), html.Div)
