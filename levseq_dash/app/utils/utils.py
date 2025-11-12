import base64
import inspect
import io
import os
import re
import threading
from datetime import datetime

import numpy as np
import pandas as pd

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components.widgets import DownloadType
from levseq_dash.app.utils import u_reaction
from levseq_dash.app.utils.u_protein_viewer import substitution_indices_pattern


def extract_all_indices(input_str):
    """Extracts all numeric residue indices from a substitution string.

    Uses regex pattern matching to find all digit sequences that represent
    residue positions in mutation strings (e.g., "A123B" -> ["123"]).

    Args:
        input_str: String containing amino acid substitutions with residue indices

    Returns:
        List of residue indices as strings
    """
    # re.findall(<pattern>, string)
    # The .findall() method iterates over a string to find a subset of characters that match a specified pattern.
    # It will return a list of every pattern match that occurs in a given string.
    result = re.findall(substitution_indices_pattern, input_str)
    return result


def is_target_index_in_string(input_str, target_index):
    """Checks if a specific residue index is present in a substitution string.

    Args:
        input_str: String containing amino acid substitutions with residue indices
        target_index: Residue index to search for (int or str)

    Returns:
        bool: True if the target index is found in the string, False otherwise
    """
    # re.findall(<pattern>, string)
    # The .findall() method iterates over a string to find a subset of characters that match a specified pattern.
    # It will return a list of every pattern match that occurs in a given string.
    # numbers = re.findall(r"(?<=\D)(\d+)(?=\D)", f"_{input_str}_")
    result = extract_all_indices(input_str)
    return str(target_index) in result


def decode_dash_upload_data_to_base64_encoded_string(dash_upload_string_contents):
    """Extracts base64-encoded data from Dash file upload content string.

    Dash file uploads provide data in the format "data:type;base64,<encoded_data>".
    This function splits the string and returns just the base64-encoded portion.

    Args:
        dash_upload_string_contents: Dash upload content string in format
                                     "data:application/octet-stream;base64,<data>"

    Returns:
        Base64-encoded string (the portion after the comma)
    """
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


def decode_csv_file_base64_string_to_dataframe(base64_encoded_string):
    """Decodes a base64-encoded CSV file string into a pandas DataFrame.

    Used to process uploaded CSV files from the Dash UI. Converts base64 string
    to bytes, then to UTF-8 string, and finally parses as CSV.

    Args:
        base64_encoded_string: Base64-encoded representation of CSV file contents

    Returns:
        Tuple of (DataFrame, bytes):
            - DataFrame: Parsed CSV data
            - bytes: Original base64-decoded bytes for checksum calculation

    Raises:
        Exception: If content is not valid UTF-8
    """
    df = pd.DataFrame()
    base64_encoded_bytes = bytes()
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

    return df, base64_encoded_bytes


def calculate_group_mean_ratios_per_smiles_and_plate(df):
    """Calculates fitness ratios relative to parent mean for each SMILES/plate group.

    Optimized version using vectorized pandas operations. Computes mean parent fitness
    per SMILES/plate combination, then calculates ratio of each variant's fitness to
    its group mean. Handles special cases like "trac" (trace) values and zero fitness.

    Args:
        df: DataFrame containing experiment data with columns: smiles, plate,
            fitness_value, substitutions

    Returns:
        DataFrame with added columns: ratio, mean, min_group_ratio, max_group_ratio

    Note:
        - Returns early if ratio column already exists and has values
        - "trac" strings in fitness values are converted to 0.001
        - Groups with zero or NaN parent mean will have NaN ratios
        - Ratios are rounded to 3 decimal places
    """
    group_cols = [gs.c_smiles, gs.c_plate]
    value_col = gs.c_fitness_value

    # Check if ratio column already exists and has values - if so, skip calculation
    if gs.cc_ratio in df.columns and not df[gs.cc_ratio].isna().all():
        return df

    # --------------------------------
    # Clean up the fitness value column - OPTIMIZED
    # --------------------------------
    # Convert to numeric - this is the main operation
    numeric_vals = pd.to_numeric(df[value_col], errors="coerce")

    # Only check for "trac" in rows that failed numeric conversion (became NaN)
    # This avoids string operations on already-numeric data
    nan_mask = numeric_vals.isna()
    if nan_mask.any():
        # Only convert to string and check the NaN values
        trac_mask = df.loc[nan_mask, value_col].astype(str).str.contains("trac", case=False, na=False, regex=False)
        # Set trac values to 0.001, others to 0
        numeric_vals.loc[nan_mask] = 0.0
        numeric_vals.loc[nan_mask[nan_mask].index[trac_mask]] = 0.001
    else:
        # No NaN values, just fill with 0
        numeric_vals = numeric_vals.fillna(0)

    df[value_col] = numeric_vals

    # Compute mean ONLY for rows where parent_col == parent_value, per group and that the parent is not 0
    # if a prent has 0 fitness value that group combo is ignored
    parent_mean = (
        df[(df[gs.c_substitutions] == "#PARENT#") & (df[value_col] > 0)]
        .groupby(group_cols, sort=False)[value_col]  # sort=False saves time
        .mean()
        .reset_index()
        .rename(columns={value_col: "mean"})
    )

    # Check if the mean column is all 0, NaN, or null - if so, return early
    if len(parent_mean) == 0 or parent_mean["mean"].isna().all() or np.isclose(parent_mean["mean"], 0).all():
        # Mean column is all 0, NaN, or null, return original df with empty ratio column
        df[gs.cc_ratio] = None
        return df

    # Merge stats back into df
    df = df.merge(parent_mean, on=group_cols, how="left")  # Keeps all rows, even if no mean exists

    # Compute fitness ratio relative to the mean - OPTIMIZED
    # Vectorized ratio calculation with rounding in one step
    # Only compute where mean exists and is not zero
    valid_mask = df["mean"].notna() & (df["mean"] != 0)
    df[gs.cc_ratio] = np.where(valid_mask, (df[value_col] / df["mean"]).round(3), np.nan)

    group_stats_ratio = (
        df.groupby(group_cols, sort=False)[gs.cc_ratio].agg(min_group_ratio="min", max_group_ratio="max").reset_index()
    )

    # merge ratio and min max of the ratio values into the data
    df = df.merge(group_stats_ratio, on=group_cols, how="left")

    return df


