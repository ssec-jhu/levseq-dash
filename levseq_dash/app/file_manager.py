# import base64
# import io
# import os
# from collections import defaultdict
# from pathlib import Path
#
# import pandas as pd
# from dash_molstar.utils import molstar_helper
#
# from levseq_dash.app import parser
# from levseq_dash.app.data_manager import DataManager, MutagenesisMethod
# from levseq_dash.app.experiment import Experiment
# from levseq_dash.app.tests.conftest import test_assay_list
#
#
# class FileManager(DataManager):
#     def __init__(self):
#         # super().__init__()
#         self.experiments_dict = defaultdict(Experiment)
#         self.assay_list = test_assay_list
#
#         # use this flag for debugging multiple files.
#         # This will load all csv files in test/data
#         # if CONFIG["debug"]["load_all_experiments_from_disk"]:
#         #    gather
#
#     def add_new_experiment_from_ui(
#             self,
#             user_id,
#             experiment_name,
#             experiment_time_stamp,
#             experiment_date,
#             substrate_cas_number: list[str],
#             product_cas_number: list[str],
#             assay,
#             mutagenesis_method: MutagenesisMethod,
#             experiment_content_base64_string,  # or file - the contents of the csv
#             geometry_content_base64_string,
#             parent_sequence=None,
#     ) -> int:
#         print("FileManager: add_new_experiment_from_ui")
#         data_df = parser.decode_csv_file_base64_string_to_dataframe(experiment_content_base64_string)
#         exp = Experiment(
#             data_df=data_df,
#             experiment_name=experiment_name,
#             experiment_date=experiment_date,
#             experiment_time_stamp=experiment_time_stamp,
#             substrate_cas_number=substrate_cas_number,
#             product_cas_number=product_cas_number,
#             assay=assay,
#             mutagenesis_method=mutagenesis_method,
#             geometry_file_path=None,
#             geometry_base64_string=geometry_content_base64_string
#         )
#         n = self.add_experiment(exp)
#         return n
#
#     def add_experiment(self, exp: Experiment):
#         n = len(self.experiments_dict.items())
#         self.experiments_dict[n] = exp
#         return n
#
#     def delete_experiment(self, experiment_id: int) -> bool:
#         del self.experiments_dict[experiment_id]
#
#         return True
#
#     # def get_user_id(username: str) -> int:
#     #     return super().get_user_id()
#
#     # def get_all_users(self):
#     #     return super().get_all_users()
#
#     def get_lab_experiments(self):
#         experiments = self.experiments_dict.keys()
#         return experiments
#
#     # def get_lab_experiments_with_meta_data(self):
#     #     return super().get_lab_experiments_with_meta_data()
#     #
#     # def get_lab_sequences(self):
#     #     return super().get_lab_sequences()
#     #
#     # def get_experiment_all(self, experiment_id: int):
#     #     super().get_experiment_all(experiment_id)
#     #
#     # def get_experiment_meta_data(self, experiment_id: int):
#     #     return super().get_experiment_meta_data(experiment_id)
#     #
#     # def get_experiment_dash_info(self, experiment_id: int):
#     #     return super().get_experiment_dash_info(experiment_id)
#
#     def get_experiment_parent_sequence(self, experiment_id: int) -> str:
#         return self.experiments_dict[experiment_id].parent_sequence
#
#     # def get_experiment_geometry_file(self, experiment_id: int):
#     #     super().get_experiment_geometry_file(experiment_id)
#
#     def get_experiment_fitness_values(self, experiment_id: int):
#         return super().get_experiment_fitness_values(experiment_id)
#
#     def get_experiment_stats(self, experiment_id: int):
#         return super().get_experiment_stats(experiment_id)
#
#     def get_assays(self):
#         return self.assay_list
#
#     def get_experiment(self, experiment_id: int) -> Experiment:
#         exp = self.experiments_dict[experiment_id]
#         return exp
#
#     def get_plates(self):
#         return None
#
#     def get_cas_numbers(self):
#         return None
#
#
# def gather_all_test_experiments():
#     experiments = {}
#     folder_path = Path(__file__).parent / 'tests/data/'
#     # Check if the folder exists
#     if folder_path.exists() and folder_path.is_dir():
#         # Get all files in the directory
#         files_in_directory = [file for file in folder_path.iterdir() if file.is_file()]
#         for file_path in files_in_directory:
#             if file_path.suffix.lower() == ".csv":
#                 file_prefix = os.path.splitext(file_path)[0]
#                 # Search for a CIF file with the same prefix and additional characters
#                 cif_candidates = [file for file in files_in_directory if file.match(f"{file_prefix}*.cif")]
#                 geometry = None
#                 if cif_candidates:
#                     geometry = cif_candidates[0]
#                 else:
#                     # search for a pdb file
#                     pdb_candidates = [file for file in files_in_directory if file.match(f"{file_prefix}*.pdb")]
#                     if pdb_candidates:
#                         geometry = pdb_candidates[0]
#
#                 if geometry:
#                     experiments.update({"csv": file_path,
#                                         "geometry": geometry})
#
#     else:
#         print(f"Directory does not exist: {folder_path}")
#
#     return experiments
#
#
#
#
# # experiment_files = gather_all_test_experiments()
# # for csv_file, geometry_file in experiment_files.items():
# #     df = pd.read_csv(csv_file)
#
#
# # exp = experiment_ep_example
# # #bytes = parser.decode_base64_string_to_base64_bytes(exp.geometry_base64_string)
# # utf8_string = exp.geometry_base64_bytes.decode('utf-8')
# # file_as_string = io.StringIO(utf8_string)
# # file = exp.geometry_file
# # pdb_cif = molstar_helper.parse_molecule(exp.geometry_base64_string, fmt="cif")
# # print("done")
