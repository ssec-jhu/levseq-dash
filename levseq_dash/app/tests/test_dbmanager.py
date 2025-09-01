import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.config import settings
from levseq_dash.app.utils import utils

num_samples = 2  # change this if more data is added


def test_db_load_examples(dbmanager_read_all_from_file):
    assert len(dbmanager_read_all_from_file.experiments_dict) == num_samples


@pytest.mark.parametrize(
    "index",
    [0, 1],
)
def test_get_experiment(dbmanager_read_all_from_file, index):
    """
    test getting experiments by their ids
    """
    exp = dbmanager_read_all_from_file.get_experiment(index)
    assert exp.plates_count > 0
    assert not exp.data_df.empty


def test_get_experiment_out_of_bounds(dbmanager_read_all_from_file):
    """
    look up for a non-existent experiment will return none
    """
    exp = dbmanager_read_all_from_file.get_experiment(num_samples)
    assert exp is None


# TODO: need to add a test for delete
# def test_delete_experiment(dbmanager_read_all_from_file):
#     """
#     delete multiple experiments, and make sure the count has gone down accordingly
#     """
#     assert len(dbmanager_read_all_from_file.experiments_dict) == num_samples
#     assert dbmanager_read_all_from_file.delete_experiment(2)
#     assert dbmanager_read_all_from_file.delete_experiment(4)
#     assert dbmanager_read_all_from_file.delete_experiment(6)
#     assert dbmanager_read_all_from_file.delete_experiment(8)
#     assert len(dbmanager_read_all_from_file.experiments_dict) == num_samples - 4


def test_db_load_assay(dbmanager_read_all_from_file):
    assert len(dbmanager_read_all_from_file.assay_list) == 24


def test_db_get_lab_experiments_with_meta_data_general(dbmanager_read_all_from_file):
    data_list_of_dict = dbmanager_read_all_from_file.get_all_lab_experiments_with_meta_data()
    assert len(data_list_of_dict) == num_samples
    df = pd.DataFrame.from_records(data_list_of_dict)
    assert df.shape[0] == num_samples
    assert df.shape[1] == 13


@pytest.mark.parametrize(
    "index,name,n_plates, n_unique",
    [
        (0, "flatten EP", 10, 2),
        (1, "flatten ssm", 4, 1),
    ],
)
def test_db_get_all_lab_experiments_with_meta_data_data(dbmanager_read_all_from_file, index, name, n_plates, n_unique):
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_all_lab_experiments_with_meta_data()
    sorted_list = sorted(list_of_all_lab_experiments_with_meta, key=lambda x: x[gs.c_experiment_name])
    assert sorted_list[index][gs.c_experiment_name] == name
    assert sorted_list[index]["plates_count"] == n_plates
    assert len(sorted_list[index]["unique_smiles_in_data"]) == n_unique


@pytest.mark.parametrize(
    "index",
    [0, 1],
)
def test_extract_all_substrate_product_smiles_from_lab_data(dbmanager_read_all_from_file, index):
    """
    This test is similar to below but will test the substrates
    """
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_all_lab_experiments_with_meta_data()

    all_smiles = utils.extract_all_substrate_product_smiles_from_lab_data(list_of_all_lab_experiments_with_meta)
    assert len(all_smiles) != 0
    # get the substrate from the test data and make sure they are found in the unique list
    substrates = list_of_all_lab_experiments_with_meta[index][gs.cc_substrate]
    assert (all_smiles.find(c) != -1 for c in substrates)

    products = list_of_all_lab_experiments_with_meta[index][gs.cc_product]
    assert (all_smiles.find(c) != -1 for c in products)


def test_get_all_lab_sequences(dbmanager_read_all_from_file):
    list_of_sequences = dbmanager_read_all_from_file.get_all_lab_sequences()
    assert len(list_of_sequences) != 0


def test_use_web_exceptions(mock_load_config_use_web, experiment_ep_pcr):
    """
    I need to control the order of the mock before the DataManager so I am putting the code
    here instead of using the fixture
    """
    from levseq_dash.app.data_manager.manager import DataManager

    dm = DataManager()
    with pytest.raises(Exception):
        dm._add_experiment(experiment_ep_pcr)


def test_use_web_exceptions_2(mock_load_config_use_web):
    """
    I need to control the order of the mock before the DataManager so I am putting the code
    here instead of using the ficture
    """
    from levseq_dash.app.data_manager.manager import DataManager

    dm = DataManager()
    with pytest.raises(Exception):
        dm._load_test_experiment_data()


def test_load_config():
    """
    Config file that is distributed must have the app mode set
    """
    # Use centralized settings helpers for config and mode checks
    assert settings.is_disk_mode() or settings.is_db_mode()


def test_load_config_invalid(mock_load_config_invalid):
    from levseq_dash.app.data_manager.manager import DataManager

    with pytest.raises(Exception):
        DataManager()


def test_load_config_app_mode_error(mock_load_config_storage_mode_error):
    from levseq_dash.app.data_manager.manager import DataManager

    with pytest.raises(Exception):
        DataManager()


def test_load_config_env(mock_load_using_existing_env_data_path):
    """
    This mock will follow through all the way to _load_test_experiment_data
    but will throw an exception because it can't find the experiment files in
    _load_test_experiment_data
    """
    from levseq_dash.app.data_manager.manager import DataManager

    with pytest.raises(Exception):
        DataManager()


def test_get_assays(dbmanager_read_all_from_file):
    assert len(dbmanager_read_all_from_file.get_assays()) == 24
