from levseq_dash.app import global_strings as gs
from levseq_dash.app import vis


def get_checkbox():
    return [
        {  # Checkbox column
            "headerCheckboxSelection": True,
            "checkboxSelection": True,
            "headerName": "",
            "width": 30,
        }
    ]


def get_experiment_id(record):
    c = [
        {
            "field": gs.cc_experiment_id,
            "headerName": gs.header_experiment_id,
            "filter": "agNumberColumnFilter",
        }
    ]
    if record:
        c[0].update(record)

    return c


def get_experiment_name(record):
    c = [
        {
            "field": "experiment_name",
            "headerName": gs.header_experiment_name,
        }
    ]
    if record:
        c[0].update(record)

    return c


def get_experiment_meta(record_1, record_2, record_3, record_4, record_5):
    c = [
        {
            "field": "experiment_date",
            "headerName": "Date",
            "filter": "agDateColumnFilter",
        },
        {
            "field": "upload_time_stamp",
            "headerName": "Uploaded",
            "filter": "agDateColumnFilter",
        },
        {
            "field": "assay",
        },
        {
            "field": gs.cc_mutagenesis,
            "headerName": gs.header_mutagenesis,
        },
        {
            "field": "plates_count",
            "headerName": "# plates",
            "filter": "agNumberColumnFilter",
        },
    ]

    if record_1:
        c[0].update(record_1)
    if record_2:
        c[1].update(record_2)
    if record_3:
        c[2].update(record_3)
    if record_4:
        c[3].update(record_4)
    if record_5:
        c[4].update(record_5)

    return c


def get_experiment_meta_cas(record_1, record_2):
    c = [
        {
            "field": gs.cc_substrate_cas,
            "headerName": gs.header_sub_cas,
        },
        {
            "field": gs.cc_prod_cas,
            "headerName": gs.header_prod_cas,
        },
    ]

    if record_1:
        c[0].update(record_1)
    if record_2:
        c[1].update(record_2)

    return c


def get_cas(record):
    c = [
        {
            "field": gs.c_cas,
            "headerName": gs.header_cas_number,
            # flex allows the resizing to be dynamic
            # "flex": 2,
        }
    ]
    if record:
        c[0].update(record)
    return c


def get_plate_well(record_1):
    c = [
        {
            "field": gs.c_plate,
            # mouse hover over the truncated cell will show the contents of the cell
            "tooltipField": gs.c_plate,
            # "flex": 2,
        },
        {
            "field": gs.c_well,
            "width": 80,
        },
    ]
    if record_1:
        c[0].update(record_1)

    return c


def get_fitness_ratio(record_1, record_2):
    c = [
        {
            "field": gs.c_fitness_value,
            "headerName": gs.header_fitness,
            "initialSort": "desc",
            "filter": "agNumberColumnFilter",
            # "flex": 2,
            # "cellStyle": {"styleConditions": vis.data_bars_colorscale(df, gs.c_fitness_value)},
        },
        {
            "field": gs.cc_ratio,
            "filter": "agNumberColumnFilter",
            # "flex": 2,
            # "cellStyle": {"styleConditions": vis.data_bars_group_mean_colorscale(df)},
        },
    ]

    if record_1:
        c[0].update(record_1)

    if record_2:
        c[1].update(record_2)

    return c


def get_substitutions(record):
    c = [
        {
            "field": gs.c_substitutions,
            # mouse hover over the truncated cell will show the contents of the cell
            "tooltipField": gs.c_substitutions,
            "headerName": gs.header_substitutions,
            # "flex": 2,
        },
    ]
    if record:
        c[0].update(record)
    return c


def get_alignment_scores():
    c = [
        # TODO: do we need to show the raw score
        # {
        #     "field": "alignment_score",
        #     "filter": "agNumberColumnFilter",
        #     "headerName": "Score",
        #     "width": 100,
        # },
        {
            "field": "norm_score",
            "initialSort": "desc",  # sort based on this column
            "headerName": "% Match",
            "filter": "agNumberColumnFilter",
            "width": 130,
        },
    ]
    return c


def get_alignment_stats():
    return [
        {
            "field": "identities",
            "headerName": "# matches",
            "filter": "agNumberColumnFilter",
            "width": 110,
        },
        {
            "field": "gaps",
            "headerName": "# gaps",
            "filter": "agNumberColumnFilter",
            "width": 80,
        },
        {
            "field": "mismatches",
            "headerName": "# mismatches",
            "filter": "agNumberColumnFilter",
            "width": 127,
        },
        {
            "field": gs.cc_seq_alignment_mismatches,
            "headerName": "Mismatched Residue",
            "width": 200,
        },
    ]


