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
import argparse
import uvicorn
import fastapi
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import psycopg
import wsexec
import globals as g


# grab some linux system info
sScriptName = os.path.basename(__file__)

# emit a banner
# fmt: off
g.DebugPrint(f"Start {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}...")
g.DebugPrint(f"Invoked as: {sys.argv[0]} by {g.linux_username}" )
# fmt: on


# Application setup
#
# We use the way this application is invoked to determine whether to emit debugging information:
#
#  invoked as        argv[0]    __name__     wantDeveloperEndpoints
#  python -m main    main.py    "__main__"   yes
#  python main.py    main.py    "__main__"   yes
#  VSCode            main.py    "__main__"   yes
#  uvicorn           uvicorn    "main"       yes iff --workers<2
#
# Typical uvicorn invocation looks like this:
#  uvicorn --host hplc-pc.che.caltech.edu --port 8051 --workers 4 main:app
#
# YMMV if you use a web server other than uvicorn, because we haven't tested this code
#  with anything else!
#
# Debugging information includes:
#  - Request logging
#  - FastAPI documentation endpoints:
#       /docs (Swagger UI)
#       /redoc (OpenAPI ReDoc)
#
if __name__ == "__main__":

    hostName = g.devHost
    tcpPort = g.devPort

    # enable debugging information
    wantDeveloperEndpoints = True

else:

    hostName = g.prodHost
    tcpPort = g.prodPort

    # enable debugging information unless there are two or more uvicorn worker processes
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", action="store", type=int)
    ka = parser.parse_known_args()[0]
    wantDeveloperEndpoints = (ka.workers is None) or (ka.workers == 1)

# instantiate FastAPI
g.DebugPrint(f"wantDeveloperEndpoints: {wantDeveloperEndpoints}")
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
            g.DebugPrint(JSONResponse(content=jsonable_encoder(args)).body.decode())  # type:ignore

        # process the HTTP request; FastAPI handles serialization (see wsexec.py)
        return wsexec.PostDatabaseQuery(args)

    except Exception as ex:

        # all exceptions bubble up to here
        if isinstance(ex, psycopg.Error):

            # postgres error: transmit the exception class and error info
            msg = ex.__repr__()
            rcode = 500  # Internal Server Error

        else:

            # python error: transmit only the last two lines of the stack trace
            aTrace = traceback.format_exception(ex)
            msg = f"{aTrace[-1]}\\n{aTrace[-2:-1]}" if len(aTrace) >= 2 else str(ex)
            rcode = 422  # Unprocessable Content

        # respond with HTTP error code and message
        raise fastapi.HTTPException(status_code=rcode, detail=msg)


# uvicorn will not load this app correctly unless the script ends with the
#  customary module-name validation:
if __name__ == "__main__":
    uvicorn.run(app, host=hostName, port=tcpPort)
