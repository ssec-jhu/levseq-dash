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
import re
import datetime

import flask
from flask import Flask
import dash
from dash import Dash, dcc, html, callback, Output, Input, State

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

    # dropdown list contents
    cols, rows = wsexec.Query("get_usernames", [])  # type:ignore
    iv = cols.index("uid")
    iu = cols.index("username")
    ig = cols.index("groupname")
    aUsers = [{"value": r[iv], "label": f"{r[iu]} ({r[ig]})"} for r in rows]

    cols, rows = wsexec.Query("get_assays", [])  # type:ignore
    aAssays = [{"value": r[0], "label": r[1]} for r in rows]

    cols, rows = wsexec.Query("get_mutagenesis_methods", [])  # type:ignore
    aMutagenesisMethods = [{"value": r[0], "label": r[1]} for r in rows]

    # interaction layout: user ID (dropdown list)
    layout_dbexec = [
        html.H3("dropdown select -> query database -> result set -> dash"),
        dcc.Dropdown(aUsers, value=5, id="dropdown_users"),
        html.Div(id="div_user_info"),
    ]

    # interaction layout: experiment metadata
    # fmt:off
    layout_ui_experiment_name = [
        html.Label("experiment name:", htmlFor="input_experiment_name"),
        dcc.Input(id="input_experiment_name", type="text", value="expt1", style={"width": "128px"}),
    ]
    layout_ui_experiment_date = [
        html.Label("experiment date:", htmlFor="input_experiment_date"),
        dcc.DatePickerSingle(
            id="input_experiment_date",
            min_date_allowed=datetime.date(2020, 1, 1),
            max_date_allowed=datetime.datetime.now(),
            initial_visible_month=datetime.datetime.today(),
            date=datetime.datetime.today(),
            style={"height":"8px"}
    ),
    ]
    layout_ui_cas_substrate = [
        html.Label("CAS (substrate):", htmlFor="input_cascsv_substrate"),
        dcc.Input(id="input_cascsv_substrate", type="text", value="345905-97-7", style={"width": "160px"}),
    ]
    layout_ui_cas_product = [
        html.Label("CAS (product):", htmlFor="input_cascsv_product"),
        dcc.Input(id="input_cascsv_product", type="text", value="395683-37-1", style={"width": "160px"}),
    ]
    layout_ui_assay = [
        html.Label("assay technique:", htmlFor="input_assay"),
        dcc.Dropdown(aAssays, value=8, id="dropdown_assay"),
    ]
    layout_ui_mutagenesis_method = [
        html.Label("mutagenesis method:", htmlFor="dropdown_mm"),
        dcc.Dropdown(aMutagenesisMethods, value=2, id="dropdown_mm"),
    ]
    layout_ui_experiment_id = [
        html.Label("experiment ID:", htmlFor="div_eid"),
        html.Div(id="div_eid", children="(none yet)", style={"width":"128px","borderStyle":"solid","borderWidth":"1px","borderColor":"green"}),
        dcc.Textarea(id="div_eid_error"),
    ]
    # fmt:on

    layout_user_input = [
        html.H3("experiment metadata -> database server -> scalar (experiment ID)"),
        html.Div(id="div_experiment_name", children=layout_ui_experiment_name),
        html.Div(id="div_experiment_date", children=layout_ui_experiment_date),
        html.Div(id="div_cas_substrate", children=layout_ui_cas_substrate),
        html.Div(id="div_cas_product", children=layout_ui_cas_product),
        html.Div(id="div_assay", children=layout_ui_assay),
        html.Div(id="div_mutagenesis_method", children=layout_ui_mutagenesis_method),
        html.Button("Do it", id="btn_init_load", n_clicks=0),
        html.Div(id="div_experiment_id", children=layout_ui_experiment_id),
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
        html.Div(id="div_filenames", children="(none yet)"),
        dcc.Textarea(id="load_error"),
    ]

    layout_zapExperiment = [
        html.H3("Unload experiment"),
        html.Button("Zap!", id="btn_zap_experiment", n_clicks=0),
        html.Div(id="unload_experiment_info", children="(none)"),
        html.Textarea(id="unload_error"),
    ]

    app.layout = [
        html.H1(children=app.title, style={"textAlign": "center", "color": "brown"}),
        html.Div(
            id="dbexec_test",
            children=layout_dbexec,
            style={"width": "100%", "border": "solid", "border-width": "1px"},
        ),
        html.Div(
            id="user_input_test",
            children=layout_user_input,
            style={"width": "100%", "border": "solid", "border-width": "1px"},
        ),
        html.Div(
            id="fsexec_test",
            children=layout_fsexec,
            style={"width": "100%", "border": "solid", "border-width": "1px"},
        ),
        html.Div(
            id="expt_unload_test",
            children=layout_zapExperiment,
            style={"width": "100%", "border": "solid", "border-width": "1px"},
        ),
    ]


