import numpy as np
import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.data_manager.experiment import Experiment, MutagenesisMethod


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
    assert experiment_ep_pcr.data_df.shape[1] == 7


def test_experiment_with_geometry_in_bytes(path_exp_ep_data):
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
    disk_manager_from_test_data, experiment_ep_pcr, experiment_ep_pcr_metadata, attribute
):
    """Test experiment assay by accessing metadata via DataManager"""
    exp_id = experiment_ep_pcr_metadata["experiment_id"]
    assert (
        disk_manager_from_test_data.get_experiment_metadata(exp_id)[attribute] == experiment_ep_pcr_metadata[attribute]
    )


def test_experiment_ep_pcr_unique_smiles(experiment_ep_pcr):
    assert len(experiment_ep_pcr.unique_smiles_in_data) == 2


@pytest.mark.parametrize(
    "attribute, expected_value",
    [
        ("experiment_name", "flatten_ep_processed_xy_cas"),
        ("experiment_date", "2021-02-23"),
        ("substrate", "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O.C1=CC=C(C=C1)C=O"),
        ("product", "C1=CC=C(C=C1)C=O"),
        ("mutagenesis_method", MutagenesisMethod.epPCR.value),
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
        (0, gs.c_alignment_count, 0),
        (0, gs.c_alignment_probability, 0.0),
        (0, gs.c_substitutions, "#N.A.#"),
        (0, gs.c_smiles, "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"),
        (94, gs.c_fitness_value, 1917633.707),
        (0, gs.c_plate, "20240422-ParLQ-ep1-300-1"),
        (0, gs.c_well, "A1"),
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
        # gs.c_aa_sequence,
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


# =============================================================================
#                           EXCEPTION TESTING
# =============================================================================


def test_experiment_init_none_data_file_path():
    """Test Experiment initialization with None data file path."""
    with pytest.raises(Exception):
        Experiment(experiment_data_file_path=None, geometry_file_path="dummy.cif")


def test_experiment_init_none_geometry_file_path():
    """Test Experiment initialization with None geometry file path."""
    with pytest.raises(Exception):
        Experiment(experiment_data_file_path="dummy.csv", geometry_file_path=None)


def test_experiment_init_nonexistent_data_file():
    """Test Experiment initialization with non-existent data file."""
    with pytest.raises(ValueError):
        Experiment(experiment_data_file_path="nonexistent.csv", geometry_file_path="dummy.cif")


def test_experiment_init_nonexistent_geometry_file(tmp_path):
    """Test Experiment initialization with non-existent geometry file."""
    # Create a dummy CSV file
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1,col2\nval1,val2")

    with pytest.raises(ValueError):
        Experiment(experiment_data_file_path=str(csv_file), geometry_file_path="nonexistent.cif")


def test_experiment_init_empty_data_file(tmp_path):
    """Test Experiment initialization with empty data file."""
    # Create empty CSV file
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")

    # Create dummy geometry file
    cif_file = tmp_path / "test.cif"
    cif_file.write_text("test content")

    with pytest.raises(Exception):
        Experiment(experiment_data_file_path=str(csv_file), geometry_file_path=str(cif_file))


def test_experiment_init_valid_columns_no_data(tmp_path):
    """Test Experiment initialization with valid column headers but no data rows."""
    # Create CSV file with only headers
    headers = gs.experiment_core_data_list
    csv_content = ",".join(headers)

    csv_file = tmp_path / "empty_with_headers.csv"
    csv_file.write_text(csv_content)

    # Create dummy geometry file
    cif_file = tmp_path / "test.cif"
    cif_file.write_text("test content")

    with pytest.raises(Exception, match="Experiment data file is empty."):
        Experiment(experiment_data_file_path=str(csv_file), geometry_file_path=str(cif_file))


def test_run_sanity_checks_empty_dataframe():
    """Test run_sanity_checks_on_experiment_file with empty DataFrame."""
    empty_df = pd.DataFrame()
    with pytest.raises(Exception):
        Experiment.run_sanity_checks_on_experiment_file(empty_df)


def test_run_sanity_checks_missing_columns():
    """Test run_sanity_checks_on_experiment_file with missing required columns."""
    # Create DataFrame with only some required columns
    df = pd.DataFrame(
        {
            gs.c_smiles: ["CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"],
            gs.c_plate: ["plate1"],
            # Missing other required columns
        }
    )

    with pytest.raises(ValueError, match="Experiment file is missing required columns"):
        Experiment.run_sanity_checks_on_experiment_file(df)


def test_run_sanity_checks_no_parent_entry():
    """Test run_sanity_checks_on_experiment_file without #PARENT# entry."""
    # Create DataFrame with all required columns but no #PARENT# entry
    df = pd.DataFrame(
        {
            gs.c_smiles: ["CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"],
            gs.c_plate: ["plate1"],
            gs.c_well: ["A1"],
            gs.c_alignment_count: [1],
            gs.c_substitutions: ["A123B"],  # No #PARENT# entry
            gs.c_alignment_probability: [1.0],
            gs.c_aa_sequence: ["MAVPGY"],
            gs.c_fitness_value: [100.0],
        }
    )

    with pytest.raises(ValueError):
        Experiment.run_sanity_checks_on_experiment_file(df)


@pytest.mark.parametrize(
    "smiles",
    [
        [""],
        ["   "],  # Whitespace-only SMILES
        ["invalid_smiles_string"],  # Invalid SMILES
    ],
)
def test_run_sanity_checks_empty_smiles(smiles):
    """Test run_sanity_checks_on_experiment_file with empty SMILES string."""
    df = pd.DataFrame(
        {
            gs.c_smiles: smiles,  # Empty SMILES
            gs.c_plate: ["plate1"],
            gs.c_well: ["A1"],
            gs.c_alignment_count: [1],
            gs.c_substitutions: ["#PARENT#"],
            gs.c_alignment_probability: [1.0],
            gs.c_aa_sequence: ["MAVPGY"],
            gs.c_fitness_value: [100.0],
        }
    )

    with pytest.raises(ValueError):
        Experiment.run_sanity_checks_on_experiment_file(df)


def test_run_sanity_checks_valid_data():
    """Test run_sanity_checks_on_experiment_file with valid data."""
    df = pd.DataFrame(
        {
            gs.c_smiles: ["CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"],  # Valid SMILES
            gs.c_plate: ["plate1"],
            gs.c_well: ["A1"],
            gs.c_alignment_count: [1],
            gs.c_substitutions: ["#PARENT#"],
            gs.c_alignment_probability: [1.0],
            gs.c_aa_sequence: ["MAVPGY"],
            gs.c_fitness_value: [100.0],
        }
    )

    # Should not raise any exception
    result = Experiment.run_sanity_checks_on_experiment_file(df)
    assert result is True


def test_extract_parent_sequence_success(path_exp_ep_data):
    """Test extract_parent_sequence with valid data."""
    # Use the existing fixture data which should have #PARENT# entries
    data_df = pd.read_csv(path_exp_ep_data[0])
    parent_sequence = Experiment.extract_parent_sequence(data_df)

    assert parent_sequence is not None
    assert len(parent_sequence) > 0

    # compare with the JSON file content
    import json

    with open(path_exp_ep_data[2], "r") as json_file:
        data = json.load(json_file)

    # Extract parent_sequence from the JSON file
    json_parent_sequence = data.get("parent_sequence")
    assert json_parent_sequence == parent_sequence


def test_extract_parent_sequence_no_parent():
    """Test extract_parent_sequence when no #PARENT# entry exists."""
    df = pd.DataFrame(
        {
            gs.c_smiles: ["CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"],
            gs.c_plate: ["plate1"],
            gs.c_well: ["A1"],
            gs.c_alignment_count: [1],
            gs.c_substitutions: ["A123B"],  # No #PARENT# entry
            gs.c_alignment_probability: [1.0],
            gs.c_aa_sequence: ["MAVPGY"],
            gs.c_fitness_value: [100.0],
        }
    )

    with pytest.raises(IndexError):
        Experiment.extract_parent_sequence(df)


def test_extract_plates_list_success(experiment_ep_pcr):
    """Test extract_plates_list with valid data."""
    plates = Experiment.extract_plates_list(experiment_ep_pcr.data_df)
    assert isinstance(plates, list)
    assert len(plates) > 0


def test_extract_plates_list_empty_dataframe():
    """Test extract_plates_list with empty DataFrame."""
    empty_df = pd.DataFrame()
    plates = Experiment.extract_plates_list(empty_df)
    assert plates == []


def test_experiment_empty_geometry_file(tmp_path, path_exp_ep_data):
    """Test Experiment initialization with empty geometry file."""
    # Create empty geometry file
    empty_cif = tmp_path / "empty.cif"
    empty_cif.write_text("")

    with pytest.raises(Exception, match="Error loading experiment data file"):
        Experiment(
            experiment_data_file_path=path_exp_ep_data[0],
            geometry_file_path=empty_cif,
        )


def test_exp_hot_cold_spots_with_empty_df(experiment_ep_pcr, mocker):
    """Test exp_hot_cold_spots when data_df is empty."""
    # Mock the data_df to be empty
    mocker.patch.object(experiment_ep_pcr, "data_df", pd.DataFrame())

    with pytest.raises(Exception, match="Experiment data is empty"):
        experiment_ep_pcr.exp_hot_cold_spots(1)


def test_exp_get_processed_core_data_with_empty_df(experiment_ep_pcr, mocker):
    """Test exp_get_processed_core_data_for_valid_mutation_extractions with empty data."""
    # Mock the data_df to be empty
    mocker.patch.object(experiment_ep_pcr, "data_df", pd.DataFrame())

    with pytest.raises(Exception, match="Experiment data is empty"):
        experiment_ep_pcr.exp_get_processed_core_data_for_valid_mutation_extractions()


@pytest.mark.parametrize(
    "well_value",
    [
        [""],  # Empty well
        [np.nan],  # NaN well
        ["Z99"],  # Invalid: Z is not A-H, 99 is not 1-12
    ],
)
def test_sanity_check_well_value(well_value):
    """Test run_sanity_checks_on_experiment_file with empty well value."""
    df = pd.DataFrame(
        {
            gs.c_smiles: ["C1=CC=C(C=C1)C=O"],
            gs.c_plate: ["plate1"],
            gs.c_well: well_value,  # Empty well
            gs.c_alignment_count: [1],
            gs.c_substitutions: [gs.hashtag_parent],
            gs.c_alignment_probability: [1.0],
            gs.c_aa_sequence: ["MAVPGY"],
            gs.c_fitness_value: [100.0],
        }
    )

    with pytest.raises(ValueError):
        Experiment.run_sanity_checks_on_experiment_file(df)


def test_sanity_check_duplicate_wells():
    """Test run_sanity_checks_on_experiment_file with duplicate wells in same smiles-plate combo."""
    df = pd.DataFrame(
        {
            gs.c_smiles: ["C1=CC=C(C=C1)C=O", "C1=CC=C(C=C1)C=O"],
            gs.c_plate: ["plate1", "plate1"],
            gs.c_well: ["A1", "A1"],  # Duplicate well
            gs.c_alignment_count: [1, 1],
            gs.c_substitutions: [gs.hashtag_parent, "A123B"],
            gs.c_alignment_probability: [1.0, 1.0],
            gs.c_aa_sequence: ["MAVPGY", "MAVPGY"],
            gs.c_fitness_value: [100.0, 200.0],
        }
    )

    with pytest.raises(ValueError, match="Duplicate wells in"):
        Experiment.run_sanity_checks_on_experiment_file(df)
