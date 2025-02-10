import base64
import os
from datetime import datetime

from levseq_dash.app import global_strings as gs


def read_structure_file(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Open the file in binary mode and read the content
    with open(file_path, "rb") as structure_file:
        file_content = structure_file.read()

    # Convert content to base64 string
    base64_string = base64.b64encode(file_content).decode("utf-8")

    # Convert content to base64 bytes
    base64_bytes = base64.b64encode(file_content)

    return base64_string, base64_bytes


class Experiment:
    def __init__(
        self,
        data_df,
        experiment_name,
        experiment_date=None,
        substrate_cas_number=None,
        product_cas_number=None,
        assay=None,
        mutagenesis_method=None,
        geometry_file_path=None,
        geometry_base64_string=None,
        geometry_base64_bytes=None,
    ):
        # defaulting to string
        if substrate_cas_number is None:
            substrate_cas_number = []
        if product_cas_number is None:
            product_cas_number = []

        self.data_df = data_df
        self.experiment_name = experiment_name

        # stamp the current time
        self.upload_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if experiment_date is None:
            experiment_date = "### EMPTY ###"
        self.experiment_time = experiment_date

        # if cas values are not provided use what's in the data
        self.cas_unique_values = list(data_df[gs.c_cas].unique())
        # keep the list as a comma delimited string
        if len(substrate_cas_number) == 0:
            self.substrate_cas_number = ", ".join(self.cas_unique_values)
        else:
            self.substrate_cas_number = ", ".join(substrate_cas_number)
        if len(product_cas_number) == 0:
            self.product_cas_number = "### EMPTY ###"  # empty string
        else:
            self.product_cas_number = ", ".join(product_cas_number)

        if assay is None:
            assay = "### EMPTY ###"

        self.assay = assay
        self.mutagenesis_method = mutagenesis_method

        # manual calculations

        self.plates = list(data_df[gs.c_plate].unique())
        self.plates_count = len(self.plates)

        # parent_sequences = data_df["amino_acid_substitutions"] == "#PARENT#"
        self.parent_sequence = data_df[data_df[gs.mutations] == "#PARENT#"]["aa_sequence"].iloc[0]

        # TODO: format needs to be fed in
        # decoded_pdb = base64.b64decode(base64_string)
        # if a path is provided, then we won't bother with the others
        if geometry_file_path and os.path.isfile(geometry_file_path):
            self.geometry_file_path = geometry_file_path
            # TODO: byres below extracted from the file cause issues with the molstar viewer, do I even need them?
            # with open(geometry_file_path, "rb") as structure_file:
            #     file_content = structure_file.read()
            #
            # self.geometry_base64_bytes = base64.b64encode(file_content)

        if geometry_base64_string:
            self.geometry_base64_string = geometry_base64_string
            self.geometry_base64_bytes = base64.b64decode(geometry_base64_string)

        if not self.geometry_file_path and not self.geometry_base64_bytes:
            self.geometry_base64_string = "### EMPTY ###"


def extract_experiment_meta_data(key, e: Experiment):
    # TODO these must be put in gs strings and changed in get_all_experiments_column_defs
    return {
        "experiment_id": key,
        "experiment_name": e.experiment_name,
        "upload_time_stamp": e.upload_time_stamp,
        "experiment_time": e.experiment_time,
        "sub_cas": e.substrate_cas_number,
        "prod_cas": e.product_cas_number,
        "assay": e.assay,
        "mutagenesis_method": e.mutagenesis_method,
        "plates_count": e.plates_count,
    }
