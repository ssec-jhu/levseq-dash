import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.utils import utils

num_samples = 12  # change this if more data is added


def test_db_load_examples(dbmanager_read_all_from_file):
    assert len(dbmanager_read_all_from_file.experiments_dict) == num_samples


def test_db_load_assay(dbmanager_read_all_from_file):
    assert len(dbmanager_read_all_from_file.assay_list) == 24


@pytest.mark.parametrize(
    "index",
    [0, 1, 2, 3, 4, 5],
)
def test_db_delete(dbmanager_read_all_from_file, index):
    assert len(dbmanager_read_all_from_file.experiments_dict) == num_samples
    assert dbmanager_read_all_from_file.delete_experiment(index)
    assert len(dbmanager_read_all_from_file.experiments_dict) == num_samples - 1


def test_db_get_lab_experiments_with_meta_data_general(dbmanager_read_all_from_file):
    data_list_of_dict = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()
    assert len(data_list_of_dict) == num_samples
    df = pd.DataFrame.from_records(data_list_of_dict)
    assert df.shape[0] == num_samples
    assert df.shape[1] == 13


@pytest.mark.parametrize(
    "index,name,n_plates, n_unique",
    [
        (0, "flatten_ep_processed_xy_cas.csv", 10, 2),
        (1, "flatten_ssm_processed_xy_cas.csv", 4, 1),
        (2, "mod_test_1_ssm.csv", 7, 1),
        (3, "mod_test_2_ssm.csv", 1, 1),
        (4, "mod_test_3_ssm.csv", 6, 1),
        (5, "mod_test_4_v2_ep.csv", 6, 1),
    ],
)
def test_db_get_lab_experiments_with_meta_data_data(dbmanager_read_all_from_file, index, name, n_plates, n_unique):
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()
    sorted_list = sorted(list_of_all_lab_experiments_with_meta, key=lambda x: x["experiment_name"])
    assert sorted_list[index]["experiment_name"] == name
    assert sorted_list[index]["plates_count"] == n_plates
    assert len(sorted_list[index]["unique_smiles_in_data"]) == n_unique


@pytest.mark.parametrize(
    "index",
    [0, 1, 2, 3, 4, 5],
)
def test_extract_all_substrate_product_smiles_from_lab_data_1(dbmanager_read_all_from_file, index):
    """
    This test is similar to below but will test the substrates
    """
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()

    all_substrate_smiles, _ = utils.extract_all_substrate_product_smiles_from_lab_data(
        list_of_all_lab_experiments_with_meta
    )

    assert len(all_substrate_smiles) != 0
    # get the substrate from the test data and make sure they are found in the unique list
    substrates = list_of_all_lab_experiments_with_meta[index][gs.cc_substrate]
    assert (all_substrate_smiles.find(c) != -1 for c in substrates)


@pytest.mark.parametrize(
    "index",
    [0, 1, 2, 3, 4, 5],
)
def test_extract_all_substrate_product_smiles_from_lab_data_2(dbmanager_read_all_from_file, index):
    """
    This test is similar to the previous but will test the products
    """
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()

    _, all_product_smiles = utils.extract_all_substrate_product_smiles_from_lab_data(
        list_of_all_lab_experiments_with_meta
    )

    assert len(all_product_smiles) != 0
    # get the product from the test data and make sure they are found in the unique list
    products = list_of_all_lab_experiments_with_meta[index][gs.cc_substrate]
    assert (all_product_smiles.find(c) != -1 for c in products)


def test_get_lab_sequences(dbmanager_read_all_from_file):
    list_of_sequences = dbmanager_read_all_from_file.get_lab_sequences()
    assert len(list_of_sequences) != 0


def test_use_web_exceptions(mock_load_config_use_web, experiment_ep_pcr):
    """
    I need to control the order of the mock before the DataManager so I am putting the code
    here instead of using the ficture
    """
    from levseq_dash.app.data_manager import DataManager

    dm = DataManager()
    with pytest.raises(Exception):
        dm.__add_experiment__(experiment_ep_pcr)


def test_use_web_exceptions_2(mock_load_config_use_web):
    """
    I need to control the order of the mock before the DataManager so I am putting the code
    here instead of using the ficture
    """
    from levseq_dash.app.data_manager import DataManager

    dm = DataManager()
    with pytest.raises(Exception):
        dm.__load_test_experiment_data__()


def test_use_web_exceptions_3(mock_load_config_use_web):
    """
    I need to control the order of the mock before the DataManager so I am putting the code
    here instead of using the ficture
    """
    from levseq_dash.app.data_manager import DataManager

    dm = DataManager()
    with pytest.raises(Exception):
        dm.__gather_all_test_experiments__()
