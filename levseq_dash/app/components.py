import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar
from dash import html

from levseq_dash.app import column_definitions as cd
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
        },
        style={"height": "1600px", "width": "100%"},
        dashGridOptions={
            # Enable multiple selection
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
            "animateRows": True,
            # https://ag-grid.com/javascript-data-grid/selection-overview/#cell-text-selection
            "enableCellTextSelection": True,
            "rowHeight": 30,
            # "pagination": True,
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


def get_info_icon_tooltip_bundle(info_icon_id, help_string, tip_placement):
    """
    Convenient function to bundle an info icon with a tooltip
    """
    return html.Div(
        [
            dbc.Label(id=info_icon_id, children=vis.icon_info),
            dbc.Tooltip(
                children=help_string,
                is_open=False,
                target=info_icon_id,
                placement=tip_placement,
                # some style is overriding the tooltip and making the strings all caps
                # overriding the text transform here
                style={"text-transform": "none"},
            ),
        ]
    )
