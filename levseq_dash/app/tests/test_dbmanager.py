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
        (0, "flatten EP", 10, 2),
        (1, "flatten ssm", 4, 1),
        (2, "mod test 1 ssm", 7, 1),
        (3, "mod test 2 ssm", 1, 1),
        (4, "mod test 3 ssm", 6, 1),
        (5, "mod test 4 v2 ep (SSM)", 6, 1),
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
def test_extract_all_substrate_product_smiles_from_lab_data(dbmanager_read_all_from_file, index):
    """
    This test is similar to below but will test the substrates
    """
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()

    all_smiles = utils.extract_all_substrate_product_smiles_from_lab_data(list_of_all_lab_experiments_with_meta)
    assert len(all_smiles) != 0
    # get the substrate from the test data and make sure they are found in the unique list
    substrates = list_of_all_lab_experiments_with_meta[index][gs.cc_substrate]
    assert (all_smiles.find(c) != -1 for c in substrates)

    products = list_of_all_lab_experiments_with_meta[index][gs.cc_product]
    assert (all_smiles.find(c) != -1 for c in products)


def test_get_lab_sequences(dbmanager_read_all_from_file):
    list_of_sequences = dbmanager_read_all_from_file.get_lab_sequences()
    assert len(list_of_sequences) != 0


def test_use_web_exceptions(mock_load_config_use_web, experiment_ep_pcr):
    """
    I need to control the order of the mock before the DataManager so I am putting the code
    here instead of using the fixture
    """
    from levseq_dash.app.data_manager import DataManager

    dm = DataManager()
    with pytest.raises(Exception):
        dm._add_experiment(experiment_ep_pcr)


def test_use_web_exceptions_2(mock_load_config_use_web):
    """
    I need to control the order of the mock before the DataManager so I am putting the code
    here instead of using the ficture
    """
    from levseq_dash.app.data_manager import DataManager

    dm = DataManager()
    with pytest.raises(Exception):
        dm._load_test_experiment_data()
