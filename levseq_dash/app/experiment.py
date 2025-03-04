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
