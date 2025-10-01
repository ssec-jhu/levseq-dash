from enum import Enum

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import column_definitions as cd
from levseq_dash.app.components import vis


# ----------------------------------------
# Tables: Experiment dashboard related
# ----------------------------------------
def get_table_experiment_top_variants():
    """
    Returns dash ag grid component with settings setup for use to show the experiments data
    """
    return dag.AgGrid(
        id="id-table-exp-top-variants",
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
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            # change the cell padding and font to make it more compact
            # 'cellStyle': {
            #     'fontSize': '12px',
            #     'padding': '5px',
            #     'verticalAlign': 'middle',
            # }
            # we  NEED to add this line or the cells won't adjust per columns
            # row height to fit wrapped text
            "autoHeight": True,
        },
        style={"height": "755px", "width": "100%"},
        dashGridOptions={
            # row selection for the protein viewer
            "rowSelection": "single",
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,  # creating a more compact look for the table
            "headerHeight": 50,
            "pagination": True,
            # https://dash.plotly.com/dash-ag-grid/tooltips
            # If tooltipInteraction is set to True in the Grid Options, the tooltips will not
            # disappear while being hovered, and you will be able to click and select the text within the tooltip.
            "tooltipInteraction": True,
            # By default, when you hover on an item, it will take 2 seconds for the tooltip to be displayed
            # and then 10 seconds for the tooltip to hide. If you need to change these delays,
            # the tooltipShowDelay and tooltipHideDelay configs should be used, which are set in milliseconds.
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
        rowClassRules={
            # "bg-secondary": "params.data.well == 'A2'",
            # "text-info fw-bold fs-5": "params.data.well == 'A1'",
            "fw-bold": "params.data.amino_acid_substitutions == '#PARENT#'",
            # "text-warning fw-bold fs-5": "['#PARENT#'].includes(
            # params.data.amino_acid_substitutions)",
        },
    )


def get_table_experiment_related_variants():
    """
    Returns dash ag grid component with settings setup for use to show all experiments
    """
    return dag.AgGrid(
        id="id-table-exp-related-variants",
        columnDefs=cd.get_an_experiments_matched_sequences_column_defs(),
        defaultColDef={
            # do NOT set "flex": 1 in default col def as it overrides all
            # the column widths
            "sortable": True,
            "resizable": True,
            "filter": True,
            # Set BOTH items below to True for header to wrap text
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            # "cellStyle": {
            #     "whiteSpace": "normal",
            #     "wordBreak": "break-word",
            #     # "fontSize": "12px",
            #     # 'padding': '5px',
            #     # 'verticalAlign': 'middle',
            # },
            # we  NEED to add this line or the cells won't adjust per columns
            # row height to fit wrapped text
            "autoHeight": True,
        },
        style={"height": vis.related_variants_table_height, "width": "100%"},
        dashGridOptions={
            # Enable multiple selection
            "alwaysShowHorizontalScroll": True,  # TODO: does this work on mac?
            "rowSelection": "single",
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,  # TODO: is this overwritten by the alignment width
            # "pagination": True,
            # # this will set the number of items per page be a function of the height
            # # if we load too many rows that are not visible, the graphics is not smart enough
            # # to hide what is not visible, so it takes longer for the page to load
            # "paginationAutoPageSize": True,
            "pagination": True,
            # https://dash.plotly.com/dash-ag-grid/tooltips
            # If tooltipInteraction is set to True in the Grid Options, the tooltips will not
            # disappear while being hovered, and you will be able to click and select the text within the tooltip.
            "tooltipInteraction": True,
            # By default, when you hover on an item, it will take 2 seconds for the tooltip to be displayed
            # and then 10 seconds for the tooltip to hide. If you need to change these delays,
            # the tooltipShowDelay and tooltipHideDelay configs should be used, which are set in milliseconds.
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    )


# ----------------------------------------
# Tables: Lab page related components
# ----------------------------------------
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
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            # we  NEED to add this line or the cells won't adjust per columns
            "autoHeight": True,
        },
        style={"height": "600px", "width": "100%"},
        dashGridOptions={
            # Enable multiple selection
            "rowSelection": "multiple",
            # "suppressRowClickSelection": True,
            # "animateRows": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "pagination": True,
            # Compact spacing similar to ag-theme-balham
            "rowHeight": 30,  # Smaller rows like balham
            "headerHeight": 30,  # Smaller headers like balham
            # https://dash.plotly.com/dash-ag-grid/tooltips
            # If tooltipInteraction is set to True in the Grid Options, the tooltips will not
            # disappear while being hovered, and you will be able to click and select the text within the tooltip.
            "tooltipInteraction": True,
            # By default, when you hover on an item, it will take 2 seconds for the tooltip to be displayed
            # and then 10 seconds for the tooltip to hide. If you need to change these delays,
            # the tooltipShowDelay and tooltipHideDelay configs should be used, which are set in milliseconds.
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    )


