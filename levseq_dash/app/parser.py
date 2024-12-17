import base64
import datetime
import io

import pandas
import pandas as pd


def parse_csv_contents(contents, filename, last_modified):
    # TODO: maintain the precision
    # TODO: extract the parent
    # TODO: verify the CAS numbers

    # dtype={
    #     "col1": "int64",  # Use int64 for large integers
    #     "col2": "float64" # Use float64 for high-precision floats
    # }
    content_type, content_string = contents.split(",")
    try:
        if "csv" in filename:
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            rows, cols = df.shape
            return (
                f"File '{filename}' uploaded successfully. "
                f"It contains {rows} rows and {cols} columns. File last modified on "
                f"{datetime.datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')}.",
                df,
            )
        else:
            # TODO: correct alert
            raise Exception
    except Exception as e:
        return f"Error processing file '{filename}': {str(e)}", pandas.DataFrame()