def get_alignment_string():
    return [
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


def get_top_variant_column_defs(df):
    """
    Returns column definitions and setup for dash ag grid table per experiment
    """
    column_def = (
        get_cas({"flex": 2})
        + get_plate_well({"flex": 2})
        + get_substitutions({"flex": 3})
        + get_fitness_ratio(
            {"flex": 2},
            {"flex": 2, "cellStyle": {"styleConditions": vis.data_bars_group_mean_colorscale(df)}},
        )
    )

    return column_def


def get_all_experiments_column_defs():
    """
    Returns column definitions and setup for dash ag grid table for all experiments
    """

    column_def = (
        get_checkbox()
        + get_experiment_id({"flex": 3})
        + get_experiment_name({"flex": 3})
        + get_experiment_meta_cas({"flex": 4}, {"flex": 4})
        + get_experiment_meta(
            {"flex": 3},
            {"flex": 3},
            {"flex": 3},
            {"flex": 3},  # mutagenesis method
            {"flex": 2},
        )
    )

    return column_def


def get_matched_sequences_column_defs():
    """
    Returns column definitions for the matched sequences
    """
    column_def = (
        get_experiment_id({"width": 120, "pinned": "left"})
        + get_cas({"width": 120, "pinned": "left"})
        + get_experiment_name({"width": 130})
        + get_alignment_scores()
        + get_experiment_meta_cas({"width": 130}, {"width": 130})
        + get_experiment_meta(
            {"width": 120},
            {"width": 120},
            {"width": 130},
            {
                "width": 130,  # mutagenesis method
                "valueFormatter": {"function": "shortenMutagenesisMethod(params.value)"},
            },
            {"width": 90},
        )
        + get_alignment_stats()
    )
    column_def += [
        {
            "field": gs.cc_hot_indices_per_cas,
            "headerName": "Hot Residue/CAS",
            "width": 250,
        },
        {
            "field": gs.cc_cold_indices_per_cas,
            "headerName": "Cold Residue/CAS",
            "width": 250,
        },
    ]
    column_def += get_alignment_string()

    return column_def


def get_matched_sequences_exp_hot_cold_data_column_defs():
    """
    Returns column definitions for the matched sequences experiment data
    """
    column_def = get_experiment_id({"width": 120, "pinned": "left"})
    column_def += [
        {
            "field": gs.cc_hot_cold_type,
            "headerName": "Type",
            # "width": 150,
            "flex": 1,
        },
    ]
    column_def += (
        get_cas({"flex": 2})
        + get_plate_well({"flex": 2})
        + get_substitutions({"flex": 3})
        + get_fitness_ratio({"flex": 2}, {"flex": 2})
    )
    column_def += [
        {
            "field": gs.c_aa_sequence,
            "headerName": "Parent Amino Acid Sequence",
            "tooltipField": gs.c_aa_sequence,
            "flex": 5,
            # "cellStyle": {"styleConditions": vis.data_bars_colorscale(df, gs.c_fitness_value)},
        },
    ]
    return column_def


def get_an_experiments_matched_sequences_column_defs():
    """
    Returns column definitions for the matched sequences
    """
    column_def = (
        get_experiment_id({"width": 160, "pinned": "left", "initialSort": "desc"})
        + get_experiment_name({"width": 130})
        + get_alignment_scores()
    )
    # column_def += [
    #     {
    #         "field": "exp_cas",
    #         "headerName": "My CAS",
    #         "cellClass": "matched-seq-cas-1",
    #         "width": 120,
    #     },
    #     {
    #         "field": "exp_index",
    #         "headerName": "My Sub Index",
    #         "cellClass": "matched-seq-cas-1",
    #         "width": 120,
    #     },
    # ]
    column_def += (
        get_cas({"width": 120})
        + get_substitutions({"width": 150})
        + get_plate_well({"width": 130})
        + get_fitness_ratio({"width": 130}, {"width": 130})
        + get_experiment_meta_cas({"width": 130}, {"width": 130})
        + get_experiment_meta(
            {"width": 120},
            {"width": 120},
            {"width": 130},
            {
                "width": 130,  # mutagenesis method
                "valueFormatter": {"function": "shortenMutagenesisMethod(params.value)"},
            },
            {"width": 90},
        )
        + get_alignment_stats()
        + get_alignment_string()
    )

    return column_def