# --------------------------------
# Tables: Sequence Alignment related
# --------------------------------
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
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            # "cellStyle": {
            #     "whiteSpace": "normal",
            #     "wordBreak": "break-word",
            #     # "fontSize": "12px",
            #     # 'padding': '5px',
            #     # 'verticalAlign': 'middle',
            # },
            # "autoHeight": True,  # Adjusts row height to fit wrapped text
        },
        style={"height": vis.seq_match_table_height, "width": "100%"},
        dashGridOptions={
            # Enable multiple selection
            "alwaysShowHorizontalScroll": True,  # TODO: does this work on mac?
            "rowSelection": "single",
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,
            "pagination": True,
            # # this will set the number of items per page be a function of the height
            # # if we load too many rows that are not visible, the graphics is not smart enough
            # # to hide what is not visible, so it takes longer for the page to load
            # "paginationAutoPageSize": True,
            # https://dash.plotly.com/dash-ag-grid/tooltips
            # If tooltipInteraction is set to True in the Grid Options, the tooltips will not
            # disappear while being hovered, and you will be able to click and select the text within the tooltip.
            "tooltipInteraction": True,
            # By default, when you hover on an item, it will take 2 seconds for the tooltip to be displayed
            # and then 10 seconds for the tooltip to hide. If you need to change these delays,
            # the tooltipShowDelay and tooltipHideDelay configs should be used, which are set in milliseconds.
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
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
            # "animateRows": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,
            "pagination": True,
            # # this will set the number of items per page be a function of the height
            # # if we load too many rows that are not visible, the graphics is not smart enough
            # # to hide what is not visible, so it takes longer for the page to load
            # "paginationAutoPageSize": True,
            # https://dash.plotly.com/dash-ag-grid/tooltips
            # If tooltipInteraction is set to True in the Grid Options, the tooltips will not
            # disappear while being hovered, and you will be able to click and select the text within the tooltip.
            "tooltipInteraction": True,
            # By default, when you hover on an item, it will take 2 seconds for the tooltip to be displayed
            # and then 10 seconds for the tooltip to hide. If you need to change these delays,
            # the tooltipShowDelay and tooltipHideDelay configs should be used, which are set in milliseconds.
            "tooltipShowDelay": 1000,
            "tooltipHideDelay": 2000,
        },
    )


# --------------------------------
# Protein Viewer
# --------------------------------
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


# --------------------------------
# Misc
# --------------------------------
def get_label_fixed_for_form(string, w=2):
    # Create a horizontal form by using the Row component. Be sure to specify width on the Label component,
    # and wrap your inputs in Col components.
    return dbc.Label(string, width=w, className="fw-bolder fs-6")


