from pathlib import Path

import pandas as pd

from levseq_dash.app.experiment import Experiment

package_root = Path(__file__).resolve().parent.parent.parent

path_assay = package_root / "app" / "tests" / "data" / "assay_measure_list.csv"
path_exp_ep_data = package_root / "app" / "tests" / "data" / "flatten_ep_processed_xy_cas.csv"
path_exp_ep_cif = package_root / "app" / "tests" / "data" / "flatten_ep_processed_xy_cas_row8.cif"

path_exp_ssm_data = package_root / "app" / "tests" / "data" / "flatten_ssm_processed_xy_cas.csv"
path_exp_ssm_cif = package_root / "app" / "tests" / "data" / "flatten_ssm_processed_xy_cas_row3.cif"


test_assay_list = (pd.read_csv(path_assay, encoding="utf-8", usecols=["Technique"]))["Technique"].tolist()

experiment_ep_example = Experiment(
    data_df=pd.read_csv(path_exp_ep_data),
    experiment_name="ep_file",
    experiment_date="TBD",
    mutagenesis_method="epPcR",
    geometry_file_path=path_exp_ep_cif,
    assay=test_assay_list[2],
)

experiment_ssm_example = Experiment(
    data_df=pd.read_csv(path_exp_ssm_data),
    experiment_name="ssm_file",
    experiment_date="TBD",
    mutagenesis_method="SSM",
    geometry_file_path=path_exp_ssm_cif,
    assay=test_assay_list[1],
)
