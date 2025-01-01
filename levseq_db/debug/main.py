#
# main.py
#
# Notes:
#  This script is the web application program entry point.
#
#  Dash "core components" are documented here: https://dash.plotly.com/dash-core-components/
#  Flask is documented here: https://flask.palletsprojects.com/en/stable/
#
#  Autoformatter: black
#  Linter: pylance
#

import sys
import os

from flask import Flask
from dash import Dash, html

from ui_set_user import UIsetUser
from ui_set_metadata import UIsetMetadata
from ui_upload import UIuploadData
from ui_unload import UIunloadData

import globals as g


# emit a banner
# fmt: off
sScriptName = os.path.basename(__file__)
print(f"\nStart {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}...")
# fmt: on


# initial web page layout implementation
def _initWebPage(debugDash: bool) -> None:

    app.title = f"{g.web_title}{' (DEBUG)' if debugDash else ''}"

    # instantiate user interactions
    uiSetUser = UIsetUser()
    uiSetMetadata = UIsetMetadata()
    uiUploadData = UIuploadData()
    uiUnloadData = UIunloadData()

    # page layout (see assets/main.py for additional CSS styles)
    app.layout = [
        html.H1(children=app.title, style={"textAlign": "center", "color": "brown"}),
        uiSetUser.Layout(),
        uiSetMetadata.Layout(),
        uiUploadData.Layout(),
        uiUnloadData.Layout(),
    ]


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
    srvFlask = Flask(__name__)
    app = Dash(__name__, server=srvFlask)  # (corresponds to gunicorn parameter "main:srvFlask")
    debugDash = False
    hostName = "hplc-pc.che.caltech.edu"
    tcpPort = 8051

# initialize the web page layout
_initWebPage(debugDash)

# gunicorn will not load this app correctly unless the script ends with the
#  customary module-name validation:
if __name__ == "__main__":
    app.server.config.update(SECRET_KEY=g.flask_session_key)
    app.run(host=hostName, port=str(tcpPort), debug=debugDash, use_reloader=debugDash)
