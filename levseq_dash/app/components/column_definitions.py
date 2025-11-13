"""
AG Grid column definitions for data tables.

This module provides reusable column definition functions for various data grids
throughout the application, including experiments, sequence alignments, and variant data.

DO NOT change definition here if you don't know what you are doing :)
This will affect all tables in the UI
"""

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis


def get_checkbox():
    """
    Create checkbox column definition for row selection.

    Returns:
        list: Column definition with checkbox selection enabled.
    """
    return [
        {  # Checkbox column
            "headerCheckboxSelection": True,
            "checkboxSelection": True,
            "headerName": "",
            "width": 30,
        }
    ]


def get_experiment_id(record):
    """
    Create experiment ID column definition.

    Args:
        record: Optional dictionary to update column properties.

    Returns:
        list: Column definition for experiment ID with truncated display.
    """
    c = [
        {
            "field": gs.cc_experiment_id,
            "headerName": gs.header_experiment_id,
            # "filter": "agNumberColumnFilter",
            # show the first 5 characters of the prefix plus the first 5 of the uuid
            "valueFormatter": {
                "function": "params.value.slice(0, 13)"  # shows first 11 chars
            },
            "tooltipField": "experiment_id",  # show full UUID on hover
        }
    ]
    if record:
        c[0].update(record)

    return c


def get_experiment_name(record):
    """
    Create experiment name column definition.

    Args:
        record: Optional dictionary to update column properties.

    Returns:
        list: Column definition for experiment name.
    """
    c = [
        {
            "field": gs.c_experiment_name,
            "headerName": gs.header_experiment_name,
            "tooltipField": gs.c_experiment_name,
        }
    ]
    if record:
        c[0].update(record)

    return c


def get_experiment_meta(record_1, record_2, record_3, record_4, record_5):
    """
    Create experiment metadata column definitions.

    Args:
        record_1: Optional properties for experiment_date column.
        record_2: Optional properties for upload_time_stamp column.
        record_3: Optional properties for assay column.
        record_4: Optional properties for mutagenesis_method column.
        record_5: Optional properties for plates_count column.

    Returns:
        list: Column definitions for experiment metadata fields.
    """
    c = [
        {
            "field": "experiment_date",
            "headerName": "Date",
            "filter": "agDateColumnFilter",
            "tooltipField": "experiment_date",
        },
        {
            "field": "upload_time_stamp",
            "headerName": "Uploaded",
            "filter": "agDateColumnFilter",
            "tooltipField": "upload_time_stamp",
        },
        {
            "field": "assay",
            "tooltipField": "assay",
        },
        {
            "field": gs.cc_mutagenesis,
            "headerName": gs.header_mutagenesis,
            "tooltipField": gs.cc_mutagenesis,
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


def get_experiment_doi(record):
    """
    Create DOI column definition with link renderer.

    Args:
        record: Optional dictionary to update column properties.

    Returns:
        list: Column definition for DOI with custom cell renderer.
    """
    c = [
        {"field": "doi", "headerName": "DOI", "tooltipField": "doi", "cellRenderer": "DOILink"},
    ]
    if record:
        c[0].update(record)
    return c


def get_experiment_meta_smiles(record_1, record_2):
    """
    Create substrate and product SMILES column definitions.

    Args:
        record_1: Optional properties for substrate column.
        record_2: Optional properties for product column.

    Returns:
        list: Column definitions for substrate and product SMILES.
    """
    c = [
        {
            "field": gs.cc_substrate,
            # "headerName": gs.header_substrate,
            "tooltipField": gs.cc_substrate,
        },
        {
            "field": gs.cc_product,
            # "headerName": gs.header_product,
            "tooltipField": gs.cc_product,
        },
    ]

    if record_1:
        c[0].update(record_1)
    if record_2:
        c[1].update(record_2)

    return c


def get_smiles(record):
    """
    Create SMILES column definition.

    Args:
        record: Optional dictionary to update column properties.

    Returns:
        list: Column definition for SMILES string.
    """
    c = [
        {
            "field": gs.c_smiles,
            "headerName": gs.header_smiles,
            "tooltipField": gs.c_smiles,
        }
    ]
    if record:
        c[0].update(record)
    return c


def get_plate_well(record_1):
    """
    Create plate and well column definitions.

    Args:
        record_1: Optional properties for plate column.

    Returns:
        list: Column definitions for plate and well identifiers.
    """
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
    """
    Create fitness value and ratio column definitions.

    Args:
        record_1: Optional properties for fitness_value column.
        record_2: Optional properties for ratio column.

    Returns:
        list: Column definitions for fitness and ratio values.
    """
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
    """
    Create amino acid substitutions column definition.

    Args:
        record: Optional dictionary to update column properties.

    Returns:
        list: Column definition for substitutions display.
    """
    c = [
        {
            "field": gs.c_substitutions,
            # mouse hover over the truncated cell will show the contents of the cell
            "tooltipField": gs.c_substitutions,
            "headerName": gs.header_substitutions,
        },
    ]
    if record:
        c[0].update(record)
    return c


def get_alignment_scores():
    """
    Create alignment score column definitions.

    Returns:
        list: Column definitions for normalized alignment scores.
    """
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
    """
    Create alignment statistics column definitions.

    Returns:
        list: Column definitions for matches, gaps, and mismatches.
    """
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
            "tooltipField": gs.cc_seq_alignment_mismatches,
            "width": 300,
        },
    ]


