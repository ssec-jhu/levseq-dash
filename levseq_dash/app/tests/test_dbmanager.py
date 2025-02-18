import pandas as pd
import pytest

from levseq_dash.app import utils
from levseq_dash.app.data_manager import DataManager


def test_db_load(mock_load_config):
    dbmanager_read_all_from_file = DataManager()
    assert dbmanager_read_all_from_file.use_db_web_service is False
    assert len(dbmanager_read_all_from_file.experiments_dict) == 6
    assert len(dbmanager_read_all_from_file.assay_list) == 24


@pytest.mark.parametrize(
    "index",
    [0, 1, 2, 3, 4, 5],
)
def test_db_delete(mock_load_config, index):
    dbmanager_read_all_from_file = DataManager()
    assert len(dbmanager_read_all_from_file.experiments_dict) == 6
    assert dbmanager_read_all_from_file.delete_experiment(index)
    assert len(dbmanager_read_all_from_file.experiments_dict) == 5


def test_db_get_lab_experiments_with_meta_data_general(dbmanager_read_all_from_file):
    data_list_of_dict = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()
    assert len(data_list_of_dict) == 6
    df = pd.DataFrame.from_records(data_list_of_dict)
    assert df.shape[0] == 6
    assert df.shape[1] == 13


@pytest.mark.parametrize(
    "index,name,n_plates, n_unique_cas",
    [
        (0, "flatten_ep_processed_xy_cas.csv", 10, 2),
        (1, "flatten_ssm_processed_xy_cas.csv", 4, 1),
        (2, "mod_test_1_ssm.csv", 7, 1),
        (3, "mod_test_2_ssm.csv", 1, 1),
        (4, "mod_test_3_ssm.csv", 6, 1),
        (5, "mod_test_4_v2_ep.csv", 6, 1),
    ],
)
def test_db_get_lab_experiments_with_meta_data_data(dbmanager_read_all_from_file, index, name, n_plates, n_unique_cas):
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()
    sorted_list = sorted(list_of_all_lab_experiments_with_meta, key=lambda x: x["experiment_name"])
    assert sorted_list[index]["experiment_name"] == name
    assert sorted_list[index]["plates_count"] == n_plates
    assert len(sorted_list[index]["unique_cas_in_data"]) == n_unique_cas


@pytest.mark.parametrize(
    "index",
    [0, 1, 2, 3, 4, 5],
)
def test_extract_all_unique_cas_from_lab_data(dbmanager_read_all_from_file, index):
    list_of_all_lab_experiments_with_meta = dbmanager_read_all_from_file.get_lab_experiments_with_meta_data()

    all_cas = utils.extract_all_unique_cas_from_lab_data(list_of_all_lab_experiments_with_meta)
    assert len(all_cas) != 0
    # get the substrate_cas from the test data and make sure they are found in the unique list
    cas_list = list_of_all_lab_experiments_with_meta[index]["substrate_cas_number"].split(",")
    assert (all_cas.find(c) != -1 for c in cas_list)


# import unittest
# from unittest.mock import patch
# from collections import defaultdict
#
#
# class TestDataManager(unittest.TestCase):
#
#     @patch("your_module.settings.load_config")  # Mock settings.load_config()
#     def test_init_with_db_web_service_enabled(self, mock_load_config):
#         """Test initialization when use_db_web_service is True"""
#         mock_load_config.return_value = {"debug": {"use_db_web_service": True, "load_all_experiments_from_disk": False}}
#
#         dm = DataManager()
#
#         # Since database connection is not implemented, we just verify it doesn't crash
#         self.assertTrue(dm.use_db_web_service)
#
#     @patch("your_module.settings.load_config")
#     def test_init_with_db_web_service_disabled(self, mock_load_config):
#         """Test initialization when use_db_web_service is False"""
#         mock_load_config.return_value = {
#             "debug": {"use_db_web_service": False, "load_all_experiments_from_disk": False}}
#
#         dm = DataManager()
#
#         self.assertFalse(dm.use_db_web_service)
#         self.assertIsInstance(dm.experiments_dict, defaultdict)
#         self.assertEqual(dm.experiments_dict.default_factory, Experiment)
#
#     @patch("your_module.settings.load_config")
#     @patch("your_module.DataManager._DataManager__load_test_experiment_data__")  # Mock private method
#     def test_load_all_experiments_from_disk(self, mock_load_test_experiment_data, mock_load_config):
#         """Test initialization when load_all_experiments_from_disk is True"""
#         mock_load_config.return_value = {"debug": {"use_db_web_service": False, "load_all_experiments_from_disk": True}}
#
#         dm = DataManager()
#
#         # Ensure the method __load_test_experiment_data__ is called
#         mock_load_test_experiment_data.assert_called_once()
#
#
# if __name__ == "__main__":
#     unittest.main()
