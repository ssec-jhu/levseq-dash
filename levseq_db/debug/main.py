#
# main.py
#
# Notes:
#  This script is the web application program entry point.
#
#  Dash "core components" are documented here: https://dash.plotly.com/dash-core-components/
#
#  Flask is documented here: https://flask.palletsprojects.com/en/stable/
#
#  Autoformatter: black
#  Linter: pylance
#

import sys
import os

import flask
from flask import Flask
from dash import Dash, dcc, html, callback, Output, Input

# import dbexec
import wsexec
import global_vars as gv


# emit a banner
# fmt: off
sScriptName = os.path.basename(__file__)
print(f"\nStart {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}...")
# fmt: on


# initial web page layout implementation
def _initWebPage(debugDash: bool) -> None:

    app.title = f"{gv.web_title}{' (DEBUG)' if debugDash else ''}"

    # the database query returns a list of tuples, each of which contains one country name
    # rows = dbexec.Query("get_usernames")
    cols, rows = wsexec.Query("get_usernames", [])

    # build a KVP list of dropdown list items
    aUsers = [{"value": r[0], "label": f"{r[1]} ({r[3]})"} for r in rows]

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
        remoteIPaddr = str(flask.request.remote_addr)
        flask.session["username"] = uid
    else:  # (this should not happen)
        remoteIPaddr = "?.?.?.?"

    # save the IP address in the database table of users
    wsexec.Query("save_user_ip", [uid, remoteIPaddr])

    # get user session config
    cols, rows = wsexec.Query("get_user_info", [uid])  # type:ignore
    flask.session["groupname"] = rows[0][cols.index("groupname")]

    # TODO: GET THE EXPERIMENT ID THROUGH THE UI AND A DATABASE QUERY!!!!
    flask.session["experiment_name"] = "experiment one"
    flask.session["eid"] = 1

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

        # upload the file data
        uid = flask.session["username"]
        eid = flask.session["eid"]
        for fileName, fileContents in zip(aFileNames, aFileContents, strict=True):

            # validate the group/experiment/filename tuple
            cb = wsexec.Query("upload_file", [uid, eid, fileName, fileContents])

            # get uploaded file status
            rval += [html.Li(f"Uploaded {fileName}: ({cb} bytes)")]

    # let Dash inject the results into the HTML document
    return rval


# Dash/Flask application setup
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
    tcpPort = 8050

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
#  customary module-name validation:
if __name__ == "__main__":
    app.server.config.update(SECRET_KEY=gv.session_key)
    app.run(host=hostName, port=str(tcpPort), debug=debugDash, use_reloader=debugDash)
