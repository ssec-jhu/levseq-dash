import base64
import hashlib
import inspect
import io
import os
import re
import threading
from datetime import datetime

import pandas as pd

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components.widgets import DownloadType
from levseq_dash.app.utils import u_reaction
from levseq_dash.app.utils.u_protein_viewer import substitution_indices_pattern

# def gather_residues_from_selection(selected_rows):
#     mutations = f"{selected_rows[0]['amino_acid_substitutions']}"
#     mutations_split = mutations.split("_") if "_" in mutations else [mutations]
#     residues = list()
#     for mutation in mutations_split:
#         match = re.search(r"[A-Za-z](\d+)[A-Za-z]", mutation)
#         if match:
#             number = match.group(1)  # Extract the captured number
#             residues.append(number)
#     return residues


def extract_all_indices(input_str):
    # re.findall(<pattern>, string)
    # The .findall() method iterates over a string to find a subset of characters that match a specified pattern.
    # It will return a list of every pattern match that occurs in a given string.
    result = re.findall(substitution_indices_pattern, input_str)
    return result


def is_target_index_in_string(input_str, target_index):
    # re.findall(<pattern>, string)
    # The .findall() method iterates over a string to find a subset of characters that match a specified pattern.
    # It will return a list of every pattern match that occurs in a given string.
    # numbers = re.findall(r"(?<=\D)(\d+)(?=\D)", f"_{input_str}_")
    result = extract_all_indices(input_str)
    return str(target_index) in result


# def get_file_size(file_bytes):
#     # TODO: revisit theis function, make it better or remove altogether
#     file_size = len(file_bytes)
#
#     if file_size < 1024:
#         file_size_text = f"{file_size} bytes"
#     elif file_size < 1024 ** 2:
#         file_size_text = f"{file_size / 1024:.2f} KB"
#     else:
#         file_size_text = f"{file_size / (1024 ** 2):.2f} MB"
#     return file_size_text


def decode_dash_upload_data_to_base64_encoded_string(dash_upload_string_contents):
    # The content field will contain the file data encoded in Base64,
    # which represents the binary content of the file as a text string.

    # An "octet-stream;base64" refers to a binary file encoded as Base64 data.
    # This format is commonly used for transmitting or embedding binary data,
    # such as files or images, in text-based systems like HTTP headers, JSON, or XML.
    # base64: Indicates that the data is encoded using Base64.
    # Base64 is a way of encoding binary data (or bytes) into a text string made up of characters
    # from the set [A-Za-z0-9+/=].
    # It is a textual representation of the binary data.

    # The part after "base64," is a Base64-encoded string.
    # This is a text string, but it represents binary data when decoded.
    content_type, base64_encoded_string = dash_upload_string_contents.split(",")

    return base64_encoded_string


# def decode_base64_string_to_base64_bytes(base64_encoded_string):
#     # base64.b64decode() function converts the base64 encoded string back
#     # into its original binary data which is bytes.
#     base64_encoded_bytes = base64.b64decode(base64_encoded_string)
#     return base64_encoded_bytes


# def decode_csv_file_bytes_to_dataframe(base64_encoded_bytes):
#     """
#     utility function for testing the uploaded experiment file
#     """
#     try:
#         # If the content of file_bytes is valid UTF-8 text,
#         # the .decode("utf-8") method will convert those bytes into a regular Python
#         # string (a str object). For example, bytes that represent text in
#         # English, Chinese, or other UTF-8 compatible languages.
#         # If the bytes are not valid UTF-8, Python will raise a UnicodeDecodeError.
#         utf8_string = base64_encoded_bytes.decode("utf-8")
#         # Converts the decoded string into a file-like object
#         # so that you can use file operations (like reading lines or seeking) on it.
#         file_as_string = io.StringIO(utf8_string)
#         df = pd.read_csv(file_as_string)
#     except UnicodeDecodeError:
#         df = pd.DataFrame()
#         # return "The content is not a valid UTF-8 string."
#
#     return df


def decode_csv_file_base64_string_to_dataframe(base64_encoded_string):
    """
    This code is a utility function for the UI
    to process the uploaded csv file into a dataframe
    """
    df = pd.DataFrame()
    if base64_encoded_string:
        # base64.b64decode() function converts the base64 encoded string back
        # into its original binary data which is bytes.
        # Decode base64 STRING -> to base64 BYTES
        base64_encoded_bytes = base64.b64decode(base64_encoded_string)

        try:
            # If the content of file_bytes is valid UTF-8 text,
            # the .decode("utf-8") method will convert those bytes into a regular Python
            # string (a str object). For example, bytes that represent text in
            # English, Chinese, or other UTF-8 compatible languages.
            # If the bytes are not valid UTF-8, Python will raise a UnicodeDecodeError.
            utf8_string = base64_encoded_bytes.decode("utf-8")
            # Converts the decoded string into a file-like object
            # so that you can use file operations (like reading lines or seeking) on it.
            file_as_string = io.StringIO(utf8_string)
            df = pd.read_csv(file_as_string)
        except UnicodeDecodeError:
            # df = pd.DataFrame()
            raise Exception("The content is not a valid UTF-8 string.")

    return df


