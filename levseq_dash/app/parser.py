import base64
import datetime
import io

import pandas as pd


def parse_contents(contents, filename, last_modified):
    # TODO: maintain the precision
    # TODO: extract the parent

    # dtype={
    #     "col1": "int64",  # Use int64 for large integers
    #     "col2": "float64" # Use float64 for high-precision floats
    # }
    content_type, content_string = contents.split(",")
    file_bytes = base64.b64decode(content_string)
    file_size = len(file_bytes)

    if file_size < 1024:
        file_size_text = f"{file_size} bytes"
    elif file_size < 1024**2:
        file_size_text = f"{file_size / 1024:.2f} KB"
    else:
        file_size_text = f"{file_size / (1024 ** 2):.2f} MB"

    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.StringIO(file_bytes.decode("utf-8")))
            rows, cols = df.shape
            info = (
                f"Filename: '{filename}'; File size: {file_size_text}; Last modified on "
                f" {datetime.datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')}. "
                f"It contains {rows} rows and {cols} columns."
            )
        elif any(filename.lower().endswith(ext) for ext in {".pdb", ".cif"}):
            info = (
                f"Filename: '{filename}'; File size: {file_size_text}; Last modified on "
                f"{datetime.datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')}."
            )

        else:
            # TODO: correct alert, add to the alert manager
            raise Exception
    except Exception as e:
        info = f"Error processing file '{filename}': {str(e)}"
        content_string = ""

    return info, content_string


def convert_experiment_upload_to_dataframe(content_string):
    """
    utility function for testing the uploaded experiment file
    """
    df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode("utf-8")))
    return df