def get_alignment_string():
    """
    Create sequence alignment string column definition.

    Returns:
        list: Column definition for alignment visualization with custom renderer.
    """
    return [
        {
            "field": gs.cc_seq_alignment,
            "autoHeight": True,  # Makes the row height adjust to content
            "cellRenderer": "seqAlignmentVis",
            "cellStyle": {
                "whiteSpace": "pre-wrap",
                "fontFamily": "monospace",
                "fontSize": 10,
                "lineHeight": "1.1",
                "padding": "5px",
            },
            "width": 7000,
        },
    ]


def get_top_variant_column_defs(df):
    """
    Create column definitions for top variants table in experiment view.

    Args:
        df: DataFrame for calculating conditional cell styles.

    Returns:
        list: Complete column definitions for top variants display.
    """
    column_def = (
        get_smiles({"flex": 2})
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
    Create column definitions for all experiments table in lab view.

    Returns:
        list: Complete column definitions including checkbox and metadata.
    """

    column_def = (
        get_checkbox()
        + get_experiment_id({"width": 170})
        + get_experiment_name({"flex": 10})
        + get_experiment_doi({"flex": 4})
        + get_experiment_meta_smiles({"flex": 5}, {"flex": 5})
        + get_experiment_meta(
            {"flex": 3},  # experiment_date
            {"flex": 4, "initialSort": "desc"},  # sort by upload_time_stamp
            {"flex": 3},  # assay
            {"flex": 3},  # mutagenesis method
            {"flex": 2},
        )
    )

    return column_def


def get_matched_sequences_column_defs():
    """
    Create column definitions for matched sequences alignment table.

    Returns:
        list: Complete column definitions including alignment stats and strings.
    """
    column_def = (
        # if you want to pin any of the columns, here's how you do it
        # get_experiment_id({"width": 120, "pinned": "left"})
        # + get_smiles({"width": 150, "pinned": "left"})
        get_experiment_id({"width": 170})
        + get_smiles({"width": 200})
        + get_experiment_name({"width": 250})
        + get_alignment_scores()
        + get_experiment_meta_smiles({"width": 200}, {"width": 200})
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
            "field": gs.cc_hot_indices_per_smiles,
            "headerName": gs.header_hot_indices_per_smiles,
            "width": 250,
        },
        {
            "field": gs.cc_cold_indices_per_smiles,
            "headerName": gs.header_cold_indices_per_smiles,
            "width": 250,
        },
    ]
    column_def += get_alignment_string()

    return column_def


def get_matched_sequences_exp_hot_cold_data_column_defs():
    """
    Create column definitions for hot/cold spot experiment data table.

    Returns:
        list: Complete column definitions including hot/cold type indicators.
    """
    column_def = get_experiment_id({"width": 170, "pinned": "left"})
    column_def += get_experiment_name({"width": 250})
    column_def += [
        {
            "field": gs.cc_hot_cold_type,
            "headerName": gs.header_hot_cold_type,
            # "width": 150,
            "flex": 1,
        },
    ]
    column_def += (
        get_smiles({"flex": 2})
        + get_plate_well({"flex": 2})
        + get_substitutions({"flex": 3})
        + get_fitness_ratio({"flex": 2}, {"flex": 2})
    )
    column_def += [
        {
            "field": "parent_sequence",
            "headerName": gs.header_aa_sequence,
            "tooltipField": "parent_sequence",
            "flex": 5,
            # "cellStyle": {"styleConditions": vis.data_bars_colorscale(df, gs.c_fitness_value)},
        },
    ]
    return column_def


def get_an_experiments_matched_sequences_column_defs():
    """
    Create column definitions for related variants in experiment view.

    Returns:
        list: Complete column definitions for experiment-specific matched sequences.
    """
    column_def = (
        # It doesn't make sense to sort by experiment ID but keeping commented for PI if of interest
        # get_experiment_id({"width": 120, "pinned": "left", "initialSort": "desc"})
        get_experiment_id({"width": 170, "pinned": "left"})
        + get_experiment_name({"width": 250})
        + get_alignment_scores()
    )
    column_def += (
        get_smiles({"width": 150})
        + get_substitutions({"width": 200})
        + get_plate_well({"width": 130})
        + get_fitness_ratio({"width": 130}, {"width": 130})
        + get_experiment_meta_smiles({"width": 150}, {"width": 150})
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
