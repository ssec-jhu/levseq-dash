#
# fsexec.py
#
# Notes:
#  Functionality relating to files in the local filesystem.
#
#  Upload/download strategy based on: https://docs.faculty.ai/user-guide/apps/examples/dash_file_upload_download.html
#

import base64
import os
from urllib.parse import quote as urlquote

import dbexec
import global_strings as gs




# upload a file from a user-selected directory on the web client machine
#  to a predefined directory (which should be located on the database server machine)
def UploadBase64File( fileName: str, b64:str) -> int:

    # The base64-encoded file produced by the dash core component Upload looks like this:
    #
    #   data:text/plain;base64,xxxxx...
    #
    # where xxxxx... is the base64-encoded representation of the binary file contents.
    #
    # (Doing base64 encoding for HTTP file transfers may not be necessary, but it's common
    #  practice and costs very little to ensure that nothing in binary file data can be
    #  misinterpreted, so it's hard to argue with this aspect of the implementation of dcc.Upload.)
    
    # We want the os to write the base64-string as a sequence of bytes, so we encode
    #  the python string as 8-bit bytes, split it on the characters ';base64,', and
    #  grab just the utf8-encoded base64 string.
    b64 = b64.encode('utf8').split(b';base64,')[1]

    # open the output file for binary write; the open() function returns an instance of io.BufferedWriter
    fileSpec = os.path.join(gs.host_upload_directory, fileName)
    with open(fileSpec, "wb") as bw:

        # decode b64 to binary and write the bytes to the output file
        return bw.write(base64.decodebytes(b64))

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
def FileUploadStatus( fileName: str ) -> str:

    # get the file's upload status from the database:
    #  'completed'
    #  'in progress'
    #  'failed: (error message)'
    #  'none'
    msg = dbexec.QueryScalar('get_file_load_status', [fileName])
    if msg != 'none':
        msg = f"uploaded; {msg}"

    else:
        # the file has not been "seen" in the database, so we look in the upload directory
        fileSpec = os.path.join(gs.host_upload_directory, fileName)
        if os.path.isfile(fileSpec):
            msg = 'uploaded; not in database'
        else:
            msg = 'not uploaded'

    return msg


if False:

    import base64
    import os
    from urllib.parse import quote as urlquote

    from flask import Flask, send_from_directory
    import dash
    from dash import dcc, html
    from dash.dependencies import Input, Output


    pathToHostDir = "/mnt/Data/ssec-devuser/uploads"

    if not os.path.exists(pathToHostDir):
        os.makedirs(pathToHostDir)


    # Normally, Dash creates its own Flask server internally. By creating our own,
    # we can create a route for downloading files directly:
    srvFlask = Flask(__name__)
    app = dash.Dash(server=srvFlask)


    @srvFlask.route("/download/<path:fileSpec>")
    def download(fileSpec):
        """Serve a file from the upload directory."""
        return send_from_directory(pathToHostDir, fileSpec, as_attachment=True)


    app.layout = html.Div(
        [
            html.H1("File Browser"),
            html.H2("Upload"),
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag and drop or click to select a file to upload."]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=True,
            ),
            html.H2("Previously uploaded files (on host)"),
            html.Ul(id="file-list"),
        ],
        style={"max-width": "500px"},
    )


    def save_file(name, content):
        """Decode and store a file uploaded with Plotly Dash."""
        data = content.encode("utf8").split(b";base64,")[1]     ### WHAT IS THIS VOODOO?????
        with open(os.path.join(pathToHostDir, name), "wb") as fp:
            fp.write(base64.decodebytes(data))


    def uploaded_files():
        """List the files in the upload directory."""
        files = []
        for filename in os.listdir(pathToHostDir):
            path = os.path.join(pathToHostDir, filename)
            if os.path.isfile(path):
                files.append(filename)
        return files


    def file_download_link(filename):
        """Create a Plotly Dash 'A' element that downloads a file from the app."""
        location = "/download/{}".format(urlquote(filename))
        return html.A(filename, href=location)


    @app.callback(
        Output("file-list", "children"),
        [Input("upload-data", "filename"), Input("upload-data", "contents")],
    )
    def update_output(uploaded_filenames, uploaded_file_contents):
        """Save uploaded files and regenerate the file list."""

        if uploaded_filenames is not None and uploaded_file_contents is not None:
            for name, data in zip(uploaded_filenames, uploaded_file_contents):
                save_file(name, data)

        files = uploaded_files()
        if len(files) == 0:
            return [html.Li("No files yet!")]
        else:
            return [html.Li(file_download_link(filename)) for filename in files]


    