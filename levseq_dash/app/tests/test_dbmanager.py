import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.config import settings
from levseq_dash.app.data_manager.experiment import MutagenesisMethod
from levseq_dash.app.utils import utils

num_samples = 2  # change this if more data is added


def test_db_load_examples(disk_manager_from_test_data):
    assert len(disk_manager_from_test_data.get_all_lab_experiments_with_meta_data()) == num_samples


@pytest.mark.parametrize(
    "experiment_id",
    ["flatten_ep_processed_xy_cas", "flatten_ssm_processed_xy_cas"],
)
def test_get_experiment(disk_manager_from_test_data, experiment_id):
    """
    test getting experiments by their ids
    """
    exp = disk_manager_from_test_data.get_experiment(experiment_id)
    assert len(exp.plates) > 0
    assert not exp.data_df.empty


def test_get_experiment_out_of_bounds(disk_manager_from_test_data):
    """
    look up for a non-existent experiment will return none
    """
    with pytest.raises(Exception):
        disk_manager_from_test_data.get_experiment("randon_id_that_does_not_exist")


def test_db_load_assay(disk_manager_from_test_data):
    assert len(disk_manager_from_test_data.assay_list) == 3


def test_db_get_lab_experiments_with_meta_data_general(disk_manager_from_test_data):
    data_list_of_dict = disk_manager_from_test_data.get_all_lab_experiments_with_meta_data()
    assert len(data_list_of_dict) == num_samples
    df = pd.DataFrame.from_records(data_list_of_dict)
    assert df.shape[0] == num_samples
    assert df.shape[1] == 11


@pytest.mark.parametrize(
    "index,name,n_plates, product",
    [
        (0, "flatten_ep_processed_xy_cas", 10, "C1=CC=C(C=C1)C=O"),
        (1, "flatten_ssm_processed_xy_cas", 4, "C1=CC=C(C=C1)C=O"),
    ],
)
def test_db_get_lab_experiments_with_meta_data_data(disk_manager_from_test_data, index, name, n_plates, product):
    list_of_all_lab_experiments_with_meta = disk_manager_from_test_data.get_all_lab_experiments_with_meta_data()
    sorted_list = sorted(list_of_all_lab_experiments_with_meta, key=lambda x: x[gs.c_experiment_name])
    assert sorted_list[index][gs.c_experiment_name] == name
    assert sorted_list[index]["plates_count"] == n_plates
    assert sorted_list[index]["product"] == product


@pytest.mark.parametrize(
    "index",
    [0, 1],
)
def test_extract_all_substrate_product_smiles_from_lab_data(disk_manager_from_test_data, index):
    """
    This test is similar to below but will test the substrates
    """
    list_of_all_lab_experiments_with_meta = disk_manager_from_test_data.get_all_lab_experiments_with_meta_data()

    all_smiles = utils.extract_all_substrate_product_smiles_from_lab_data(list_of_all_lab_experiments_with_meta)
    assert len(all_smiles) != 0
    # get the substrate from the test data and make sure they are found in the unique list
    substrates = list_of_all_lab_experiments_with_meta[index][gs.cc_substrate]
    assert (all_smiles.find(c) != -1 for c in substrates)

    products = list_of_all_lab_experiments_with_meta[index][gs.cc_product]
    assert (all_smiles.find(c) != -1 for c in products)


def test_get_lab_sequences(disk_manager_from_test_data):
    list_of_sequences = disk_manager_from_test_data.get_all_lab_sequences()
    assert len(list_of_sequences) != 0


def test_load_config():
    """
    Config file that is distributed must have the app mode set
    """
    # Use centralized settings helpers for config and mode checks
    assert settings.is_disk_mode() or settings.is_db_mode()


def test_get_assays(disk_manager_from_test_data):
    assert len(disk_manager_from_test_data.get_assays()) == 3


