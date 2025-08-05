import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.data_manager.experiment import Experiment


@pytest.mark.parametrize(
    "index, smiles",
    [(0, "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"), (1, "C1=CC=C(C=C1)C=O")],
)
def test_experiment_ep_pcr_smiles(experiment_ep_pcr, index, smiles):
    assert experiment_ep_pcr.unique_smiles_in_data[index] == smiles


@pytest.mark.parametrize(
    "index, plate",
    [
        (0, "20240422-ParLQ-ep1-300-1"),
        (2, "20240422-ParLQ-ep1-500-1"),
        (4, "20240502-ParLQ-ep2-300-1"),
        (6, "20240502-ParLQ-ep2-300-3"),
        (8, "20240502-ParLQ-ep2-500-2"),
    ],
)
def test_experiment_ep_pcr_plated(experiment_ep_pcr, index, plate):
    assert experiment_ep_pcr.plates[index] == plate


def test_experiment_ep_pcr_data_shape(experiment_ep_pcr):
    assert experiment_ep_pcr.data_df.shape[0] == 1920
    assert experiment_ep_pcr.data_df.shape[1] == 8


def test_experiment_with_geometry_in_bytes(path_exp_ep_data, assay_list):
    # load as bytes
    from levseq_dash.app.data_manager.experiment import Experiment

    # read the file as bytes
    with open(path_exp_ep_data[1], "rb") as f:
        byte_content = f.read()

    if byte_content:
        experiment_with_bytes_geometry = Experiment(
            experiment_data_file_path=path_exp_ep_data[0],
            geometry_file_path=path_exp_ep_data[1],
        )
        assert isinstance(experiment_with_bytes_geometry.geometry_base64_bytes, bytes)
        assert len(experiment_with_bytes_geometry.geometry_base64_bytes) == 134480


@pytest.mark.parametrize(
    "attribute",
    [
        "experiment_name",
        "experiment_date",
        "substrate",
        "product",
        "mutagenesis_method",
    ],
)
def test_experiment_loaded_metadata(
    dbmanager_read_all_from_file, experiment_ep_pcr, experiment_ep_pcr_metadata, attribute
):
    """Test experiment assay by accessing metadata via DataManager"""
    exp_id = experiment_ep_pcr_metadata["experiment_id"]
    assert dbmanager_read_all_from_file.experiments_metadata[exp_id][attribute] == experiment_ep_pcr_metadata[attribute]


def test_experiment_ep_pcr_unique_smiles(experiment_ep_pcr):
    assert len(experiment_ep_pcr.unique_smiles_in_data) == 2


@pytest.mark.parametrize(
    "attribute, expected_value",
    [
        ("experiment_name", "flatten_ep_processed_xy_cas"),
        ("experiment_date", "2021-02-23"),
        ("substrate", "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O.C1=CC=C(C=C1)C=O"),
        ("product", "C1=CC=C(C=C1)C=O"),
        ("mutagenesis_method", "Error-prone PCR (epPCR)"),
        ("plates_count", 10),
        (
            "parent_sequence",
            "MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQGSNQHLIYYFG"
            "DKSGRPIPQYLEAVRKRFGLWIIDTLCKPLDRQWLNYMYEIGLRHHRTKKGKTDGVDTVEHIPLRYMIAFIA"
            "PIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAIWSYPYAKTGEWLE",
        ),
    ],
)
def test_experiment_metadata(experiment_ep_pcr_metadata, attribute, expected_value):
    assert experiment_ep_pcr_metadata[attribute] == expected_value


def test_experiment_ep_pcr_plates(experiment_ep_pcr):
    assert len(experiment_ep_pcr.plates) == 10


def test_experiment_ep_pcr_geometry_base64_bytes(experiment_ep_pcr):
    assert experiment_ep_pcr.geometry_base64_bytes is not None
    assert isinstance(experiment_ep_pcr.geometry_base64_bytes, bytes)
    assert len(experiment_ep_pcr.geometry_base64_bytes) > 0


