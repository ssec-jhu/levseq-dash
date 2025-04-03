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
            # flex allows the resizing to be dynamic
            "flex": 2,
        },
        {
            "field": gs.c_plate,
            # mouse hover over the truncated cell will show the contents of the cell
            "tooltipField": gs.c_plate,
            "flex": 2,
        },
        {
            "field": gs.c_well,
            "width": 80,
        },
        {
            "field": gs.c_substitutions,
            # mouse hover over the truncated cell will show the contents of the cell
            "tooltipField": gs.c_substitutions,
            "headerName": "Sub",
            "flex": 2,
        },
        {
            "field": gs.c_fitness_value,
            "headerName": "Fitness",
            "initialSort": "desc",
            "filter": "agNumberColumnFilter",
            "flex": 2,
            # "cellStyle": {"styleConditions": vis.data_bars_colorscale(df, gs.c_fitness_value)},
        },
        {
            "field": "ratio",
            "filter": "agNumberColumnFilter",
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
            "field": gs.cc_experiment_id,
            "pinned": "left",  # pinned the column to the left for all results
            "headerName": "ID",
            # "flex": 2,
            "width": 70,
        },
        {
            "field": "cas_number",
            "headerName": "CAS",
            "pinned": "left",
            # "flex": 3,
            "width": 120,
        },
        {
            "field": "experiment_name",
            "headerName": "Exp Name",
            # "flex": 3,
            "width": 130,
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
            "width": 130,
            # "tooltipField": gs.snpt_col_sample_description,
        },
        {
            "field": "product_cas_number",
            "headerName": "Prod CAS",
            "width": 130,
        },
        {
            "field": "assay",
            "width": 130,
        },
        {
            "field": "mutagenesis_method",
            "headerName": "Method",
            "headerTooltip": "Mutagenesis Method",
            # this will shorten the length of the string to SSM or epPCR
            # comment this line if you want the original value displayed
            "valueFormatter": {"function": "shortenMutagenesisMethod(params.value)"},
            "width": 120,
        },
        {
            "field": "plates_count",
            "headerName": "#plates",
            "filter": "agNumberColumnFilter",
            "width": 100,
        },
        {
            "field": "identities",
            "headerName": "# matches",
            "filter": "agNumberColumnFilter",
            "width": 110,
        },
        {
            "field": "gaps",
            "headerName": "#gaps",
            "filter": "agNumberColumnFilter",
            "width": 90,
        },
        {
            "field": "mismatches",
            "headerName": "#matches",
            "filter": "agNumberColumnFilter",
            "width": 125,
        },
        {
            "field": gs.cc_hot_indices_per_cas,
            "headerName": "Hot Residue/CAS",
            "width": 200,
        },
        {
            "field": gs.cc_cold_indices_per_cas,
            "headerName": "Cold Residue/CAS",
            "width": 200,
        },
        # {
        #     "field": gs.c_substitutions,
        #     "headerName": "AA Sub/CAS",
        #     "autoHeight": True,  # Makes the row height adjust to content
        #     # "cellStyle": {
        #     #     "whiteSpace": "pre-wrap",
        #     #     # "lineHeight": "1.2"
        #     # },
        #     "width": 200,
        # },
        {
            "field": gs.cc_seq_alignment_mismatches,
            "headerName": "Alignment Mismatches",
            "width": 200,
        },
        {
            "field": gs.cc_seq_alignment,
            "autoHeight": True,  # Makes the row height adjust to content
            "cellRenderer": "seqAlignmentVis",
            "cellStyle": {
                "whiteSpace": "pre-wrap",
                "fontFamily": "monospace",
                "fontSize": 12,
                "lineHeight": "1.2",
                "padding": "10px",
            },
            "width": 1500,
        },
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
            "field": "experiment_id",
            "headerName": "Experiment ID",
            "width": 150,
        },
        {
            "field": gs.cc_hot_cold_type,
            "width": 150,
        },
        {
            "field": gs.c_cas,
            "headerName": "CAS #",
            # flex allows the resizing to be dynamic
            "flex": 2,
        },
        {
            "field": gs.c_plate,
            "flex": 2,
        },
        {
            "field": gs.c_well,
            "width": 80,
        },
        {
            "field": gs.c_substitutions,
            "headerName": "AA Substitutions",
            "flex": 2,
        },
        {
            "field": gs.c_fitness_value,
            "headerName": "Fitness",
            # "initialSort": "desc",
            "filter": "agNumberColumnFilter",
            "flex": 2,
            # "cellStyle": {"styleConditions": vis.data_bars_colorscale(df, gs.c_fitness_value)},
        },
        {
            "field": "ratio",
            "initialSort": "desc",
            "filter": "agNumberColumnFilter",
            "flex": 2,
            # "cellStyle": {"styleConditions": vis.data_bars_colorscale(df, gs.c_fitness_value)},
        },
    ]
