#
# main.py
#
# Notes:
#  This script is the web application program entry point.
#
#  See "Application setup" below for different ways to invoke this script.
#
#  FastAPI is documented here: https://fastapi.tiangolo.com/
#  Dash "core components" are documented here: https://dash.plotly.com/dash-core-components/
#  Flask is documented here: https://flask.palletsprojects.com/en/stable/
#  psycopg3 is documented here: https://www.psycopg.org/psycopg3/docs/
#
#  Autoformatter: black
#  Linter: pylance
#

import sys
import os
import uvicorn
import dbexec
import wsexec
from fastapi import FastAPI
import globals as g


# emit a banner
# fmt: off
sScriptName = os.path.basename(__file__)
print(f"\nStart {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}...")
print(f"Invoked as: {sys.argv[0]}" )
# fmt: on

# instantiate FastAPI
app = FastAPI()


# This webservice is simple:
#  - We only expose one endpoint.
#  - Every HTTP request maps to a postgres SQL stored procedure or function whose signature is:
#      verb [optional parameters]
#  - Every HTTP response is a json structure whose first member is "details", e.g.
#      {
#        "details": "whatever ??????"}
#      }
#    We do this because FastAPI formats error responses in the same way.  A remote client
#     implementation can always expect the "details" member to be present regardless of what
#     the HTTP response code might be.
#
#
# GET requests      response
#  - "/": ping      200 OK
#  - (all others)   404 Not Found
#
# POST requests
# - "/": queries    200 OK: good data
#                   400 Bad Request: bad parameter syntax (invalid verb, wrong number or format of parameters)
#                   500 Internal Server Error (error raised in postgres SQL code)
# - (all others)    404 Not Found


@app.get("/")
async def getRoot() -> wsexec.ResultSet:
    return wsexec.GetImplementationInfo()


#
# TODO
#
# @app.post("/items/")
# async def create_item(item: Item):
#     return item


# TODO: CREATE A wsexec.Query class with members verb (str) and args (list)???
@app.post("/")
async def query() -> wsexec.ResultSet | None:
    return wsexec.ResultSet(columns=["a", "b"], rows=[(1, 2), (3, 4)])


# Application setup
if sys.argv[0] != sScriptName:

    # We assume we are running from the command line or within a debugger (e.g., VSCode, which
    #  uses a fully-qualified file specification instead of a bare filename). If we use
    #  localhost, we can debug on the local machine or on a remote machine via port forwarding
    #  (which VSCode knows how to do without being told).
    #
    hostName = g.devHost
    tcpPort = g.devPort

else:

    # We assume that a loader (i.e., uvicorn) imports this script as a module.
    #
    # YMMV if you use a web server other than uvicorn, because we haven't tested this code
    #  with anything else!
    #
    # fmt:off
    hostName = g.prodHost
    tcpPort = g.prodPort
    # fmt:on

# uvicorn will not load this app correctly unless the script ends with the
#  customary module-name validation:
if __name__ == "__main__":
    # uvicorn also fails if the run() method is invoked with variable names, e.g.
    #    uvicorn.run(app, host=hostName, port=str(tcpPort))
    #  so we have to resort to a little hack...
    s = f"uvicorn.run(app,host='{hostName}', port={tcpPort})"
    exec(s)
