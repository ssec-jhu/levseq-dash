from collections import defaultdict

from levseq_dash.app import parser
from levseq_dash.app.data_manager import DataManager, MutagenesisMethod
from levseq_dash.app.experiment import Experiment
from levseq_dash.app.tests.conftest import test_assay_df


class FileManager(DataManager):
    def __init__(self):
        # super().__init__()
        self.experiments_dict = defaultdict(Experiment)
        self.assay_list = test_assay_df

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

    def get_plates(self):
        return None

    def get_cas_numbers(self):
        return None
