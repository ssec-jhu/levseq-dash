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
#  psycopg3 is documented here: https://www.psycopg.org/psycopg3/docs/
#
#  Autoformatter: black
#  Linter: pylance
#

import sys
import os
import traceback
import uvicorn
import fastapi
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import psycopg
import wsexec
import global_vars as g


# grab some linux system info
sScriptName = os.path.basename(__file__)

# emit a banner
# fmt: off
print(f"\nStart {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}...")
print(f"Invoked as: {sys.argv[0]} by {g.linux_username}" )
# fmt: on


# Application setup
if sys.argv[0] != sScriptName:

    # We assume we are running within a debugger like VSCode, which uses a fully-qualified
    #  file specification instead of a bare filename.  In this case we use localhost so we
    #  can debug on the local machine or on a remote machine via port forwarding (which
    #  VSCode knows how to do without being told).
    #
    hostName = g.devHost
    tcpPort = g.devPort
    wantDeveloperEndpoints = True

else:

    # We assume that a loader (i.e., uvicorn) imports this script as a module.  This also
    #  occurs when this webservice is loaded by python, so we can launch the webservice by
    #  doing
    #
    #   python main.py [boolean]
    #
    # YMMV if you use a web server other than uvicorn, because we haven't tested this code
    #  with anything else!
    #
    hostName = g.prodHost
    tcpPort = g.prodPort

    # The first command-line parameter (e.g., python main.py True) controls whether the
    #  webservice exposes FastAPI's /docs (Swagger UI) and /redoc (OpenAPI ReDoc) endpoints.
    wantDeveloperEndpoints = (len(sys.argv) >= 2) and (sys.argv[1])

# instantiate FastAPI
print(f"wantDeveloperEndpoints: {wantDeveloperEndpoints}")
if wantDeveloperEndpoints:
    app = fastapi.FastAPI()
else:
    app = fastapi.FastAPI(docs_url=None, redoc_url=None)


# Webservice endpoints
#
#  There's only one (or two if you count the "ping" functionality):
#
#   GET requests    response
#   "/": ping       200 OK
#   (all others)    404 Not Found
#
#   POST requests   response
#   "/": queries    200 OK: successful postgres SQL execution
#                   400 Bad Request: bad parameter syntax (invalid verb, wrong number or format of parameters)
#                   500 Internal Server Error (error raised in postgres SQL code)
#   (all others)    404 Not Found
#
#  FastAPI's default implementation differentiates among several error response categories.
#   HTTP response 200 means "success", and HTTP response >= 400 means "failure" with FastAPI-
#   provided response data:
#
#       [ "details": "(error details") ]


@app.get("/")
async def getRoot() -> wsexec.QueryResponse:
    return wsexec.GetImplementationInfo()


@app.post("/")
async def query(args: wsexec.QueryParams) -> wsexec.QueryResponse:

    try:

        # conditionally emit query arguments as JSON
        if wantDeveloperEndpoints:
            print(JSONResponse(content=jsonable_encoder(args)).body.decode())  # type:ignore

        # process the HTTP request; FastAPI handles serialization (see wsexec.py)
        return wsexec.PostDatabaseQuery(args)

    except Exception as ex:

        # all exceptions bubble up to here
        if isinstance(ex, psycopg.Error):

            # postgres error: transmit the exception class and error info
            msg = ex.__repr__()

        else:

            # python error: transmit only the last two lines of the stack trace
            aTrace = traceback.format_exception(ex)
            msg = f"{aTrace[-1]}\\n{aTrace[-2:-1]}" if len(aTrace) >= 2 else str(ex)

        # return HTTP 422 Unprocessable Content
        raise fastapi.HTTPException(status_code=422, detail=msg)


# uvicorn will not load this app correctly unless the script ends with the
#  customary module-name validation:
if __name__ == "__main__":
    uvicorn.run(app, host=hostName, port=tcpPort)
