import base64
import io

import pandas as pd

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


def decode_base64_binary_string_to_base64_bytes(dash_upload_string_contents):
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


def decode_base64_string_to_base64_bytes(base64_encoded_string):
    # base64.b64decode() function converts the base64 encoded string back
    # into its original binary data which is bytes.
    base64_encoded_bytes = base64.b64decode(base64_encoded_string)
    return base64_encoded_bytes


def decode_csv_file_base64_string_to_dataframe(base64_encoded_string):
    df = decode_csv_file_bytes_to_dataframe(decode_base64_string_to_base64_bytes(base64_encoded_string))
    return df


def decode_csv_file_bytes_to_dataframe(base64_encoded_bytes):
    """
    utility function for testing the uploaded experiment file
    """
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
        df = pd.DataFrame()
        # return "The content is not a valid UTF-8 string."

    return df