def extract_all_substrate_product_smiles_from_lab_data(list_of_all_lab_experiments_with_meta: list):
    """Extracts unique substrate and product SMILES from all lab experiments.

    Collects and deduplicates all substrate and product SMILES strings from the
    experiment metadata, returning them as semicolon-delimited sorted strings.

    Args:
        list_of_all_lab_experiments_with_meta: List of experiment metadata dictionaries
                                               (AG Grid data format)

    Returns:
        Tuple of (substrate_smiles_string, product_smiles_string):
            - substrate_smiles_string: Semicolon-delimited sorted unique substrates
            - product_smiles_string: Semicolon-delimited sorted unique products
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


def export_data_as_csv(option, file_name):
    """Generates CSV export parameters for AG Grid table downloads.

    Helper function that creates configuration parameters for AG Grid's built-in
    CSV export functionality. Adds timestamp to filename and determines which rows
    to export based on user selection.

    Args:
        option: Download type option (filtered or all) from DownloadType enum
        file_name: Base name for the downloaded CSV file (without extension)

    Returns:
        Tuple of (export_trigger, export_params):
            - export_trigger: Boolean (True) to trigger the export
            - export_params: Dict with fileName and exportedRows configuration

    Note:
        The actual export is handled by AG Grid on the client side
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
    """Validates a SMILES string and returns UI styling indicators.

    Helper function for Dash input validation that checks if a SMILES string
    is valid using RDKit. Returns boolean flags for UI styling (valid/invalid).

    Args:
        smiles_string: SMILES string to validate

    Returns:
        Tuple of (valid, invalid):
            - valid: True if SMILES is valid, False otherwise
            - invalid: True if SMILES is invalid, False otherwise

    Note:
        Both flags are returned for Dash Bootstrap Components' input validation styling
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
    """Selects the first row of AG Grid table data for default selection.

    Used to set default row selection in tables after they're rendered and sorted
    on the client side. Since sorting happens client-side, we can't preselect from
    the original data order.

    Args:
        data: List of row data dictionaries from AG Grid virtualRowData

    Returns:
        List containing the first row dictionary, or None if data is empty
    """
    if data:
        # set the default selected row to be the first row that is rendered on the front end
        # the table sets the sorting and all on the front end side after it is rendered, so we
        # can not select the first row of the data output that gets sent from the previous
        # callback.
        return [data[0]]

    return None


def log_with_context(msg, log_flag):
    """Logs a message with process, thread, and function context information.

    Conditional logging helper that includes PID, thread ID, thread name, and
    calling function name for debugging multi-threaded/multi-process applications.

    Args:
        msg: Message to log
        log_flag: Boolean flag to enable/disable logging for this call

    Note:
        Only logs if log_flag is True. Useful for profiling and debugging.
        Format: [PID:pid][TID:tid][thread_name][FUNC:function_name] message
    """
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