def test_setup_data_path_not_exists(mocker):
    """Test _setup_data_path raises error when path doesn't exist."""
    mock = mocker.patch("levseq_dash.app.config.settings.load_config")
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": "/nonexistent/path"},
    }

    from levseq_dash.app.data_manager.disk_manager import DiskDataManager

    with pytest.raises(FileNotFoundError):
        DiskDataManager()


def test_check_for_duplicate_experiment_no_duplicate(disk_manager_from_test_data):
    """Test check_for_duplicate_experiment with unique checksum."""
    result = disk_manager_from_test_data.check_for_duplicate_experiment("some-random-checksum-value")
    assert result is False


def test_check_for_duplicate_experiment_duplicate(disk_manager_from_test_data):
    """Test check_for_duplicate_experiment with duplicate checksum."""
    exp_list = disk_manager_from_test_data.get_all_lab_experiments_with_meta_data()
    existing_checksum = exp_list[0]["csv_checksum"]

    with pytest.raises(ValueError, match="DUPLICATE experiment data detected"):
        disk_manager_from_test_data.check_for_duplicate_experiment(existing_checksum)


def test_delete_experiment_nonexistent(disk_manager_from_test_data):
    """Test delete_experiment returns False for nonexistent ID."""
    result = disk_manager_from_test_data.delete_experiment("nonexistent-id")
    assert result is False


def test_delete_experiment_success(disk_manager_from_temp_data, experiment_ssm_cvv_cif_bytes):
    """Test delete_experiment successfully deletes experiment."""

    # Add an experiment
    exp_id = disk_manager_from_temp_data.add_experiment_from_ui(
        experiment_name="To Delete",
        experiment_date="2025-01-01",
        substrate="C1=CC=C(C=C1)C=O",
        product="C1=CC=C(C=C1)C=O",
        assay="NMR Spectroscopy",
        mutagenesis_method=MutagenesisMethod.SSM,
        experiment_doi="",
        experiment_additional_info="",
        experiment_content_base64_string=experiment_ssm_cvv_cif_bytes[0],
        geometry_content_base64_string=experiment_ssm_cvv_cif_bytes[1],
    )

    # Verify it exists
    assert disk_manager_from_temp_data.get_experiment_metadata(exp_id) is not None

    # Delete it
    result = disk_manager_from_temp_data.delete_experiment(exp_id)
    assert result is True

    # Verify it's gone
    assert disk_manager_from_temp_data.get_experiment_metadata(exp_id) is None


def test_delete_experiment_with_cached_data(disk_manager_from_temp_data, experiment_ssm_cvv_cif_bytes):
    """Test delete_experiment removes from cache."""

    exp_id = disk_manager_from_temp_data.add_experiment_from_ui(
        experiment_name="Cached Delete",
        experiment_date="2025-01-01",
        substrate="C1=CC=C(C=C1)C=O",
        product="C1=CC=C(C=C1)C=O",
        assay="NMR Spectroscopy",
        mutagenesis_method=MutagenesisMethod.SSM,
        experiment_doi="",
        experiment_additional_info="",
        experiment_content_base64_string=experiment_ssm_cvv_cif_bytes[0],
        geometry_content_base64_string=experiment_ssm_cvv_cif_bytes[1],
    )

    # Load into cache
    exp = disk_manager_from_temp_data.get_experiment(exp_id)
    assert exp is not None

    # Delete - should remove from cache
    result = disk_manager_from_temp_data.delete_experiment(exp_id)
    assert result is True

    # Verify it's gone - metadata should be None
    assert disk_manager_from_temp_data.get_experiment_metadata(exp_id) is None

    # Verify it's gone - experiment itself should throw an exception
    with pytest.raises(Exception):
        disk_manager_from_temp_data.get_experiment(exp_id)