# callback: user list dropdown selection
@callback(
    Output("div_user_info", "children"),
    Input("dropdown_users", "value"),
    prevent_initial_call=False,
)
def selectUser(uid) -> list:
    print("selectUser")

    # do nothing if the user-selection dropdown has no current value
    if uid is None:
        return ["Current user ID: (none)"]

    if flask.has_request_context():
        remoteIPaddr = str(flask.request.remote_addr)
        flask.session["uid"] = uid
    else:  # (this should not happen)
        remoteIPaddr = "?.?.?.?"

    # save the IP address in the database table of users
    wsexec.Query("save_user_ip", [uid, remoteIPaddr])

    # get user session config
    cols, rows = wsexec.Query("get_user_info", [uid])  # type:ignore
    flask.session["groupname"] = rows[0][cols.index("groupname")]

    # return the current user name for HTML display
    return [f"Current user ID: {uid}"]


# try to clean the specified Exception string representation
def getExceptionText(ex: Exception) -> list[str]:

    # convert embedded newline markers in the Exception string to HTML markup
    aLines = re.split(r"\n|\\n", str(ex))

    # if we have only one line of text, return the repr (which includes the python exception name)
    if len(aLines) == 1:
        aLines = [ex.__repr__()]

    return aLines


def _exception_getExperimentID(ex: Exception) -> list[str]:
    print("_exception_getExperimentID")

    # emit exception text
    aText = "\n".join(getExceptionText(ex))
    dash.set_props("div_eid_error", dict(value=aText))

    # the return value is bound to the associated callback Output(s)
    return ["(error)"]


# callback: experiment metadata validation / get new experiment ID
@callback(
    [Output("div_eid", "children")],
    [Input("btn_init_load", "n_clicks")],
    [
        State("input_experiment_name", "value"),
        State("input_experiment_date", "date"),
        State("dropdown_assay", "value"),
        State("dropdown_mm", "value"),
        State("input_cascsv_substrate", "value"),
        State("input_cascsv_product", "value"),
    ],
    prevent_initial_call=True,
    on_error=_exception_getExperimentID,
)
def getExperimentID(
    n_clicks: int,
    experimentName: str,
    experimentDate: str,
    assay: int,
    mutagenesis_method: int,
    cas_substrate: str,
    cas_product: str,
) -> list[str]:
    print("getExperimentID...")

    # validate the user-entered experiment metadata and get a experiment ID
    eid = wsexec.Query(
        "init_load",
        [
            flask.session["uid"],
            experimentName,
            experimentDate,
            assay,
            mutagenesis_method,
            cas_substrate,
            cas_product,
        ],
    )  # type:ignore

    # update session variables
    flask.session["experiment_name"] = experimentName
    flask.session["eid"] = eid

    # update the UI state
    dash.set_props("div_eid_error", dict(value="(no error)"))

    return [str(eid)]


def _exception_uploadFiles(ex: Exception) -> tuple:
    print("_exception_uploadFiles")

    # emit exception text
    aText = "\n".join(getExceptionText(ex))
    dash.set_props("load_error", dict(value=aText))

    # the return value is bound to the associated callback Output(s)
    return (["(error)"], [], [])


