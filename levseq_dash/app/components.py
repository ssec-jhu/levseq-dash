from enum import Enum

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar
from dash import dcc, html

from levseq_dash.app import column_definitions as cd
from levseq_dash.app import global_strings as gs
from levseq_dash.app import vis


def get_label_fixed_for_form(string):
    # Create a horizontal form by using the Row component. Be sure to specify width on the Label component,
    # and wrap your inputs in Col components.
    return dbc.Label(string, width=2, className="fw-bolder fs-6")


def get_table_experiment():
    """
    Returns dash ag grid component with settings setup for use to show the experiments data
    """
    return dag.AgGrid(
        id="id-table-top-variants",
        # columnDef have a colored column which is dynamic and will be returned in a callback
        # columnDefs=components.get_top_variant_column_defs(),
        columnSize="autoSize",
        defaultColDef={
            # do NOT set "flex": 1 in default col def as it overrides all
            # the column widths
            "sortable": True,
            "resizable": True,
            "filter": True,
            # Set BOTH items below to True for header to wrap text
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            # change the cell padding and font to make it more compact
            # 'cellStyle': {
            #     'fontSize': '12px',
            #     'padding': '5px',
            #     'verticalAlign': 'middle',
            # }
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
        },
        style={"height": "755px", "width": "100%"},
        dashGridOptions={
            # row selection for the protein viewer
            "rowSelection": "single",
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,
            "headerHeight": 50,
        },
        rowClassRules={
            # "bg-secondary": "params.data.well == 'A2'",
            # "text-info fw-bold fs-5": "params.data.well == 'A1'",
            "fw-bold": "params.data.amino_acid_substitutions == '#PARENT#'",
            # "text-warning fw-bold fs-5": "['#PARENT#'].includes(
            # params.data.amino_acid_substitutions)",
        },
    )


def get_table_all_experiments():
    """
    Returns dash ag grid component with settings setup for use to show all experiments
    """
    return dag.AgGrid(
        id="id-table-all-experiments",
        columnDefs=cd.get_all_experiments_column_defs(),
        defaultColDef={
            # do NOT set "flex": 1 in default col def as it overrides all
            # the column widths
            "sortable": True,
            "resizable": True,
            "filter": True,
            # Set BOTH items below to True for header to wrap text
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            # "flex": 1,  # TODO: remove this after you put fixed width
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
        },
        # style={"height": "600px", "width": "100%"},
        dashGridOptions={
            # Enable multiple selection
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
            "animateRows": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
        },
    )


def get_table_matched_sequences():
    """
    Returns dash ag grid component with settings setup for use to show all experiments
    """
    return dag.AgGrid(
        id="id-table-matched-sequences",
        columnDefs=cd.get_matched_sequences_column_defs(),
        defaultColDef={
            # do NOT set "flex": 1 in default col def as it overrides all
            # the column widths
            "sortable": True,
            "resizable": True,
            "filter": True,
            # Set BOTH items below to True for header to wrap text
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            # "flex": 1,  # TODO: remove this after you put fixed width
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "cellStyle": {
                "whiteSpace": "normal",
                "wordBreak": "break-word",
                # "fontSize": "12px",
                # 'padding': '5px',
                # 'verticalAlign': 'middle',
            },
            "autoHeight": True,  # Adjusts row height to fit wrapped text
            "tooltipComponent": "agTooltipComponent",
        },
        style={"height": vis.seq_match_table_height, "width": "100%"},
        dashGridOptions={
            # Enable multiple selection
            "alwaysShowHorizontalScroll": True,  # TODO: does this work on mac?
            "rowSelection": "single",
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,  # TODO: is this overwritten by the alignnmnet width
            "pagination": True,
            # # this will set the number of items per page be a function of the height
            # # if we load too many rows that are not visible, the graphics is not smart enough
            # # to hide what is not visible, so it takes longer for the page to load
            # "paginationAutoPageSize": True,
        },
        # className="ag-theme-alpine",
    )


