import re
from enum import StrEnum
from pathlib import Path

import pandas as pd

from levseq_dash.app import global_strings as gs
from levseq_dash.app.utils import u_protein_viewer, u_reaction, utils


class MutagenesisMethod(StrEnum):
    epPCR = gs.eppcr
    SSM = gs.ssm


class Experiment:
    """
    The `Experiment` class represents an experimental setup that processes and validates
    data from experiment files. It handles the loading of experiment data that WAS SAVED USING THE UPLOAD,
    geometry files, and performs various operations such as data preprocessing, validation, and analysis.

    Attributes:
        data_df (pd.DataFrame): The "only necessary columns"  from experiment data loaded from the CSV file.
        geometry_base64_bytes (bytes): The geometry file content in base64-encoded bytes.
        unique_smiles_in_data (list): A list of unique SMILES strings in the experiment data.
        plates (list): A list of unique plates in the experiment data.
    """

    def __init__(
        self,
        experiment_data_file_path,
        geometry_file_path,
    ):
        # ----------------------------
        # process the core data first
        # ----------------------------
        if not Path(experiment_data_file_path).is_file() or not Path(geometry_file_path).is_file():
            raise ValueError(
                "Experiment data file path, geometry file path must be provided in order to load an Experiment object."
            )

        # read the input data
        try:
            # read CSV file with only the required columns
            # Note: The sequence column is not read here for optimization purposes.
            # The parent sequence was extracted during the upload process.

            self.data_df = pd.read_csv(experiment_data_file_path, usecols=gs.experiment_core_data_list)
            if self.data_df.empty:
                raise ValueError("Experiment data file is empty.")

            # read the cif file as bytes
            with open(geometry_file_path, "rb") as f:
                self.geometry_base64_bytes = f.read()
                if len(self.geometry_base64_bytes) == 0:
                    raise ValueError("Geometry file is empty.")

            # internal calculations that are metadata but are not stored with the files
            self.unique_smiles_in_data = list(self.data_df[gs.c_smiles].unique())
            self.plates = self.extract_plates_list(self.data_df)

        except Exception as e:
            raise Exception(f"Error loading experiment data file: {e}")

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

            # drop some of the unused columns, we only need the columns below
            columns_to_keep = [gs.c_smiles, gs.c_plate, gs.c_well, gs.c_substitutions, gs.c_fitness_value, gs.cc_ratio]
            df = df.drop(columns=[col for col in df.columns if col not in columns_to_keep])

            # remove anything from the mutations column with # or - and drop rows where column has NaN values
            # Notes: square brackets [] mean "match either # or -"
            # na=True ensures missing values are also considered invalid
            # ~ (bitwise NOT) negates the condition
            df = df[~df[gs.c_substitutions].str.contains(r"[#-]", na=True)]
            # not loading the sequences anymore as they take up unnecessary space
            # df = df[~df[gs.c_aa_sequence].str.contains(r"[#-]", na=True)]
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
        """
        Use this function only after running sanity checks on the original DataFrame where the column exists.
        Do not use it on a DataFrame that is in memory because it may be optimized and not have the column.
        """
        return df[df[gs.c_substitutions] == gs.hashtag_parent][gs.c_aa_sequence].iloc[0]

    @staticmethod
    def run_sanity_checks_on_experiment_file(df: pd.DataFrame):
        """
        Perform a series of sanity checks on the provided experiment DataFrame to ensure data integrity.

        Args:
            df (pd.DataFrame): The original experiment data as a pandas DataFrame.

        Raises:
            Exception: If the DataFrame is empty.
            ValueError: If required columns are missing.
            ValueError: If the '#PARENT#' entry is missing in the substitutions' column.
            ValueError: If any SMILES string is invalid, null, or empty.

        Returns:
            bool: True if all sanity checks pass.
        """
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

        # # check that parent entries don't have empty fitness values
        # parent_rows = df[df[gs.c_substitutions] == gs.hashtag_parent]
        # for index, row in parent_rows.iterrows():
        #     fitness_value = row[gs.c_fitness_value]
        #     if pd.isnull(fitness_value):
        #         raise ValueError(
        #             f"Parent entry ('{gs.hashtag_parent}') at row {index} has empty fitness value. "
        #             f"Please fill the cell with 0 or an appropriate value."
        #         )

        # each row of the csv file must be checked for valid smiles string
        # I want to notify the user which row has an error, so they can fix their experiment file
        for index, row in df.iterrows():
            smiles_string = str(row[gs.c_smiles])
            if not smiles_string or pd.isnull(smiles_string) or smiles_string.strip() == "":
                raise ValueError(f"Invalid SMILES string at row {index}. Value is null, NaN, or empty.")
            valid = u_reaction.is_valid_smiles(smiles_string)
            if not valid:
                raise ValueError(f"Invalid SMILES string at row {index}. SMILES is:'{smiles_string}'")

        # check that all wells follow standard 96-well plate format (A1-H12 or A01-H12)
        # Pattern: ^[A-H](0?[1-9]|1[0-2])$
        # ^ = start, [A-H] = letters A-H, (0?[1-9]|1[0-2]) = numbers 1-12 (with optional leading zero), $ = end
        valid_well_pattern = re.compile(r"^[A-H](0?[1-9]|1[0-2])$")
        for index, row in df.iterrows():
            well = str(row[gs.c_well]).strip()

            if not well or pd.isnull(well) or well == "":
                raise ValueError(f"Well value at row {index} is null, NaN, or empty.")

            if not valid_well_pattern.match(well):
                raise ValueError(
                    f"Well '{well}' at row {index} does not follow standard 96-well plate format. "
                    f"Expected format is letter A-H followed by number 1-12."
                )

        # check for unique wells within each smiles-plate group
        for (smiles, plate), group in df.groupby([gs.c_smiles, gs.c_plate]):
            duplicate_wells = group.duplicated(subset=[gs.c_well], keep=False)
            if duplicate_wells.any():
                duplicate_rows = group[duplicate_wells]
                duplicate_wells_list = duplicate_rows[gs.c_well].unique().tolist()
                duplicate_indices = duplicate_rows.index.tolist()
                raise ValueError(
                    f"Duplicate wells in (smiles={smiles}, plate='{plate}) combo. "
                    f"Wells {duplicate_wells_list} in rows: {duplicate_indices}. "
                )

        # # Relaxing parent-smiles combo requirement
        # # check any smiles-plate column combo has a #PARENT# in its gs.c_substitution column
        # for (s, p), group in df.groupby([gs.c_smiles, gs.c_plate]):
        #     if "#PARENT#" not in group[gs.c_substitutions].values:
        #         raise ValueError(
        #             f"Experiment file has missing '#PARENT#' in combo: {gs.c_smiles}='{s}' and {gs.c_plate}='{p}'"
        #         )

        # you passed all checks
        return True
