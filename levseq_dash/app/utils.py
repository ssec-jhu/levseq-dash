import base64
import io
import random
import re

import pandas as pd
from dash_molstar.utils import molstar_helper


def get_geometry_for_viewer(exp):
    if exp.geometry_file_path:
        pdb_cif = molstar_helper.parse_molecule(exp.geometry_file_path, fmt="cif")
    else:
        pdb_cif = molstar_helper.parse_molecule(exp.geometry_base64_bytes, fmt="cif")
    return pdb_cif


def gather_residues_from_selection(selected_rows):
    mutations = f"{selected_rows[0]['amino_acid_substitutions']}"
    mutations_split = mutations.split("_") if "_" in mutations else [mutations]
    residues = list()
    for mutation in mutations_split:
        match = re.search(r"[A-Za-z](\d+)[A-Za-z]", mutation)
        if match:
            number = match.group(1)  # Extract the captured number
            residues.append(number)
    return residues


def get_selection_focus(residues, analyse=True):
    """ "
    https://dash-molstar.readthedocs.io/en/latest/
    """
    target = molstar_helper.get_targets(
        chain="A",
        residue=residues,
        auth=True,
        # if it's a CIF file to select the authentic chain names and residue
        # numbers
    )
    sel = molstar_helper.get_selection(
        target,
        # select by default, it will put a green highlight on the atoms
        # default select mode (true) or hover mode (false)
        # select=False,
        add=False,
    )  # TODO: do we want to add to the list?

    # Focus the camera on the specified targets.
    # If analyse is set to True, non-covalent interactions within 5 angstroms will be analysed.
    # https://dash-molstar.readthedocs.io/en/latest/callbacks.html#parameter-focus
    foc = molstar_helper.get_focus(target, analyse=analyse)

    return sel, foc


def reset_selection():
    target = {"chain_name": None, "auth": False, "residue_numbers": []}
    sel = molstar_helper.get_selection(
        target,
        # select by default, it will put a green highlight on the atoms
        # default select mode (true) or hover mode (false)
        select=True,
        add=False,
    )
    return sel


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


def calculate_group_mean_ratios_per_cas_and_plate(df):
    # df = df.loc[:, ["cas_number", "plate", "well", "amino_acid_substitutions", "fitness_value"]]
    group_cols = ["cas_number", "plate"]
    value_col = "fitness_value"

    # Compute min and max fitness for each group
    group_stats = df.groupby(group_cols)[value_col].agg(["min", "max"]).reset_index()

    # Compute mean ONLY for rows where parent_col == parent_value, per group
    parent_mean = (
        df[df["amino_acid_substitutions"] == "#PARENT#"]
        .groupby(group_cols)[value_col]
        .mean()
        .reset_index()
        .rename(columns={value_col: "mean"})
    )

    # Merge stats back into df
    df = df.merge(group_stats, on=group_cols, suffixes=("", "_group"))
    df = df.merge(parent_mean, on=group_cols, how="left")  # Keeps all rows, even if no mean exists

    # Compute fitness ratio relative to the mean
    df["ratio"] = df[value_col] / df["mean"]
    # TODO: rounding creates an error
    # df["ratio"] = df["ratio"].round(2)
    group_stats_ratio = df.groupby(group_cols)["ratio"].agg(["min", "max"]).reset_index()
    df = df.merge(group_stats_ratio, on=group_cols, suffixes=("", "_group"))

    return df


def generate_random_cas_numbers():
    """
    This method is only to be used for debugging and reading from disk and prototyping.
    """
    num_cas = random.randint(1, 3)  # Randomly choose between 1 and 3 CAS numbers
    cas_list = []

    for _ in range(num_cas):
        part1 = random.randint(10000, 999999)  # 5-6 digits
        part2 = random.randint(10, 99)  # 2 digits
        part3 = random.randint(0, 9)  # 1-digit check number
        cas_number = f"{part1}-{part2}-{part3}"
        cas_list.append(cas_number)

    return cas_list


def extract_all_unique_cas_from_lab_data(list_of_all_lab_experiments_with_meta: list[{}]):
    """
    This method extracts all the unique substrate cas  used in the lab data.
    The data is already pulled from the disk/db along with other metadata
    The input is a list of dictionaries, data type used by AgGrid
    """
    # TODO: which unique cas do we want to show here? unique files? substrate only?
    all_unique_cas = ""
    if len(list_of_all_lab_experiments_with_meta) != 0:
        unique_cas_set = set()
        for exp in list_of_all_lab_experiments_with_meta:
            cas_list = exp["substrate_cas_number"].split(",")
            unique_cas_set.update(cas_list)
        all_unique_cas = ";".join(sorted(unique_cas_set))

    return all_unique_cas
