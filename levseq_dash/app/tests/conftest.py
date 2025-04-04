from pathlib import Path

import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.experiment import Experiment, MutagenesisMethod

package_root = Path(__file__).resolve().parent.parent.parent

path_assay = package_root / "app" / "tests" / "data" / "assay_measure_list.csv"
path_exp_ep_data = package_root / "app" / "tests" / "data" / "flatten_ep_processed_xy_cas.csv"
path_exp_ep_cif = package_root / "app" / "tests" / "data" / "flatten_ep_processed_xy_cas_row8.cif"

path_exp_ssm_data = package_root / "app" / "tests" / "data" / "flatten_ssm_processed_xy_cas.csv"
path_exp_ssm_cif = package_root / "app" / "tests" / "data" / "flatten_ssm_processed_xy_cas_row3.cif"

test_assay_list = (pd.read_csv(path_assay, encoding="utf-8", usecols=["Technique"]))["Technique"].tolist()


@pytest.fixture
def mock_load_config_from_disk(mocker):
    """
    Fixture to mock a response
    """
    mock = mocker.patch("levseq_dash.app.settings.load_config")
    mock.return_value = {"debug": {"load_all_experiments_from_disk": True, "use_db_web_service": False}}
    return mock


@pytest.fixture
def mock_load_config_use_web(mocker):
    """
    Fixture to mock a response
    """
    mock = mocker.patch("levseq_dash.app.settings.load_config")
    mock.return_value = {"debug": {"load_all_experiments_from_disk": False, "use_db_web_service": True}}
    return mock


@pytest.fixture
def dbmanager_read_all_from_file(mock_load_config_from_disk):
    from levseq_dash.app.data_manager import DataManager

    return DataManager()


@pytest.fixture(scope="session")
def assay_list():
    return test_assay_list


@pytest.fixture(scope="session")
def experiment_empty():
    return Experiment()


@pytest.fixture(scope="session")
def experiment_ep_pcr():
    experiment_ep_example = Experiment(
        experiment_data_file_path=path_exp_ep_data,
        experiment_name="ep_file",
        experiment_date="TBD",
        mutagenesis_method=MutagenesisMethod.epPCR,
        geometry_file_path=path_exp_ep_cif,
        assay=test_assay_list[2],
    )
    return experiment_ep_example


@pytest.fixture(scope="session")
def experiment_ssm():
    experiment_ssm_example = Experiment(
        experiment_data_file_path=path_exp_ssm_data,
        experiment_name="ssm_file",
        experiment_date="TBD",
        mutagenesis_method="SSM",
        geometry_file_path=path_exp_ssm_cif,
        assay=test_assay_list[1],
    )
    return experiment_ssm_example


@pytest.fixture(scope="session")
def experiment_ep_pcr_with_user_cas():
    return Experiment(
        experiment_data_file_path=path_exp_ep_data,
        experiment_name="ep_file",
        experiment_date="TBD",
        # these are RANDOM cas numbers for test only
        substrate_cas_number=["918704-25-2", "98053-92-1"],
        product_cas_number=["597635-11-3", "605026-90-8", "650843-51-7"],
        mutagenesis_method=MutagenesisMethod.epPCR,
        geometry_file_path=path_exp_ep_cif,
        assay=test_assay_list[3],
    )


@pytest.fixture(scope="session")
def selected_row_top_variant_table():
    """
    this is an example selected row from the current setup of the top variants table
    """
    return [
        {
            "cas_number": "345905-97-7",
            "plate": "20240422-ParLQ-ep1-300-1",
            "well": "G10",
            "amino_acid_substitutions": "K99R_R118C",
            "fitness_value": 2506309.878,
            "min": 80628.5812,
            "max": 3176372.303,
            "mean": 1823393.4415588235,
            "ratio": 1.3745304885254768,
            "min_group": 0.044218970718173926,
            "max_group": 1.7420114773937716,
        }
    ]


@pytest.fixture(scope="session")
def selected_row_top_variant_table_aa_errors():
    """
    this is an example selected row from the current setup of the top variants table
    """
    return [{"amino_acid_substitutions": "K99R R118C"}]


@pytest.fixture(scope="session")
def list_of_residues():
    hot = "[10, 20, 30]"
    cold = "[30, 40, 50]"
    mismatch = "[25, 60]"
    return hot, cold, mismatch