def get_table_matched_sequences_exp_hot_cold_data():
    """
    Returns dash ag grid component with settings setup for use to show all experiments
    """
    return dag.AgGrid(
        id="id-table-matched-sequences-exp-hot-cold-data",
        columnDefs=cd.get_matched_sequences_exp_hot_cold_data_column_defs(),
        defaultColDef={
            # do NOT set "flex": 1 in default col def as it overrides all
            # the column widths
            "sortable": True,
            "resizable": True,
            "filter": True,
            # Set BOTH items below to True for header to wrap text
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            # "flex": 1,  # TODO: remove this after you put fixed width
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
        },
        style={"height": "800px", "width": "100%"},
        dashGridOptions={
            # Enable multiple selection
            # "rowSelection": "multiple",
            # "suppressRowClickSelection": True,
            "animateRows": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,
            "pagination": True,
            # # this will set the number of items per page be a function of the height
            # # if we load too many rows that are not visible, the graphics is not smart enough
            # # to hide what is not visible, so it takes longer for the page to load
            # "paginationAutoPageSize": True,
        },
    )


def get_protein_viewer():
    """
    Returns the dash molstar viewer component
    """
    return dash_molstar.MolstarViewer(
        id="id-viewer",
        # data=data,
        style={"width": "auto", "height": "600px"},
        layout={
            # "layoutShowControls": True,
            # https://dash-molstar.readthedocs.io/en/latest/load.html#general-options
            # ‘outside’, ‘portrait’, ‘landscape’ and ‘reactive’ (default)
            "layoutControlsDisplay": "landscape",
            "layoutIsExpanded": False,  # if true it makes it full screen
        },
    )


def get_info_icon_tooltip_bundle(info_icon_id, help_string, location, allow_html=False):
    return html.Div(
        [
            # html.Span(vis.icon_info, id=info_icon_id, weight=500, size="md"),
            dbc.Label(id=info_icon_id, children=vis.icon_info),
            get_tooltip(info_icon_id, help_string, location, allow_html),
        ]
    )


def get_tooltip(target_id, string, tip_placement, allow_html=False):
    if allow_html:
        string = (html.Div(dcc.Markdown(string, dangerously_allow_html=True)),)
    return dbc.Tooltip(
        children=string,
        is_open=False,
        target=target_id,
        placement=tip_placement,
        # some style is overriding the tooltip and making the strings all caps
        # overriding the text transform here
        style={"text-transform": "none"},
    )


class DownloadType(Enum):
    ORIGINAL = 1
    FILTERED = 2


def get_radio_items_download_options(radio_id):
    # Note: tooltips will only bind with the first radio_id that comes in, the GEQ one that comes after will not bind
    # the tooltips because the tooltip id is the same as the radio item id not the radio button group as a whole
    id_1 = f"{radio_id}_1"
    id_2 = f"{radio_id}_2"
    return [
        dbc.RadioItems(
            options=[
                {
                    "label": html.Span(id=id_1, children=[vis.icon_download, gs.download_original]),
                    "value": DownloadType.ORIGINAL.value,
                },
                {
                    "label": html.Span(id=id_2, children=[vis.icon_download, gs.download_filtered]),
                    "value": DownloadType.FILTERED.value,
                },
            ],
            value=DownloadType.ORIGINAL.value,
            id=radio_id,
            inline=True,
        ),
        get_tooltip(id_1, gs.help_download_mode_unfiltered, "top"),
        get_tooltip(id_2, gs.help_download_mode_filtered, "top"),
    ]


def get_button_download(button_id):
    return [
        dbc.Button(
            children=html.Span([vis.icon_download, gs.download_results]),
            id=button_id,
            n_clicks=0,
            size="md",
            class_name="d-grid gap-2 col-12 btn-primary",
        ),
        get_tooltip(button_id, gs.help_download, "top"),
    ]
