#
# fsexec.py
#
# Notes:
#  Functionality relating to files in the local filesystem.
#
#  Upload/download strategy based on: https://docs.faculty.ai/user-guide/apps/examples/dash_file_upload_download.html
#

import os
import base64

import dbexec
import global_strings as gs


# upload file data produced by the Dash Upload implementation to the
#  database server machine
def UploadExperimentFile(fileSpec: str, b64: str) -> int:

    # the LevSeq files should rarely be more than a few MB in size, so we just ship
    #  the filename and contents to the webservice and assume that the webservers,
    #  postgres, and all the intermediate layers of code can handle a multi-megabyte
    #  "parameter"
    return dbexec.QueryScalar("save_file", [fileSpec, b64])  # type:ignore

    if False:
        # We want the os to write the base64-string as a sequence of bytes, so we encode
        #  the python string as 8-bit bytes, split it on the characters ';base64,', and
        #  grab just the utf8-encoded base64 string.
        b64bytes = b64.encode("utf8").split(b";base64,")[1]

        # open the output file for binary write; the open() function returns an instance of io.BufferedWriter
        with open(fileSpec, "wb") as bw:

            # decode b64 to binary, write the bytes to the output file, and return the number of bytes written
            return bw.write(base64.decodebytes(b64bytes))


# download a file from a predefined directory on the database server machine
#  to a user-selected directory on the web client machine
def DownloadFile():
    return


# get a fully-qualified path to the predefined upload directory on the database server machine
def GetUploadDirectory():
    return


# return a filtered list of filenames in the predefined upload directory
def GetUploadDirectoryList():
    return


# return a string that indicates whether the specified file has been uploaded and
#  subsequently loaded into the database
def GetFileUploadStatus(fileSpec: str) -> str:

    # get the file's upload status from the database:
    #  'completed'
    #  'in progress'
    #  'failed: (error message)'
    #  'none'
    msg = dbexec.QueryScalar("get_file_load_status", [fileSpec])
    if msg != "none":
        msg = f"uploaded; {msg}"

    else:
        # the file has not been "seen" in the database, so we look in the upload directory
        if os.path.isfile(fileSpec):
            msg = "uploaded; not in database"
        else:
            msg = "not uploaded"

    return msg
