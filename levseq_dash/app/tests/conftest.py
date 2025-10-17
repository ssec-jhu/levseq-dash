from pathlib import Path

import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.data_manager.experiment import Experiment, MutagenesisMethod

load_config_mock_string = "levseq_dash.app.config.settings.load_config"


@pytest.fixture(scope="session")
def package_root():
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="session")
def test_data_path(package_root):
    return package_root / "app" / "tests" / "test_data"


@pytest.fixture(scope="session")
def app_data_path(package_root):
    return package_root / "app" / "data"


@pytest.fixture(scope="session")
def path_exp_ep_data(test_data_path):
    return [
        test_data_path / "flatten_ep_processed_xy_cas" / "flatten_ep_processed_xy_cas.csv",
        test_data_path / "flatten_ep_processed_xy_cas" / "flatten_ep_processed_xy_cas.cif",
        test_data_path / "flatten_ep_processed_xy_cas" / "flatten_ep_processed_xy_cas.json",
    ]


@pytest.fixture(scope="session")
def experiment_ep_pcr_metadata(path_exp_ep_data):
    """Load experiment metadata from JSON file"""
    import json

    with open(path_exp_ep_data[2], "r") as f:
        metadata_dict = json.load(f)
    return metadata_dict


@pytest.fixture(scope="session")
def path_exp_ssm_data(test_data_path):
    return [
        test_data_path / "flatten_ssm_processed_xy_cas" / "flatten_ssm_processed_xy_cas.csv",
        test_data_path / "flatten_ssm_processed_xy_cas" / "flatten_ssm_processed_xy_cas.cif",
        test_data_path / "flatten_ssm_processed_xy_cas" / "flatten_ssm_processed_xy_cas.json",
    ]


@pytest.fixture(scope="session")
def experiment_ssm_metadata(path_exp_ep_data):
    """Load experiment metadata from JSON file"""
    import json

    with open(path_exp_ep_data[2], "r") as f:
        metadata_dict = json.load(f)
    return metadata_dict


@pytest.fixture
def mock_load_config_from_test_data_path(mocker, test_data_path):
    """
    Fixture to mock a response for load config from disk
    """
    # data_path = test_data_path / "data"
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": test_data_path},
    }
    return mock


@pytest.fixture
def mock_load_config_from_app_data_path(mocker):
    """
    Fixture to mock a response for load config from disk
    """
    # data_path = test_data_path / "data"
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": "data"},
        # "logging":{"data-manager": "true"}
    }
    return mock


@pytest.fixture(scope="function")
def disk_manager_from_app_data(mock_load_config_from_app_data_path):
    from levseq_dash.app.data_manager.disk_manager import DiskDataManager

    return DiskDataManager()


@pytest.fixture(scope="function")
def disk_manager_from_temp_data(mocker, tmp_path):
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"five-letter-id-prefix": "MYLAB", "enable-data-modification": True, "local-data-path": str(tmp_path)},
    }

    from levseq_dash.app.data_manager.disk_manager import DiskDataManager

    return DiskDataManager()


@pytest.fixture
def mock_load_config(mocker):
    """Fixture for mocking load_config"""
    mock = mocker.patch("levseq_dash.app.config.settings.load_config")
    return mock


@pytest.fixture
def mock_get_disk_settings(mocker):
    mock = mocker.patch("levseq_dash.app.config.settings.get_disk_settings")
    return mock


@pytest.fixture
def mock_get_logging_settings(mocker):
    """Fixture for mocking get_logging_settings"""
    mock = mocker.patch("levseq_dash.app.config.settings.get_logging_settings")
    return mock


@pytest.fixture
def mock_get_deployment_mode(mocker):
    mock = mocker.patch("levseq_dash.app.config.settings.get_deployment_mode")
    return mock


@pytest.fixture
def mock_is_data_modification_enabled(mocker):
    mock = mocker.patch("levseq_dash.app.config.settings.is_data_modification_enabled")
    return mock


@pytest.fixture
def mock_is_local_instance_mode(mocker):
    mock = mocker.patch("levseq_dash.app.config.settings.is_local_instance_mode")
    return mock


@pytest.fixture
def mock_load_config_invalid(mocker):
    """
    Fixture to mock a config file in disk mode with an invalid path
    """
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": "non/existent/path"},
    }
    return mock


@pytest.fixture
def mock_load_config_storage_mode_error(mocker):
    """
    Fixture to mock a config file in an invalid data-mode
    """
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "invalid_string",
        # path is not important here
        "disk": {"local-data-path": "non/existent/path"},
    }
    return mock


@pytest.fixture
def mock_load_using_existing_env_data_path(mock_load_config_from_test_data_path, monkeypatch, tmp_path):
    """
    Fixture to mock a DATA_PATH env with a temp_path
    """
    # using monkeypatch for env variables
    # Note: tmp_path fixture already exists
    monkeypatch.setenv("DATA_PATH", str(tmp_path))


@pytest.fixture
def disk_manager_from_test_data(mock_load_config_from_test_data_path):
    from levseq_dash.app.data_manager.disk_manager import DiskDataManager

    return DiskDataManager()


@pytest.fixture(scope="session")
def experiment_ep_pcr(path_exp_ep_data):
    """Create experiment using new ExperimentMetadata pattern"""
    experiment_ep_example = Experiment(
        experiment_data_file_path=path_exp_ep_data[0],
        geometry_file_path=path_exp_ep_data[1],
    )
    return experiment_ep_example


