import base64
import os
from datetime import datetime

from levseq_dash.app import global_strings as gs


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
            experiment_date = "### EMPTY ###"
        self.experiment_time = experiment_date

        self.cas_unique_values = list(data_df[gs.c_cas].unique())
        if substrate_cas_number or product_cas_number is None:
            substrate_cas_number = product_cas_number = self.cas_unique_values
        self.substrate_cas_number = substrate_cas_number
        self.product_cas_number = product_cas_number

        if assay is None:
            assay = "### EMPTY ###"

        self.assay = assay
        self.mutagenesis_method = mutagenesis_method

        # manual calculations
        self.upload_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.plates = list(data_df[gs.c_plate].unique())
        self.plates_count = len(self.plates)

        # parent_sequences = data_df["amino_acid_substitutions"] == "#PARENT#"
        self.parent_sequence = data_df[data_df[gs.mutations] == "#PARENT#"]["aa_sequence"].iloc[0]

        # TODO: format needs to be fed in
        if os.path.isfile(geometry_file):
            self.geometry_file = geometry_file
        else:
            self.geometry_file = base64.b64decode(geometry_file)