@pytest.mark.parametrize(
    "index, key, value",
    [
        (0, gs.c_aa_sequence, "#N.A.#"),
        (0, gs.c_alignment_count, 0),
        (0, gs.c_alignment_probability, 0.0),
        (0, gs.c_substitutions, "#N.A.#"),
        (0, gs.c_smiles, "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"),
        (94, gs.c_fitness_value, 1917633.707),
        (0, gs.c_plate, "20240422-ParLQ-ep1-300-1"),
        (0, gs.c_well, "A1"),
        (
            36,
            "aa_sequence",
            "MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQGSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTLCKPLDRQWL"
            "NYMYEIGLRHHRTKKGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAIWSYPYAKTGEWLE",
        ),
        (51, gs.c_alignment_count, 29),
        (61, gs.c_alignment_probability, 0.0),
        (69, gs.c_substitutions, "#PARENT#"),
        (99, gs.c_smiles, "C1=CC=C(C=C1)C=O"),
        (99, gs.c_fitness_value, 1244116.159),
        (42, gs.c_plate, "20240422-ParLQ-ep1-300-1"),
        (0, gs.c_well, "A1"),
    ],
)
def test_exp_core_data(experiment_ep_pcr, index, key, value):
    df = experiment_ep_pcr.data_df
    assert index in df.index and df.loc[index, key] == value


def test_exp_hot_cold_spots_structure(experiment_ep_pcr):
    """Tests if the function returns dataframes with expected structure."""
    hot_cold_spots_df, hot_cold_residue_per_smiles = experiment_ep_pcr.exp_hot_cold_spots(2)
    assert isinstance(hot_cold_spots_df, pd.DataFrame)
    assert isinstance(hot_cold_residue_per_smiles, pd.DataFrame)

    # Check expected columns in hot_cold_spots_df
    expected_cols = {
        gs.c_smiles,
        gs.c_plate,
        gs.c_well,
        gs.c_substitutions,
        gs.c_aa_sequence,
        gs.c_fitness_value,
        gs.cc_hot_cold_type,
        gs.cc_ratio,
    }
    assert expected_cols.issubset(hot_cold_spots_df.columns)


@pytest.mark.parametrize(
    "n",
    [1, 2, 3, 4, 5, 6],
)
def test_exp_hot_cold_spots_count(experiment_ep_pcr, experiment_ep_pcr_metadata, n):
    """Tests if the function returned value count is consistent with n"""
    plates_count = experiment_ep_pcr_metadata["plates_count"]
    hot_cold_spots_df, hot_cold_residue_per_smiles = experiment_ep_pcr.exp_hot_cold_spots(n)
    count = len(experiment_ep_pcr.unique_smiles_in_data) * plates_count * 2 * n
    assert count == hot_cold_spots_df.shape[0]


def test_exp_hot_cold_spots_exception(experiment_ep_pcr):
    with pytest.raises(Exception):
        experiment_ep_pcr.exp_hot_cold_spots(0)


@pytest.mark.parametrize(
    "n",
    [1, 2, 3, 4, 5, 6],
)
def test_exp_hot_cold_spots_filtering(experiment_ep_pcr, n):
    """Tests if invalid data is removed."""

    hot_cold_spots_df, _ = experiment_ep_pcr.exp_hot_cold_spots(n)

    # Ensure the invalid rows are removed
    assert not hot_cold_spots_df[gs.c_substitutions].str.contains(r"[#-]", na=True).any()
    assert not hot_cold_spots_df[gs.c_aa_sequence].str.contains(r"[#-]", na=True).any()


@pytest.mark.parametrize(
    "n",
    [1, 2, 3, 4, 5, 6],
)
def test_exp_hot_cold_spots_n_values(experiment_ep_pcr, n):
    """Tests if the function correctly extracts top/bottom N residues."""
    hot_cold_spots_df, _ = experiment_ep_pcr.exp_hot_cold_spots(n)

    # Ensure we get exactly N hot and cold variants per smiles + Plate combo
    hot_count = hot_cold_spots_df[hot_cold_spots_df[gs.cc_hot_cold_type] == gs.seg_align_hot].shape[0]
    cold_count = hot_cold_spots_df[hot_cold_spots_df[gs.cc_hot_cold_type] == gs.seg_align_cold].shape[0]

    assert hot_count == cold_count


@pytest.mark.parametrize(
    "n",
    [1, 2, 3, 4, 5, 6],
)
def test_exp_hot_cold_spots_grouping(experiment_ep_pcr, n):
    """Tests if the function correctly groups by smiles and extracts substitution indices."""
    _, hot_cold_residue_per_smiles = experiment_ep_pcr.exp_hot_cold_spots(n)

    # Ensure extracted smiles count is consistent
    assert len(hot_cold_residue_per_smiles[gs.c_smiles].unique()) == len(experiment_ep_pcr.unique_smiles_in_data)