def calculate_group_mean_ratios_per_smiles_and_plate(df):
    # df = df.loc[:, ["smiles", gs.c_plate, "well", "amino_acid_substitutions", "fitness_value"]]
    group_cols = [gs.c_smiles, gs.c_plate]
    value_col = gs.c_fitness_value

    # Compute min and max fitness for each group
    group_stats = df.groupby(group_cols)[value_col].agg(["min", "max"]).reset_index()

    # Compute mean ONLY for rows where parent_col == parent_value, per group
    parent_mean = (
        df[df[gs.c_substitutions] == "#PARENT#"]
        .groupby(group_cols)[value_col]
        .mean()
        .reset_index()
        .rename(columns={value_col: "mean"})
    )

    # Merge stats back into df
    df = df.merge(group_stats, on=group_cols, suffixes=("", "_group"))
    df = df.merge(parent_mean, on=group_cols, how="left")  # Keeps all rows, even if no mean exists

    # Compute fitness ratio relative to the mean
    df[gs.cc_ratio] = df[value_col] / df["mean"]
    # TODO: rounding creates an error
    # df[gs.cc_ratio] = df[gs.cc_ratio].round(2)
    group_stats_ratio = df.groupby(group_cols)[gs.cc_ratio].agg(["min", "max"]).reset_index()
    df = df.merge(group_stats_ratio, on=group_cols, suffixes=("", "_group"))

    return df


def extract_all_substrate_product_smiles_from_lab_data(list_of_all_lab_experiments_with_meta: list[{}]):
    """
    This method extracts all the unique substrate and product smiles  used in the lab data.
    The input is a list of dictionaries, data type used by AgGrid
    """
    all_product_smiles = ""
    all_substrate_smiles = ""
    if len(list_of_all_lab_experiments_with_meta) != 0:
        substrate_smiles_set = set()
        product_smiles_set = set()
        for exp in list_of_all_lab_experiments_with_meta:
            substrate_smiles_set.add(exp[gs.cc_substrate])
            product_smiles_set.add(exp[gs.cc_product])
        all_product_smiles = ";  ".join(sorted(product_smiles_set))
        all_substrate_smiles = ";  ".join(sorted(substrate_smiles_set))

    return all_substrate_smiles, all_product_smiles


# def generate_slider_marks_dict(max_value):
#     """
#     This method extracts generates tick marks text for the range slider based on the
#     max value provided by the experiment. The tick marks are to be set in a dictionary.
#     """
#     data_range = range(0, max_value, 1)
#     return {str(round(value, 1)): str(round(value, 1)) for value in data_range}


def export_data_as_csv(option, file_name):
    """
    This method is a helper function to generate download parameters for an aggrid-table
    The download operation is handled by the grid itself. Client just provides params
    """
    if option == DownloadType.FILTERED.value:
        exported_rows = "filteredAndSorted"
    else:
        exported_rows = "all"

    # timestamp the file
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # https://ag-grid.com/javascript-data-grid/csv-export/#reference-CsvExportParams-exportedRows
    return True, {"fileName": f"{file_name}_{exported_rows}_{timestamp}.csv", "exportedRows": exported_rows}


def validate_smiles_string(smiles_string):
    """
    This function is a helper function to show the substrate and product text boxes
    as valid or invalid text boxes in the UI.
    """
    # set the defaults
    valid = False
    invalid = True
    try:
        if u_reaction.is_valid_smiles(smiles_string):
            valid = True
            invalid = False
    except Exception as e:
        # if any exception is thrown, it's still invalid
        pass
    # TODO: look into reducing this into either valid or invalid
    return valid, invalid


def select_first_row_of_data(data):
    if data:
        # set the default selected row to be the first row that is rendered on the front end
        # the table sets the sorting and all on the front end side after it is rendered, so we
        # can not select the first row of the data output that gets sent from the previous
        # callback.
        return [data[0]]

    return None


def log_with_context(msg, log_flag):
    # Check if logging is enabled for the given flag
    if not log_flag:
        return  # Do not log if the flag is disabled

    pid = os.getpid()
    tid = threading.get_ident()
    tname = threading.current_thread().name

    # Get the name of the calling function
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    func_name = caller_frame.f_code.co_name if caller_frame else "<unknown>"

    print(f"[PID:{pid}][TID:{tid}][{tname}][FUNC:{func_name}] {msg}")


def calculate_file_checksum(file_bytes) -> str:
    """Calculate SHA256 checksum of a file."""

    if file_bytes is None:
        raise ValueError("file_bytes cannot be None")

    if not isinstance(file_bytes, bytes):
        raise TypeError("file_bytes must be of type bytes")

    if len(file_bytes) == 0:
        raise ValueError("file_bytes cannot be empty")

    sha256 = hashlib.sha256()
    sha256.update(file_bytes)

    return sha256.hexdigest()
