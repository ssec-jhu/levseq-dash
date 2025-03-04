import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar

from levseq_dash.app import global_strings as gs
from levseq_dash.app import vis


def get_label(string):
    return dbc.Label(string, width=3, className="fs-6")


def get_top_variant_column_defs(df):
    # mean_values = df[df["amino_acid_substitutions"] == "#PARENT#"].groupby("cas_number")["fitness_value"].mean()
    return [
        {
            "field": gs.c_cas,
            "headerName": "CAS #",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            # flex allows the resizing to be dynamic
            "flex": 2,
        },
        {
            "field": gs.c_plate,
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 2,
        },
        {
            "field": gs.c_well,
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "width": 80,
        },
        {
            "field": gs.c_substitutions,
            "headerName": "Sub",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 2,
        },
        {
            "field": gs.c_fitness_value,
            "headerName": "Fitness",
            "initialSort": "desc",
            "filter": "agNumberColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 2,
            # "cellStyle": {"styleConditions": vis.data_bars_colorscale(df, gs.c_fitness_value)},
        },
        {
            "field": "ratio",
            "filter": "agNumberColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 2,
            "cellStyle": {"styleConditions": vis.data_bars_group_mean_colorscale(df)},
        },
    ]


def get_all_experiments_column_defs():
    return [
        {  # Checkbox column
            "headerCheckboxSelection": True,
            "checkboxSelection": True,
            "headerName": "",
            "width": 30,
            # "flex": 1,
        },
        {
            "field": "experiment_id",
            "headerName": "ID",
            "filter": "agNumberColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 2,
        },
        {
            "field": "experiment_name",
            "headerName": "Name",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 3,
        },
        {
            "field": "experiment_date",
            "headerName": "Date",
            "filter": "agDateColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 4,
        },
        {
            "field": "upload_time_stamp",
            "headerName": "Uploaded",
            "filter": "agDateColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 4,
        },
        {
            "field": "substrate_cas_number",
            "headerName": "Sub CAS",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 3,
        },
        {
            "field": "product_cas_number",
            "headerName": "Prod CAS",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 4,
        },
        {
            "field": "assay",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 4,
        },
        {
            "field": "mutagenesis_method",
            "headerName": "Mutagenesis Method",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 4,
        },
        {
            "field": "plates_count",
            "headerName": "#Plates",
            "filter": "agNumberColumnFilter",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "flex": 2,
        },
    ]


def get_table_experiment():
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
        style={"height": "650px", "width": "100%"},
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
    return dag.AgGrid(
        id="id-table-all-experiments",
        columnDefs=get_all_experiments_column_defs(),
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


def get_protein_viewer():
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
