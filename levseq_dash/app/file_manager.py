import base64
import os
from collections import defaultdict
from datetime import datetime

import pandas as pd

from levseq_dash.app import parser
from levseq_dash.app.data_manager import DataManager, MutagenesisMethod


class Experiment:
    def __init__(
        self,
        data_df,
        experiment_name=None,
        experiment_date=None,
        experiment_time_stamp=None,
        substrate_cas_number=None,
        product_cas_number=None,
        assay=None,
        mutagenesis_method=None,
        geometry_file=None,
    ):
        self.data_df = data_df
        self.experiment_name = experiment_name
        self.experiment_time_stamp = experiment_time_stamp

        if experiment_date is None:
            experiment_date = "TBD"
        self.experiment_time = experiment_date

        self.cas_unique_values = data_df["cas_number"].unique()
        if substrate_cas_number or product_cas_number is None:
            substrate_cas_number = product_cas_number = self.cas_unique_values
        self.substrate_cas_number = substrate_cas_number
        self.product_cas_number = product_cas_number

        self.assay = assay
        self.mutagenesis_method = mutagenesis_method

        # manual calculations
        self.upload_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        plates = data_df["plate"].unique()
        self.plates_count = len(plates)

        # parent_sequences = data_df["amino_acid_substitutions"] == "#PARENT#"
        self.parent_sequence = data_df[data_df["amino_acid_substitutions"] == "#PARENT#"]["aa_sequence"].iloc[0]

        # TODO: format needs to be fed in
        if os.path.isfile(geometry_file):
            self.geometry_file = geometry_file
        else:
            self.geometry_file = base64.b64decode(geometry_file)


experiment_1 = Experiment(
    data_df=pd.read_csv("./tests/data/flatten_ep_processed_xy_cas.csv"),
    experiment_name="ep_file",
    experiment_date="TBD",
    mutagenesis_method="epPcR",
    geometry_file="./tests/data/flatten_ep_processed_xy_cas_row8.cif",
)

experiment_2 = Experiment(
    data_df=pd.read_csv("./tests/data/flatten_ssm_processed_xy_cas.csv"),
    experiment_name="ssm_file",
    experiment_date="TBD",
    mutagenesis_method="SSM",
    geometry_file="./tests/data/flatten_ssm_processed_xy_cas_row3.cif",
)


class FileManager(DataManager):
    def __init__(self):
        # load csv files
        # super().__init__()
        self.experiments_dict = defaultdict(Experiment)
        assay_df = pd.read_csv("./tests/data/assay_measure_list.csv", encoding="utf-8", usecols=["Technique"])
        self.assay_list = assay_df["Technique"].tolist()

    def add_new_experiment(
        self,
        user_id,
        experiment_name,
        experiment_time_stamp,
        experiment_date,
        substrate_cas_number: list[str],
        product_cas_number: list[str],
        assay,
        mutagenesis_method: MutagenesisMethod,
        experiment_content,  # or file - the contents of the csv
        geometry_content,
        parent_sequence=None,
    ) -> int:
        print("FileManager: add_new_experiment")
        n = len(self.experiments_dict.items())
        data_df = parser.convert_experiment_upload_to_dataframe(experiment_content)
        exp = Experiment(
            data_df=data_df,
            experiment_name=experiment_name,
            experiment_date=experiment_date,
            experiment_time_stamp=experiment_time_stamp,
            substrate_cas_number=substrate_cas_number,
            product_cas_number=product_cas_number,
            assay=assay,
            mutagenesis_method=mutagenesis_method,
            geometry_file=geometry_content,
        )

        self.experiments_dict[n] = exp
        return n

    def delete_experiment(self, experiment_id: int) -> bool:
        del self.experiments_dict[experiment_id]

        return True

    # def get_user_id(username: str) -> int:
    #     return super().get_user_id()

    # def get_all_users(self):
    #     return super().get_all_users()

    def get_lab_experiments(self):
        experiments = self.experiments_dict.keys()
        return experiments

    # def get_lab_experiments_with_meta_data(self):
    #     return super().get_lab_experiments_with_meta_data()
    #
    # def get_lab_sequences(self):
    #     return super().get_lab_sequences()
    #
    # def get_experiment_all(self, experiment_id: int):
    #     super().get_experiment_all(experiment_id)
    #
    # def get_experiment_meta_data(self, experiment_id: int):
    #     return super().get_experiment_meta_data(experiment_id)
    #
    # def get_experiment_dash_info(self, experiment_id: int):
    #     return super().get_experiment_dash_info(experiment_id)

    def get_experiment_parent_sequence(self, experiment_id: int) -> str:
        return self.experiments_dict[experiment_id].parent_sequence

    # def get_experiment_geometry_file(self, experiment_id: int):
    #     super().get_experiment_geometry_file(experiment_id)

    def get_experiment_fitness_values(self, experiment_id: int):
        return super().get_experiment_fitness_values(experiment_id)

    def get_experiment_stats(self, experiment_id: int):
        return super().get_experiment_stats(experiment_id)

    def get_assays(self):
        return self.assay_list

    def get_experiment(self, experiment_id: int) -> Experiment:
        exp = self.experiments_dict[experiment_id]
        return exp
