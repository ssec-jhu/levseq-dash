#
# main.py
#
# Notes:
#  This script is the web application program entry point.
#
#  Dash "core components" are documented here: https://dash.plotly.com/dash-core-components/
#
#  Autoformatter: black
#  Linter: pylance
#

import sys
import os

import flask
from flask import Flask
from dash import Dash, dcc, html, callback, Output, Input

import dbexec
import fsexec
import global_strings as gs


# emit a banner
sScriptName = os.path.basename(__file__)
print(
    f"\nStart {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}..."
)


# initial web page layout implementation
def _initWebPage(debugDash: bool) -> None:

    app.title = f"{gs.web_title}{' (DEBUG)' if debugDash else ''}"

    # the database query returns a list of tuples, each of which contains one country name
    rows = dbexec.Query("get_usernames")

    # convert each row tuple to a string
    aUsers = [dbexec.RowToDropdownOption(r) for r in rows]

    # interaction layout: user ID (dropdown list)
    layout_dbexec = [
        html.H3("dropdown select -> query database -> result set -> dash"),
        dcc.Dropdown(aUsers, "", id="user_selection"),
        html.Ul(id="selected_user"),
    ]

    # interaction layout: file upload
    layout_fsexec = [
        html.H3(
            "local CSV file select -> upload to database server -> load into database table -> result set -> dash"
        ),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and drop or click to select files to upload"]),
            style={
                "width": "320px",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
            accept=".csv,.cif,.pdb",
        ),
        html.Ul(id="uploaded_filenames", children="(none yet)"),
    ]

    app.layout = [
        html.H1(children=app.title, style={"textAlign": "center", "color": "brown"}),
        html.Div(
            id="dbexec_test",
            children=layout_dbexec,
            style={"width": "100%", "border": "solid", "border-width": "1px"},
        ),
        html.Div(
            id="fsexec_test",
            children=layout_fsexec,
            style={"width": "100%", "border": "solid", "border-width": "1px"},
        ),
    ]


# callback: user list dropdown selection
@callback(
    Output("selected_user", "children"),
    Input("user_selection", "value"),
    prevent_initial_call=True,
)
def selectUser(uid) -> list:

    if flask.has_request_context():
        remoteIPaddr = flask.request.remote_addr
        flask.session["user"] = uid
        flask.session["upload_dir"] = (
            gs.host_upload_directory
        )  # TODO: GET THIS FROM DB!!!
    else:  # (this should not happen)
        remoteIPaddr = "?.?.?.?"

    # save the IP address in the database table of users
    dbexec.NonQuery("save_user_ip", [uid, remoteIPaddr])

    # return the current user name for HTML display
    return [f"Current user ID: {uid}"]


# callback: file upload
@callback(
    Output("uploaded_filenames", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
    prevent_initial_call=True,
)
def writeUploadedFiles(aFileNames: list[str], aFileContents: list[str]) -> list:

    rval = []

    if aFileNames is not None and aFileContents is not None:
        hostUploadDir = flask.session["upload_dir"]
        for fileName, fileContents in zip(aFileNames, aFileContents, strict=True):
            fileSpec = os.path.join(hostUploadDir, fileName)

            cb = fsexec.UploadBase64File(fileSpec, fileContents)

            if fileName[-4:].lower() == ".csv":
                dbexec.NonQuery("load_csv_file", [fileSpec])

            uploadStatus = fsexec.FileUploadStatus(fileName)
            rval += [html.Li(f"Uploaded {fileName}: {cb} bytes (status: {uploadStatus})")]

    return rval


# Web application setup
#
# The loader-assigned module name lets us determine whether we are loaded by a python script
#  loader or as a module (e.g., by gunicorn).
#
# We use TCP port 8050 for debugging and port 8051 for users.
if __name__ == "__main__":

    # We assume we are running from the command line or within a debugger (e.g., VSCode)...
    #
    # - All we need is a dash app instance.
    #
    # - If we use localhost, we can debug on the local machine or on a remote machine via port
    #    forwarding (which VSCode knows how to do without being told).
    #
    app = Dash(__name__)
    debugDash = True
    hostName = "localhost"
    tcpPort = 8051

else:

    # We assume that a loader (e.g., gunicorn) imports this script as a module
    #  and calls variable app directly.  This means...
    #
    # - __name__ == 'main' (not '__main__').
    #
    # - We need to provide a flask wrapper.
    #
    # YMMV if you use a web server other than gunicorn, because we haven't tested this code
    #  with anything else!
    #
    # fmt:off
    srvFlask = Flask(__name__)
    app = Dash(__name__, server=srvFlask)  # (corresponds to gunicorn parameter "main:srvFlask")
    debugDash = False
    hostName = 'hplc-pc.che.caltech.edu'
    tcpPort = 8051
    # fmt:on

# initialize the web page layout
_initWebPage(debugDash)

# gunicorn will not load this app correctly unless the script ends with the
#  following two lines of code:
if __name__ == "__main__":
    app.server.config.update(SECRET_KEY=gs.session_key)
    app.run(host=hostName, port=str(tcpPort), debug=debugDash, use_reloader=debugDash)
