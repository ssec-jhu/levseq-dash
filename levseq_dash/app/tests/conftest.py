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
def path_data_experiments(test_data_path):
    return test_data_path / "data" / "experiments"


@pytest.fixture(scope="session")
def path_data_structures(test_data_path):
    return test_data_path / "data" / "structures"


@pytest.fixture(scope="session")
def path_exp_ep_data(path_data_experiments):
    return path_data_experiments / "flatten_ep_processed_xy_cas.csv"


@pytest.fixture(scope="session")
def path_exp_ep_cif(path_data_structures):
    return path_data_structures / "flatten_ep_processed_xy_cas_row8.cif"


@pytest.fixture(scope="session")
def path_exp_ssm_data(path_data_experiments):
    return path_data_experiments / "flatten_ssm_processed_xy_cas.csv"


@pytest.fixture(scope="session")
def path_exp_ssm_cif(path_data_structures):
    return path_data_structures / "flatten_ssm_processed_xy_cas_row3.cif"


@pytest.fixture(scope="session")
def path_cif_bytes_string_file_sample(test_data_path):
    return test_data_path / "data" / "cif_bytes_string_sample.txt"


@pytest.fixture
def mock_load_config_from_disk(mocker, test_data_path):
    """
    Fixture to mock a response for load config from disk
    """
    # data_path = test_data_path / "data"
    mock = mocker.patch(load_config_mock_string)
    data_path = test_data_path / "data"
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": data_path},
    }
    return mock


@pytest.fixture
def mock_load_config(mocker):
    """Fixture for mocking load_config"""
    mock = mocker.patch("levseq_dash.app.config.settings.load_config")
    return mock


@pytest.fixture
def mock_get_logging_settings(mocker):
    """Fixture for mocking get_logging_settings"""
    mock = mocker.patch("levseq_dash.app.config.settings.get_logging_settings")
    return mock


@pytest.fixture
def mock_get_deployment_mode(mocker):
    """Fixture for mocking get_logging_settings"""
    mock = mocker.patch("levseq_dash.app.config.settings.get_deployment_mode")
    return mock


@pytest.fixture
def mock_is_data_modification_enabled(mocker):
    """Fixture for mocking get_logging_settings"""
    mock = mocker.patch("levseq_dash.app.config.settings.is_data_modification_enabled")
    return mock


# @pytest.fixture
# def mock_load_config_from_disk_dedb_data(mocker, package_root):
#     """
#     Fixture to mock a response for load config from disk
#     """
#     data_path = package_root / "app" / "data" / "DEDB"
#     mock = mocker.patch(load_config_mock_string)
#     mock.return_value = {
#         "deployment-mode": "local-instance",
#         "storage-mode": "disk",
#         "disk": {"local-data-path": data_path},
#     }
#     return mock


@pytest.fixture
def mock_load_config_use_web(mocker):
    """
    Fixture to mock a response
    """
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {"deployment-mode": "local-instance", "storage-mode": "db"}
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
def mock_load_using_existing_env_data_path(mock_load_config_from_disk, monkeypatch, tmp_path):
    """
    Fixture to mock a DATA_PATH env with a temp_path
    """
    # using monkeypatch for env variables
    # Note: tmp_path fixture already exists
    monkeypatch.setenv("DATA_PATH", str(tmp_path))


@pytest.fixture
def dbmanager_read_all_from_file(mock_load_config_from_disk):
    from levseq_dash.app.data_manager.manager import DataManager

    return DataManager()


@pytest.fixture(scope="session")
def assay_list(test_data_path):
    path_assay = test_data_path / "assay" / "assay_measure_list.csv"
    test_assay_list = (pd.read_csv(path_assay, encoding="utf-8", usecols=["Technique"]))["Technique"].tolist()
    return test_assay_list


@pytest.fixture(scope="session")
def experiment_empty():
    return Experiment()


@pytest.fixture(scope="session")
def experiment_ep_pcr(assay_list, path_exp_ep_data, path_exp_ep_cif):
    experiment_ep_example = Experiment(
        experiment_data_file_path=path_exp_ep_data,
        experiment_name="ep_file",
        experiment_date="TBD",
        mutagenesis_method=MutagenesisMethod.epPCR,
        geometry_file_path=path_exp_ep_cif,
        assay=assay_list[2],
    )
    return experiment_ep_example


@pytest.fixture(scope="session")
def experiment_ssm(assay_list, path_exp_ssm_data, path_exp_ssm_cif):
    experiment_ssm_example = Experiment(
        experiment_data_file_path=path_exp_ssm_data,
        experiment_name="ssm_file",
        experiment_date="TBD",
        mutagenesis_method="SSM",
        geometry_file_path=path_exp_ssm_cif,
        assay=assay_list[1],
    )
    return experiment_ssm_example


@pytest.fixture(scope="session")
def experiment_ep_pcr_with_user_smiles(assay_list, path_exp_ep_data, path_exp_ep_cif):
    return Experiment(
        experiment_data_file_path=path_exp_ep_data,
        experiment_name="ep_file",
        experiment_date="TBD",
        # these are RANDOM for test only
        substrate="CC(C)(C)C(=O)O[NH3+].CCC#CCCOCC.O=S(=O)([O-])C(F)(F)F",
        product="C1=CC=C2C(=C1)C=CC=C2",
        mutagenesis_method=MutagenesisMethod.epPCR,
        geometry_file_path=path_exp_ep_cif,
        assay=assay_list[3],
    )


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
        "mutagenesis_method": "Site saturation mutagenesis (SSM)",
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