# callback: file load
#
# This Dash implementation is as ugly as it could possibly be:
#
#  - The Upload component triggers a callback only when the contents of its "filename"
#     and/or "contents" properties change, even if the user re-selects the same file(s)
#     in the component interactive dialog.
#
#  - This means we need to reset these properties explicitly by binding them as Output
#     in this callback implementation.
#
#  - But changing the properties triggers another callback! So that means we need to
#     handle the re-entrant condition explicitly.  We do it by examining the "filename"
#     value.
#
#  - Finally, in the re-entrant situation, we need to preserve the state of any other Output
#     components.
#
# Apparently this horrible implementation is by design.  See, for example,
#  https://community.plotly.com/t/upload-attributes-not-cleared-after-callback-runs/40697
#
# This entire trap can be avoided by NOT using the Upload component to actually upload
#  anything!  Instead, the code can be written to keep the filenames and content around
#  until some other UI component does something with them. (Typically "pythonic" approach:
#  a few lines of code come at the expense of megabytes of bloat.) AARGH!
#
@callback(
    [
        Output("div_filenames", "children"),
        Output("upload-data", "filename"),
        Output("upload-data", "contents"),
    ],
    [
        Input("upload-data", "filename"),
        Input("upload-data", "contents"),
    ],
    [
        State("div_filenames", "children"),
    ],
    prevent_initial_call=True,
    on_error=_exception_uploadFiles,
)
def uploadFiles(aFileNames: list[str], aFileContents: list[str], aUF: list[str]) -> tuple:
    print(f"uploadFiles: aFileNames: {aFileNames}, aUF: {aUF}")

    # If this callback was triggered by resetting the Upload component's "filename" and/or
    #  "contents" properties (see below), all we need to do is ensure that the UI state
    #  doesn't change.
    if len(aFileNames) == 0:
        return (aUF, [], [])

    uid = flask.session["uid"]
    eid = flask.session["eid"]

    rval = ""
    for fileName, fileContents in zip(aFileNames, aFileContents, strict=True):

        # upload the file data
        cb = wsexec.Query("load_file", [uid, eid, fileName, fileContents])

        # show uploaded file info
        rval += f"Uploaded {fileName}: ({cb} bytes); "

    # update UI state
    dash.set_props("load_error", dict(children="(no error)"))
    dash.set_props("unload_error", dict(value="(no error)"))
    dash.set_props("unload_experiment_info", dict(children="(none)"))

    # clear the Upload component filename and contents
    dash.set_props("upload-data", dict(filename=None, contents=None))

    # update the UI state and reset the Upload component's "filename" and "contents" properties
    return ([rval], [], [])


def _exception_unloadExperiment(ex: Exception) -> list[str]:
    print("_exception_unloadExperiment")

    # emit exception text
    aText = "\n".join(getExceptionText(ex))
    dash.set_props("unload_error", dict(value=aText))

    # the return value is bound to the associated callback Output(s)
    return ["(error)"]


# callback: experiment unload
@callback(
    [Output("unload_experiment_info", "children")],
    [Input("btn_zap_experiment", "n_clicks")],
    prevent_initial_call=True,
    on_error=_exception_unloadExperiment,
)
def unloadExperiment(n_clicks: int) -> str:
    print("unloadExperiment...")

    uid = flask.session["uid"]
    eid = flask.session["eid"]

    # unload the experiment data and delete all assocated uploaded files
    wsexec.Query("unload_experiment", [uid, eid])

    msg = f"Unloaded experiment ID {flask.session["eid"]} ({flask.session["experiment_name"]})"

    # update UI state (maybe return as Output(), but this seems simpler)
    dash.set_props("load_error", dict(value="(no error)"))
    dash.set_props("unload_error", dict(value="(no error)"))
    dash.set_props("uploaded_filenames", dict(children=""))

    # update session state
    flask.session["eid"] = None
    flask.session["experiment_name"] = None

    return msg


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
