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
import dash
from dash import Dash, dcc, html, callback, Output, Input, State

from ui_set_user import UIsetUser
from ui_set_metadata import UIsetMetadata
from ui_upload import UIuploadData

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

    # instantiate user interactions
    uiSetUser = UIsetUser()
    uiSetMetadata = UIsetMetadata()
    uiUploadData = UIuploadData()

    # initialize
    uiSetUser.Init()
    uiSetMetadata.Init()
    uiUploadData.Init()

    layout_zapExperiment = [
        html.H3("Unload experiment"),
        html.Button("Zap!", id="btn_zap_experiment", n_clicks=0),
        html.Div(id="unload_experiment_info", children="(none)"),
        html.Textarea(id="unload_error"),
    ]

    app.layout = [
        html.H1(children=app.title, style={"textAlign": "center", "color": "brown"}),
        uiSetUser.Layout(),
        uiSetMetadata.Layout(),
        uiUploadData.Layout(),
        # html.Div(
        #     id="user_input_test",
        #     children=layout_user_input,
        #     style={"width": "100%", "border": "solid", "border-width": "1px"},
        # ),
        # html.Div(
        #     id="fsexec_test",
        #     children=layout_fsexec,
        #     style={"width": "100%", "border": "solid", "border-width": "1px"},
        # ),
        html.Div(
            id="expt_unload_test",
            children=layout_zapExperiment,
            style={"width": "100%", "border": "solid", "border-width": "1px"},
        ),
    ]


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
