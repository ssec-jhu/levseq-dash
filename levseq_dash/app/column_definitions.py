from levseq_dash.app import global_strings as gs
from levseq_dash.app import vis


def get_top_variant_column_defs(df):
    """
    Returns column definitions and setup for dash ag grid table per experiment
    """
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
    """
    Returns column definitions and setup for dash ag grid table for all experiments
    """
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