def test_delete_experiment_with_exception(disk_manager_from_temp_data, experiment_ssm_cvv_cif_bytes, mocker):
    """Test delete_experiment handles exceptions and returns False."""

    # Add experiment
    exp_id = disk_manager_from_temp_data.add_experiment_from_ui(
        experiment_name="Exception Test",
        experiment_date="2025-01-01",
        substrate="C1=CC=C(C=C1)C=O",
        product="C1=CC=C(C=C1)C=O",
        assay="NMR Spectroscopy",
        mutagenesis_method=MutagenesisMethod.SSM,
        experiment_doi="",
        experiment_additional_info="",
        experiment_content_base64_string=experiment_ssm_cvv_cif_bytes[0],
        geometry_content_base64_string=experiment_ssm_cvv_cif_bytes[1],
    )

    # Mock shutil.rmtree to raise an exception
    mocker.patch("shutil.rmtree", side_effect=Exception("Delete error"))

    # Should return False on exception
    with pytest.raises(Exception, match="Delete error"):
        disk_manager_from_temp_data.delete_experiment(exp_id)


def test_get_experiment_file_content(disk_manager_from_test_data):
    """Test get_experiment_file_content returns file bytes."""
    files = disk_manager_from_test_data.get_experiment_file_content("flatten_ep_processed_xy_cas")
    assert "json" in files
    assert "csv" in files
    assert isinstance(files["json"], bytes)
    assert isinstance(files["csv"], bytes)


def test_get_experiment_file_content_nonexistent(disk_manager_from_test_data):
    """Test get_experiment_file_content returns empty dict for nonexistent ID."""
    files = disk_manager_from_test_data.get_experiment_file_content("nonexistent-id")
    assert files == {}


def test_get_experiment_file_content_with_error(disk_manager_from_test_data, mocker):
    """Test get_experiment_file_content handles read errors."""

    # Mock Path.read_bytes to raise exception
    mocker.patch("pathlib.Path.read_bytes", side_effect=Exception("Read error"))

    with pytest.raises(Exception, match="Error reading files for experiment"):
        disk_manager_from_test_data.get_experiment_file_content("flatten_ep_processed_xy_cas")


def test_get_experiments_zipped_empty(disk_manager_from_test_data):
    """Test get_experiments_zipped returns None for empty list."""
    result = disk_manager_from_test_data.get_experiments_zipped([])
    assert result is None


def test_get_experiments_zipped(disk_manager_from_test_data):
    """Test get_experiments_zipped creates valid zip."""
    exp_list = disk_manager_from_test_data.get_all_lab_experiments_with_meta_data()
    zip_data = disk_manager_from_test_data.get_experiments_zipped(exp_list[:5])
    assert zip_data is not None
    assert isinstance(zip_data, bytes)
    assert len(zip_data) > 0


def test_get_experiments_zipped_with_error(disk_manager_from_test_data, mocker):
    """Test get_experiments_zipped handles file read errors."""
    exp_list = [{"experiment_id": "flatten_ep_processed_xy_cas"}]

    # Mock get_experiment_file_content to raise exception
    mocker.patch.object(
        disk_manager_from_test_data,
        "get_experiment_file_content",
        side_effect=Exception("File read error"),
    )

    with pytest.raises(Exception, match="Error adding files for experiment"):
        disk_manager_from_test_data.get_experiments_zipped(exp_list)


def test_get_experiment_uses_cache(mocker, disk_manager_from_test_data):
    """Test that get_experiment uses cache on second call."""
    experiment_id = "flatten_ssm_processed_xy_cas"

    # cache should be empty at start
    assert len(disk_manager_from_test_data._experiments_core_data_cache) == 0

    # First call - loads from disk
    exp1 = disk_manager_from_test_data.get_experiment(experiment_id)

    # cache should have one entry now
    assert len(disk_manager_from_test_data._experiments_core_data_cache) == 1

    # Second call - should use cache
    exp1_call2 = disk_manager_from_test_data.get_experiment(experiment_id)

    # Should be the same object from cache
    assert exp1 is exp1_call2

    # get another experiment
    experiment_id_2 = "flatten_ep_processed_xy_cas"
    exp2 = disk_manager_from_test_data.get_experiment(experiment_id_2)

    # cache should have two entries now
    assert len(disk_manager_from_test_data._experiments_core_data_cache) == 2
