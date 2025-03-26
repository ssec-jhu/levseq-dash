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
            "tooltipField": gs.c_plate,
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
            "tooltipField": gs.c_substitutions,
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
            "flex": 2,
        },
        {
            "field": "experiment_name",
            "headerName": "Name",
            "flex": 3,
        },
        {
            "field": "experiment_date",
            "headerName": "Date",
            "filter": "agDateColumnFilter",
            "flex": 4,
        },
        {
            "field": "upload_time_stamp",
            "headerName": "Uploaded",
            "filter": "agDateColumnFilter",
            "flex": 4,
        },
        {
            "field": "substrate_cas_number",
            "headerName": "Sub CAS",
            "flex": 3,
        },
        {
            "field": "product_cas_number",
            "headerName": "Prod CAS",
            "flex": 4,
        },
        {
            "field": "assay",
            "flex": 4,
        },
        {
            "field": "mutagenesis_method",
            "headerName": "Mutagenesis Method",
            "flex": 4,
        },
        {
            "field": "plates_count",
            "headerName": "#Plates",
            "filter": "agNumberColumnFilter",
            "flex": 2,
        },
    ]


def get_matched_sequences_column_defs():
    """
    Returns column definitions for the matched sequences
    """
    return [
        # {  # Checkbox column
        #     "headerCheckboxSelection": True,
        #     "checkboxSelection": True,
        #     "headerName": "",
        #     "width": 30,
        # },
        {
            "field": "id",
            "pinned": "left",  # pinned the column to the left for all results
            "headerName": "ID",
            # "flex": 2,
            "width": 70,
        },
        {
            "field": "experiment_name",
            "headerName": "Name",
            # "flex": 3,
            "width": 150,
        },
        {
            "field": "alignment_score",
            "filter": "agNumberColumnFilter",
            "headerName": "Raw Score",
            # "flex": 3,
            "width": 100,
        },
        {
            "field": "norm_score",
            "initialSort": "desc",  # sort based on this column
            "headerName": "Norm Score",
            "filter": "agNumberColumnFilter",
            "width": 120,
        },
        {
            "field": "experiment_date",
            "headerName": "Date",
            "filter": "agDateColumnFilter",
            "width": 120,
        },
        {
            "field": "upload_time_stamp",
            "headerName": "Uploaded",
            "filter": "agDateColumnFilter",
            "width": 150,
        },
        {
            "field": "substrate_cas_number",
            "headerName": "Sub CAS",
            "autoHeight": True,  # Adjusts row height to fit wrapped text
            # TODO: should I remove the cell style and add tooltip? do we need to see the whole
            #  list or do we just want it to be there
            "cellStyle": {
                "whiteSpace": "normal",
                "wordBreak": "break-word",
                # "lineHeight": "1.2"
            },
            "width": 130,
            # "tooltipField": gs.snpt_col_sample_description,
        },
        {
            "field": "product_cas_number",
            "headerName": "Prod CAS",
            # TODO: should I remove the cell style and add tooltip? do we need to see the whole
            #  list or do we just want it to be there
            "autoHeight": True,
            "cellStyle": {
                "whiteSpace": "normal",
                "wordBreak": "break-word",
                # "lineHeight": "1.2"
            },
            "width": 130,
        },
        {
            "field": "assay",
            # TODO: should I remove the cell style and add tooltip? do we need to see the whole
            #  list or do we just want it to be there
            "autoHeight": True,  # Adjusts row height to fit wrapped text
            "cellStyle": {
                "whiteSpace": "normal",
                "wordBreak": "break-word",
                # "lineHeight": "1.2"
            },
            "width": 130,
        },
        {
            "field": "mutagenesis_method",
            "headerName": "Method",
            "autoHeight": True,  # Adjusts row height to fit wrapped text
            "cellStyle": {
                "whiteSpace": "normal",
                "wordBreak": "break-word",
            },
            "headerTooltip": "Mutagenesis Method",
            # this will shorten the length of the string to SSM or epPCR
            # comment this line if you want the original value displayed
            "valueFormatter": {"function": "shortenMutagenesisMethod(params.value)"},
            "width": 120,
        },
        {
            "field": "plates_count",
            "headerName": "#Plates",
            "filter": "agNumberColumnFilter",
            "width": 100,
        },
        {
            "field": "identities",
            "filter": "agNumberColumnFilter",
            "headerName": "# matches",
            "width": 110,
        },
        {
            "field": "gaps",
            "filter": "agNumberColumnFilter",
            "width": 90,
        },
        {
            "field": "mismatches",
            "filter": "agNumberColumnFilter",
            "width": 125,
        },
        {
            "field": "hot_n_str",
            "headerName": "Hot Indices",
            "autoHeight": True,  # Makes the row height adjust to content
            "cellStyle": {
                "whiteSpace": "pre-wrap",
                # "fontFamily": "monospace",
                # "lineHeight": "1.2"
            },
            "width": 200,
        },
        {
            "field": "cold_n_str",
            "headerName": "Cold Indices",
            "autoHeight": True,  # Makes the row height adjust to content
            "cellStyle": {
                "whiteSpace": "pre-wrap",
                # "fontFamily": "monospace",
                # "lineHeight": "1.2"
            },
            "width": 200,
        },
        {
            "field": "mutations",
            "autoHeight": True,  # Makes the row height adjust to content
            "cellStyle": {
                "whiteSpace": "pre-wrap",
                # "fontFamily": "monospace",
                # "lineHeight": "1.2"
            },
            "width": 200,
        },
        {
            "field": "alignnment",
            "autoHeight": True,  # Makes the row height adjust to content
            "cellRenderer": "tempDebug",
            "cellStyle": {
                "whiteSpace": "pre-wrap",
                "fontFamily": "monospace",
                "fontSize": 12,
                "lineHeight": "1.2",
                "padding": "10px",
            },
            "width": 1500,
        },
        # {
        #     "field": "coordinates",
        #     "filterParams": {
        #         "buttons": ["reset", "apply"],
        #         "closeOnApply": True,
        #     },
        #     "width": 150,
        #     "cellRenderer": "addLineBreaksOnArrayRow",
        #     "autoHeight": True,
        # },
        # {
        #     "field": "alignment",
        #     "filterParams": {
        #         "buttons": ["reset", "apply"],
        #         "closeOnApply": True,
        #     },
        #     # "width": 1100, # for two line mode
        #     "width": 700,
        #     "cellRenderer": "addLineBreaksOnNewLines",
        #     "autoHeight": True,
        # },
        # {
        #     "field": "indices",
        #     "filterParams": {"buttons": ["reset", "apply"], "closeOnApply": True, },
        #     "width": 2000,
        #     'cellRenderer': "addLineBreaksOnArrayRow",
        #     "autoHeight": True,
        # },
    ]


def get_matched_sequences_exp_hot_cold_data_column_defs():
    """
    Returns column definitions for the matched sequences experiment data
    """
    return [
        # {  # Checkbox column
        #     "headerCheckboxSelection": True,
        #     "checkboxSelection": True,
        #     "headerName": "",
        #     "width": 30,
        # },
        {
            "field": "id",
            "headerName": "ID",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "width": 100,
        },
        {
            "field": "variant_type",
            "filterParams": {
                "buttons": ["reset", "apply"],
                "closeOnApply": True,
            },
            "width": 150,
        },
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
    ]
