import base64
import os
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import pandas as pd

from levseq_dash.app import global_strings as gs
from levseq_dash.app import utils


class MutagenesisMethod(StrEnum):
    epPCR = gs.eppcr
    SSM = gs.ssm


class Experiment:
    # data_df = pd.DataFrame()
    # experiment_name = ""
    # upload_time_stamp = ""
    # experiment_date = ""
    # substrate_cas_number = []
    # product_cas_number = []
    # assay = ""
    # mutagenesis_method = ""
    #
    # geometry_file_path = Path()
    # geometry_base64_string = ""
    # geometry_base64_bytes = bytes()
    #
    # unique_cas_in_data = []
    # plates = []
    # plates_count = 0
    # parent_sequence = ""

    def __init__(
        self,
        experiment_data_file_path=None,
        experiment_csv_data_base64_string=None,
        experiment_name=None,
        experiment_date=None,
        upload_time_stamp=None,
        substrate_cas_number=None,
        product_cas_number=None,
        assay=None,
        mutagenesis_method=None,
        geometry_file_path=None,
        geometry_base64_string=None,
        geometry_base64_bytes=None,
    ):
        # ----------------------------
        # process the core data first
        # ----------------------------
        self.data_df = pd.DataFrame()
        if experiment_data_file_path and os.path.isfile(experiment_data_file_path):
            self.data_df = pd.read_csv(experiment_data_file_path, usecols=gs.experiment_core_data_list)
        elif experiment_csv_data_base64_string:
            self.data_df = utils.decode_csv_file_base64_string_to_dataframe(experiment_csv_data_base64_string)

        # TODO: do we want to rais an exception if empty?
        # if self.data_df.empty:
        #    raise Exception("Experiment Core Data is empty!")

        # ------------------
        # process meta data
        # ------------------
        self.experiment_name = experiment_name if experiment_name else ""
        self.experiment_date = experiment_date if experiment_date else ""
        self.upload_time_stamp = (
            upload_time_stamp if upload_time_stamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.assay = assay if assay else ""
        self.mutagenesis_method = mutagenesis_method if mutagenesis_method else ""

        # TODO: substrate and product cas should be whatever the user provided. don't fill it with unique, that
        # can be separate
        # keep the list as a comma delimited string
        if substrate_cas_number is None:
            self.substrate_cas_number = []  # ", ".join(self.unique_cas_in_data)
        else:
            self.substrate_cas_number = ", ".join(substrate_cas_number)

        if product_cas_number is None:
            self.product_cas_number = []
        else:
            self.product_cas_number = ", ".join(product_cas_number)

        # ------------------
        # process geometry data
        # ------------------
        # if a path is provided, then we won't bother with the others
        if geometry_file_path and os.path.isfile(geometry_file_path):
            self.geometry_file_path = geometry_file_path
        else:
            self.geometry_file_path = None  # Path()

        if geometry_base64_string:
            self.geometry_base64_string = geometry_base64_string
            self.geometry_base64_bytes = base64.b64decode(geometry_base64_string)
        else:
            self.geometry_base64_string = ""
            self.geometry_base64_bytes = bytes()

        if geometry_base64_bytes:
            self.geometry_base64_bytes = geometry_base64_bytes

        # --------------------
        # internal calculations
        # --------------------
        self.unique_cas_in_data = list(self.data_df[gs.c_cas].unique()) if not self.data_df.empty else []
        self.plates = list(self.data_df[gs.c_plate].unique()) if not self.data_df.empty else []
        self.plates_count = len(self.plates)
        self.parent_sequence = (
            self.data_df[self.data_df[gs.c_substitutions] == "#PARENT#"][gs.c_aa_sequence].iloc[0]
            if not self.data_df.empty
            else ""
        )
        if self.geometry_file_path:
            self.geometry_file_format = self.geometry_file_path.suffix
        else:
            self.geometry_file_format = ""

    def exp_to_dict(self):
        result = {}
        for attr, value in self.__dict__.items():
            if isinstance(value, pd.DataFrame):
                result[attr] = value.to_dict()  # Convert DataFrame to a dictionary
            elif isinstance(value, Path):
                result[attr] = str(value)  # Convert Path to string
            else:
                result[attr] = value  # Keep other types as is
        return result

    def exp_core_data_to_dict(self):
        return self.data_df.to_dict("records")

    def exp_meta_data_to_dict(self):
        # this extracts a bit more than metadata. it extracts all attributes.
        # this is easier to do as it is dynamic with any changes in attributes
        result = {}
        for attr, value in self.__dict__.items():
            if (
                isinstance(value, pd.DataFrame)
                or isinstance(value, Path)
                or isinstance(value, bytes)
                or attr == "geometry_base64_string"
                or attr == "experiment_csv_data_base64_string"
            ):
                pass
            else:
                result[attr] = value  # Keep other types as is
        return result

    def exp_hot_cold_spots(self, n):
        """
        This function extracts the top/bottom N residues for the experiment.
        It filters and cleans all data so the extracted values are valid experiment results
        The results are extracted per CAS of the experiment.
        Each values, norm ratio with respect to parent sequence is also appended to the data.
        Args:
            n: top N that we want to extract
        """
        if n > 0:
            # calculate the experiments group mean and ratio values
            # ratio is determined within a cas+plate combo
            df = utils.calculate_group_mean_ratios_per_cas_and_plate(self.data_df)

            # truncate the columns, we only need the columns below
            df = df[
                [gs.c_cas, gs.c_plate, gs.c_well, gs.c_substitutions, gs.c_aa_sequence, gs.c_fitness_value, gs.cc_ratio]
            ]

            # remove anything from the mutations column with # or - and drop rows where column 'F' has NaN values
            # Notes: square brackets [] mean "match either # or -"
            # na=True ensures missing values are also considered invalid
            # ~ (bitwise NOT) negates the condition
            df = df[~df[gs.c_substitutions].str.contains(r"[#-]", na=True)]
            df = df[~df[gs.c_aa_sequence].str.contains(r"[#-]", na=True)]
            # and drop rows where column 'F' has NaN values
            df = df.dropna(subset=[gs.c_fitness_value])

            hot_n = pd.DataFrame()
            cold_n = pd.DataFrame()
            for cas_number in self.unique_cas_in_data:
                for plate_number in self.plates:
                    # for this cas number and this plate of the experiment sorted by fitness values...
                    df_per_cas_plate = df[(df[gs.c_cas] == cas_number) & (df[gs.c_plate] == plate_number)].sort_values(
                        by=gs.c_fitness_value, ascending=False
                    )

                    # ... extract top/bottom N
                    df_hot_n = df_per_cas_plate.head(n)
                    df_cold_n = df_per_cas_plate.tail(n)

                    # ... concatenate to previous results
                    hot_n = pd.concat([hot_n, df_hot_n])
                    cold_n = pd.concat([cold_n, df_cold_n])

            def extract_substitution_indices_per_cas(df, new_column_name):
                """
                This is an internal python function used only below. The function extracts the substitution indices
                of the dataframe input grouped by the CAS numbers for te experiment
                """
                df_result = (
                    # group by cas
                    df.groupby(gs.c_cas)[gs.c_substitutions]
                    # and extract the unique indices form the substitutions column
                    # ...sort it as well
                    .apply(lambda x: sorted(x.str.extractall(r"(\d+)")[0].unique().tolist(), key=int))
                    # Generate a new DataFrame or Series with the index reset.
                    # https://pandas.pydata.org/docs/reference/api/pandas.Series.reset_index.html
                    # This is useful when the index needs to be treated as a column,
                    # or when the index is meaningless and needs to be reset to the default before another operation.
                    .reset_index()
                    # results will be applied with the same column name so need to rename the final column
                    .rename(columns={gs.c_substitutions: new_column_name})
                )
                return df_result

            # extract indices per CAS
            hot_per_cas = extract_substitution_indices_per_cas(df=hot_n, new_column_name=gs.cc_hot_indices_per_cas)
            cold_per_cas = extract_substitution_indices_per_cas(df=cold_n, new_column_name=gs.cc_cold_indices_per_cas)

            # merge result columns, all rows are exactly the same because the original data was the same
            hot_cold_residue_per_cas = hot_per_cas.merge(cold_per_cas, how="left")

            # TODO: Note:These lines may be added/deleted in the future, keep an eye on it
            sub_per_cas = extract_substitution_indices_per_cas(df=df, new_column_name=gs.cc_exp_residue_per_cas)
            hot_cold_residue_per_cas = hot_cold_residue_per_cas.merge(sub_per_cas, how="left")

            # add a column to identify results
            hot_n[gs.cc_hot_cold_type] = "Hot"
            cold_n[gs.cc_hot_cold_type] = "Cold"

            # merge the hot and the cold together
            hot_cold_spots_merged_df = pd.concat([hot_n, cold_n], ignore_index=True)

            return hot_cold_spots_merged_df, hot_cold_residue_per_cas
        else:
            raise Exception("A number greater than 0 must be provided.")


# # def read_structure_file(file_path):
#     # Check if the file exists
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"The file {file_path} does not exist.")
#
#     # Open the file in binary mode and read the content
#     with open(file_path, "rb") as structure_file:
#         file_content = structure_file.read()
#
#     # Convert content to base64 string
#     base64_string = base64.b64encode(file_content).decode("utf-8")
#
#     # Convert content to base64 bytes
#     base64_bytes = base64.b64encode(file_content)
#
#     return base64_string, base64_bytes
