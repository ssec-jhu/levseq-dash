import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.config import settings
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


# TODO: need to add a test for delete
# def test_delete_experiment(disk_manager_from_test_data):
#     """
#     delete multiple experiments, and make sure the count has gone down accordingly
#     """
#     assert len(disk_manager_from_test_data.experiments_dict) == num_samples
#     assert disk_manager_from_test_data.delete_experiment(2)
#     assert disk_manager_from_test_data.delete_experiment(4)
#     assert disk_manager_from_test_data.delete_experiment(6)
#     assert disk_manager_from_test_data.delete_experiment(8)
#     assert len(disk_manager_from_test_data.experiments_dict) == num_samples - 4


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


# def test_load_config_invalid(mock_load_config_invalid):
#     from levseq_dash.app.data_manager.manager import DataManager
#
#     with pytest.raises(FileNotFoundError):
#         DataManager()
#
#
# def test_load_config_app_mode_error(mock_load_config_app_mode_error):
#     from levseq_dash.app.data_manager.manager import DataManager
#
#     with pytest.raises(Exception):
#         DataManager()
#
#
# def test_load_config_env(mock_load_using_existing_env_data_path):
#     """
#     This mock will follow through all the way to _load_test_experiment_data
#     but will throw an exception because it can't find the experiment files in
#     _load_test_experiment_data
#     """
#     from levseq_dash.app.data_manager.manager import DataManager
#
#     with pytest.raises(Exception):
#         DataManager()


def test_get_assays(disk_manager_from_test_data):
    assert len(disk_manager_from_test_data.get_assays()) == 3
