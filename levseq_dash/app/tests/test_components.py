import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar
from dash import html

from levseq_dash.app.components import column_definitions as cd
from levseq_dash.app.components import widgets
from levseq_dash.app.components.layout import (
    layout_about,
    layout_bars,
    layout_experiment,
    layout_explore,
    layout_landing,
    layout_matching_sequences,
    layout_upload,
)
from levseq_dash.app.utils import utils


def test_get_label():
    assert isinstance(widgets.get_label_fixed_for_form("random_string"), dbc.Label)


def test_get_top_variant_column_defs(experiment_ep_pcr):
    df_filtered_with_ratio = utils.calculate_group_mean_ratios_per_smiles_and_plate(experiment_ep_pcr.data_df)
    d = cd.get_top_variant_column_defs(df_filtered_with_ratio)
    assert len(d) == 6


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


def test_get_explore_page():
    assert isinstance(layout_landing.get_layout(), html.Div)


def test_get_experiment_page():
    assert isinstance(layout_experiment.get_layout(), html.Div)


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


def test_about_page_layout():
    """Test if the about page layout is correctly generated."""
    assert isinstance(layout_about.get_layout(), html.Div)


def test_explore_layout():
    """Test if the about page layout is correctly generated."""
    assert isinstance(layout_explore.get_layout(), html.Div)