def get_info_icon_tooltip_bundle(info_icon_id, help_string, location, allow_html=False):
    return html.Span(
        [
            # do not use html.span or dbc.label it will mess with the layout
            html.Div(id=info_icon_id, children=vis.get_icon(vis.icon_info, vis.SMALL), className="main-color"),
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


def get_input_plus_info_ico_bundle(input_id, input_value, info_icon_help_string):
    return html.Span(
        [
            dbc.Input(
                id=input_id,
                value=input_value,
                type="text",
                debounce=True,
            ),
            html.Span(
                get_info_icon_tooltip_bundle(
                    info_icon_id=f"{input_id}-info",
                    help_string=info_icon_help_string,
                    location="top",
                ),
                style={"marginLeft": "5px"},
            ),
        ],
        className="d-flex align-items-center",
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
                    "label": html.Span(id=id_1, children=[vis.get_icon(vis.icon_download), gs.download_original]),
                    "value": DownloadType.ORIGINAL.value,
                },
                {
                    "label": html.Span(id=id_2, children=[vis.get_icon(vis.icon_download), gs.download_filtered]),
                    "value": DownloadType.FILTERED.value,
                },
            ],
            className="d-flex align-items-center",
            value=DownloadType.ORIGINAL.value,
            id=radio_id,
            inline=True,
        ),
        get_tooltip(id_1, gs.help_download_mode_unfiltered, "top"),
        get_tooltip(id_2, gs.help_download_mode_filtered, "top"),
    ]


def get_download_text_icon_combo(text_string):
    return html.Span(
        [
            html.Span(vis.get_icon(vis.icon_download)),
            html.Span(
                [text_string],
                style={"marginLeft": "12px"},
            ),
        ]
    )


def get_download_radio_combo(button_id, radio_id):
    # Note: tooltips will only bind with the first radio_id that comes in, the GEQ one that comes after will not bind
    # the tooltips because the tooltip id is the same as the radio item id not the radio button group as a whole
    id_1 = f"{radio_id}_1"
    id_2 = f"{radio_id}_2"
    return html.Span(
        [
            # keep this span here
            # removing it makes the buttons big
            html.Span(
                dbc.Button(
                    children=[get_download_text_icon_combo(gs.download_results)],
                    id=button_id,
                    n_clicks=0,
                    size="sm",
                    # col-12 will take up the full space of the container
                    class_name="d-grid gap-2 col-12 btn-primary align-items-center",
                ),
            ),
            dbc.RadioItems(
                options=[
                    {
                        "label": html.Span(id=id_1, children=[vis.get_icon(vis.icon_download), gs.download_original]),
                        "value": DownloadType.ORIGINAL.value,
                    },
                    {
                        "label": html.Span(id=id_2, children=[vis.get_icon(vis.icon_download), gs.download_filtered]),
                        "value": DownloadType.FILTERED.value,
                    },
                ],
                className="d-flex align-items-center",
                style={"marginLeft": "5px"},
                value=DownloadType.ORIGINAL.value,
                id=radio_id,
                inline=True,
            ),
            # the tooltips for the components
            get_tooltip(button_id, gs.help_download, "top"),
            get_tooltip(id_1, gs.help_download_mode_unfiltered, "top"),
            get_tooltip(id_2, gs.help_download_mode_filtered, "top"),
        ],
        # keep the spans horizontally in one row
        style={"display": "flex"},
    )


def generate_label_with_info(label, id_info):
    """
    Produces a bold label with a string. This is used in multiple places throughout the layout.
    """
    return html.Div(
        [
            html.Span(f"{label}:", style=vis.experiment_info),
            html.Span(id=id_info),
        ],
        style={
            "wordBreak": "break-all",  # this is the key
            "whiteSpace": "normal",  # text wrap onto the next line.
        },
    )


def get_alert(alert_message, error=True, is_markdown=False):
    if error:
        class_name = "p-3 user-alert-error"
    else:
        class_name = "p-3 user-alert"

    # If markdown is enabled, use dcc.Markdown to render the content
    if is_markdown:
        children = dcc.Markdown(alert_message, dangerously_allow_html=True)
        class_name = "p-3 user-alert"
    else:
        children = alert_message

    return dbc.Alert(
        children=children,
        is_open=True,
        dismissable=True,
        className=class_name,
    )
