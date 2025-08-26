import base64
import os
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import pandas as pd

from levseq_dash.app import global_strings as gs
from levseq_dash.app.utils import u_protein_viewer, u_reaction, utils


class MutagenesisMethod(StrEnum):
    epPCR = gs.eppcr
    SSM = gs.ssm


class Experiment:
    def __init__(
        self,
        experiment_data_file_path=None,
        experiment_csv_data_base64_string=None,
        experiment_name=None,
        experiment_date=None,
        upload_time_stamp=None,
        substrate=None,
        product=None,
        assay=None,
        mutagenesis_method=None,
        geometry_file_path=None,
        geometry_base64_string=None,
        geometry_base64_bytes=None,
    ):
        # ----------------------------
        # process the core data first
        # ----------------------------

        # read th input data
        input_df = pd.DataFrame()
        if experiment_data_file_path and os.path.isfile(experiment_data_file_path):
            input_df = pd.read_csv(experiment_data_file_path)
        elif experiment_csv_data_base64_string:
            input_df = utils.decode_csv_file_base64_string_to_dataframe(experiment_csv_data_base64_string)

        # run all the sanity checks on this file
        # sanity checks will raise Exceptions
        # check that the df is not empty, check for missing columns, check for presence of '#PARENT#' and in combos,
        # check all the smiles strings are valid
        self.data_df = pd.DataFrame()
        if self.run_sanity_checks_on_experiment_file(input_df):
            self.data_df = input_df[gs.experiment_core_data_list].copy()

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
        self.substrate = substrate if substrate else ""
        self.product = product if product else ""

        # can be separate
        # keep the list as a comma delimited string
        # if substrate is None:
        #     self.substrate = []  # ", ".join(self.unique_smiles_in_data)
        # else:
        #     self.substrate = ", ".join(substrate)
        #
        # if product is None:
        #     self.product = []
        # else:
        #     self.product = ", ".join(product)

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
            # TODO: below should be None, check throughout code later
            self.geometry_base64_string = ""
            self.geometry_base64_bytes = bytes()

        if geometry_base64_bytes:
            self.geometry_base64_bytes = geometry_base64_bytes

        # --------------------
        # internal calculations
        # --------------------
        self.unique_smiles_in_data = list(self.data_df[gs.c_smiles].unique()) if not self.data_df.empty else []
        self.plates = self.extract_plates_list(self.data_df)
        self.plates_count = len(self.plates)

        # sanity check already checks that such a row exists
        self.parent_sequence = (
            self.data_df[self.data_df[gs.c_substitutions] == gs.hashtag_parent][gs.c_aa_sequence].iloc
        )[0]

        if self.geometry_file_path:
            self.geometry_file_format = self.geometry_file_path.suffix
        else:
            self.geometry_file_format = ""

    def exp_meta_data_to_dict(self):
        """
        This extracts a bit more than metadata. It extracts all attributes.
        This is easier to do as it is dynamic with any changes in attributes.
        """
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

    def exp_get_processed_core_data_for_valid_mutation_extractions(self):
        """
        This function cleans and preprocesses the core data for use in mostly the sequence alignments and
        ration calculations. It filters and cleans all data so the extracted values are valid experiment
        results for the sake of the sequence alignment and ratio calculations. The results are extracted per
        smiles of the experiment. Each values, norm ratio with respect to parent sequence is also appended
        to the data.
        """
        if not self.data_df.empty:
            df = utils.calculate_group_mean_ratios_per_smiles_and_plate(self.data_df)

            # truncate the columns, we only need the columns below
            df = df[
                [
                    gs.c_smiles,
                    gs.c_plate,
                    gs.c_well,
                    gs.c_substitutions,
                    gs.c_aa_sequence,
                    gs.c_fitness_value,
                    gs.cc_ratio,
                ]
            ]

            # remove anything from the mutations column with # or - and drop rows where column has NaN values
            # Notes: square brackets [] mean "match either # or -"
            # na=True ensures missing values are also considered invalid
            # ~ (bitwise NOT) negates the condition
            df = df[~df[gs.c_substitutions].str.contains(r"[#-]", na=True)]
            df = df[~df[gs.c_aa_sequence].str.contains(r"[#-]", na=True)]
            # and drop rows where column 'F' has NaN values
            df = df.dropna(subset=[gs.c_fitness_value])

            return df
        else:
            raise Exception("Experiment data is empty!")

    def exp_hot_cold_spots(self, n):
        """
        This function extracts the top/bottom N residues for the experiment.
        It filters and cleans all data so the extracted values are valid experiment results
        The results are extracted per smiles of the experiment.
        Each values, norm ratio with respect to parent sequence is also appended to the data.
        Args:
            n: top N that we want to extract
        """
        if not self.data_df.empty:
            if n > 0:
                df = self.exp_get_processed_core_data_for_valid_mutation_extractions()

                hot_n = pd.DataFrame()
                cold_n = pd.DataFrame()
                for smiles in self.unique_smiles_in_data:
                    for plate_number in self.plates:
                        # for this smiles number and this plate of the experiment sorted by fitness values...
                        df_per_smiles_plate = df[
                            (df[gs.c_smiles] == smiles) & (df[gs.c_plate] == plate_number)
                        ].sort_values(by=gs.c_fitness_value, ascending=False)

                        # ... extract top/bottom N
                        df_hot_n = df_per_smiles_plate.head(n)
                        df_cold_n = df_per_smiles_plate.tail(n)

                        # ... concatenate to previous results
                        hot_n = pd.concat([hot_n, df_hot_n])
                        cold_n = pd.concat([cold_n, df_cold_n])

                def extract_substitution_indices_per_smiles(df_in, new_column_name):
                    """
                    This is an internal python function used only below. The function extracts the substitution indices
                    of the dataframe input grouped by the smiles for te experiment
                    """
                    df_result = (
                        # group by smiles
                        df_in.groupby(gs.c_smiles)[gs.c_substitutions]
                        # and extract the unique indices form the substitutions column
                        # ...sort it as well
                        .apply(
                            lambda x: sorted(
                                x.str.extractall(u_protein_viewer.substitution_indices_pattern)[0].unique().tolist(),
                                key=int,
                            )
                        )
                        # Generate a new DataFrame or Series with the index reset.
                        # https://pandas.pydata.org/docs/reference/api/pandas.Series.reset_index.html
                        # This is useful when the index needs to be treated as a column,
                        # or when the index is meaningless and needs to be reset to the default
                        # before another operation.
                        .reset_index()
                        # results will be applied with the same column name so need to rename the final column
                        .rename(columns={gs.c_substitutions: new_column_name})
                    )
                    return df_result

                # extract indices per smiles
                hot_per_smiles = extract_substitution_indices_per_smiles(
                    df_in=hot_n, new_column_name=gs.cc_hot_indices_per_smiles
                )
                cold_per_smiles = extract_substitution_indices_per_smiles(
                    df_in=cold_n, new_column_name=gs.cc_cold_indices_per_smiles
                )

                # merge result columns, all rows are exactly the same because the original data was the same
                hot_cold_residue_per_smiles = hot_per_smiles.merge(cold_per_smiles, how="left")

                # TODO: Note:These lines may be added/deleted in the future, keep an eye on it
                sub_per_smiles = extract_substitution_indices_per_smiles(
                    df_in=df, new_column_name=gs.cc_exp_residue_per_smiles
                )
                hot_cold_residue_per_smiles = hot_cold_residue_per_smiles.merge(sub_per_smiles, how="left")

                # add a column to identify results
                hot_n[gs.cc_hot_cold_type] = gs.seg_align_hot
                cold_n[gs.cc_hot_cold_type] = gs.seg_align_cold

                # merge the hot and the cold together
                hot_cold_spots_merged_df = pd.concat([hot_n, cold_n], ignore_index=True)

                return hot_cold_spots_merged_df, hot_cold_residue_per_smiles
            else:
                raise Exception("A number greater than 0 must be provided.")
        else:
            raise Exception("Experiment data is empty!")

    @staticmethod
    def extract_plates_list(df):
        return list(df[gs.c_plate].unique()) if not df.empty else []

    @staticmethod
    def extract_parent_sequence(df):
        return df[df[gs.c_substitutions] == gs.hashtag_parent][gs.c_aa_sequence].iloc[0]

    @staticmethod
    def run_sanity_checks_on_experiment_file(df: pd.DataFrame):
        # check that the df is not empty
        if df.empty:
            raise Exception("Experiment file has no data.")

        # check for missing columns
        df_columns_set = set(df.columns)
        column_names_set = set(gs.experiment_core_data_list)
        missing_columns = list(column_names_set - df_columns_set)

        if len(missing_columns) != 0:
            raise ValueError(f"Experiment file is missing required columns: {', '.join(missing_columns)}")

        # check for presence of '#PARENT#' in 'amino_acid_substitutions' column
        if gs.hashtag_parent not in df[gs.c_substitutions].values:
            raise ValueError(
                f"Experiment file does not contain any '#PARENT#' entry in the {gs.c_substitutions} column."
            )

        # check all the smiles strings are valid in the file
        invalid_smiles_rows = df[df[gs.c_smiles].apply(u_reaction.is_valid_smiles).isnull()]

        if not invalid_smiles_rows.empty:
            invalid_indices = invalid_smiles_rows.index.tolist()
            raise ValueError(f"Experiment file has invalid SMILES found at rows: {invalid_indices}")

        # # Relaxing parent-smiles combo requirement
        # # check any smiles-plate column combo has a #PARENT# in its gs.c_substitution column
        # for (s, p), group in df.groupby([gs.c_smiles, gs.c_plate]):
        #     if "#PARENT#" not in group[gs.c_substitutions].values:
        #         raise ValueError(
        #             f"Experiment file has missing '#PARENT#' in combo: {gs.c_smiles}='{s}' and {gs.c_plate}='{p}'"
        #         )

        # you passed all checks
        return True