@pytest.fixture(scope="session")
def experiment_ssm(path_exp_ssm_data):
    experiment_ssm_example = Experiment(
        experiment_data_file_path=path_exp_ssm_data[0],
        geometry_file_path=path_exp_ssm_data[1],
    )
    return experiment_ssm_example


@pytest.fixture(scope="session")
def selected_row_top_variant_table():
    """
    this is an example selected row from the current setup of the top variants table
    """
    return [
        {
            gs.c_smiles: "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
            gs.c_plate: "20240422-ParLQ-ep1-300-1",
            gs.c_well: "G10",
            gs.c_substitutions: "K99R_R118C",
            gs.c_fitness_value: 2506309.878,
            "min": 80628.5812,
            "max": 3176372.303,
            "mean": 1823393.4415588235,
            gs.cc_ratio: 1.3745304885254768,
            "min_group": 0.044218970718173926,
            "max_group": 1.7420114773937716,
        }
    ]


@pytest.fixture(scope="session")
def selected_row_top_variant_table_aa_errors():
    """
    this is an example selected row from the current setup of the top variants table
    """
    return [{gs.c_substitutions: "K99R R118C"}]


@pytest.fixture(scope="session")
def list_of_residues():
    hot = "[10, 20, 30]"
    cold = "[30, 40, 50]"
    mismatch = "[25, 60]"
    return hot, cold, mismatch


@pytest.fixture(scope="session")
def list_of_residues_edge():
    hot = [1, 197]
    cold = [60]
    # mismatch = "[25, 60]"
    return hot, cold


@pytest.fixture
def alignment_string():
    return """\
target            0 MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLMG
                  0 ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||.|
query             0 MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAG

target           60 GWAASNEHLIYYFSNPDTGAPIKEYLERVRARCVAWVLDTTCRDYNREWLDYQYEVGLRH
                 60 ||||||||||||.|||||||||||||||||||..||||||||||||||||||||||||||
query            60 GWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRH

target          120 HRSKKGVTDGVRTVPNTPLRYLIAEIYPLTATIKPFLAKKGGSPEDIEGMYNAWLKSVVL
                120 ||||||||||||||||||||||||.|||.|||||||||||||||||||||||||||||||
query           120 HRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVL

target          180 QVAIWSHPYTKENDRLE 197
                180 |||||||||||||||-- 197
query           180 QVAIWSHPYTKENDR-- 195
"""


@pytest.fixture(scope="session")
def seq_align_per_smiles_data():
    d = [
        {
            gs.c_smiles: "C1=CC=C(C=C1)C=O",
            gs.cc_hot_indices_per_smiles: ["59", "89", "93", "149"],
            gs.cc_cold_indices_per_smiles: ["89", "119", "120"],
            gs.cc_exp_residue_per_smiles: [
                "20",
                "43",
                "59",
                "89",
                "93",
                "107",
                "119",
                "120",
                "134",
                "149",
                "175",
                "183",
            ],
        }
    ]
    df = pd.DataFrame(d)

    meta_data = {
        gs.c_experiment_name: "flatten_ssm_processed_xy_cas.csv",
        "experiment_date": "01-01-2025",
        "upload_time_stamp": "2025-04-04 19:36:26",
        "assay": "NMR Spectroscopy",
        "mutagenesis_method": MutagenesisMethod.SSM.value,
        gs.cc_substrate: "C1=CC=C(C=C1)C=O, CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        gs.cc_product: "C1=CC=C(C=C1)C=O",
        "unique_smiles_in_data": ["C1=CC=C(C=C1)C=O"],
        "plates": ["20241201-SSM-P1", "20241201SSM-P2", "20241201SSM-P3", "20241201SSM-P4"],
        "plates_count": 4,
        "parent_sequence": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTG"
        "APIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLA"
        "KKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR",
        "geometry_file_format": ".cif",
    }
    seq_data = {
        gs.cc_experiment_id: 1,
        "sequence": "MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVR"
        "ARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVV"
        "LQVAIWSHPYTKENDR",
        "sequence_alignment": "target            0 MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAG\n"
        "                  0 ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        "query             0 MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAG\n"
        "\n"
        "target           60 GWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRH\n"
        "                 60 ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        "query            60 GWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRH\n\n"
        "target          120 HRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVL\n"
        "                120 ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        "query           120 HRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVL\n"
        "\n"
        "target          180 QVAIWSHPYTKENDR 195\n                180 ||||||||||||||| 195\n"
        "query           180 QVAIWSHPYTKENDR 195\n",
        "alignment_score": 1040.0,
        "norm_score": 1.0,
        "identities": 195,
        "mismatches": 0,
        "gaps": 0,
    }

    return df, seq_data, meta_data


@pytest.fixture(scope="session")
def seq_align_data():
    return {
        gs.cc_experiment_id: 1,
        "sequence": "MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQGSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTL"
        "CKPLDRQWLNYMYEIGLRHHRTKKGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAIWSYPYAKTGEWLE",
        "sequence_alignment": "target            0 MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQ\n"
        "                  0 ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        "query             0 MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQ\n"
        "\n"
        "target           60 GSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTLCKPLDRQWLNYMYEIGLRHHRTK\n"
        "                 60 ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        "query            60 GSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTLCKPLDRQWLNYMYEIGLRHHRTK\n\n"
        "target          120 KGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAI\n"
        "                120 ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
        "query           120 KGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAI\n\n"
        "target          180 WSYPYAKTGEWLE 193\n                180 ||||||||||||| 193\n"
        "query           180 WSYPYAKTGEWLE 193\n",
        "alignment_score": 1053.0,
        "norm_score": 1.0,
        "identities": 193,
        "mismatches": 0,
        "gaps": 0,
    }
