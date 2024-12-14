#
# main.py
#
# Notes:
#  This script is the web application program entry point.
#

import sys
import os

from flask import Flask
from dash import Dash, dcc, html, callback, Output, Input

import dbexec
import fsexec
import global_strings as gs


# emit a banner
sScriptName = os.path.basename(__file__)
print(f"\nStart {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}...")

# initial web page layout implementation
def _initWebPage( debugDash : bool ) -> None:

    app.title = f"{gs.web_title}{' (DEBUG)' if debugDash else ''}"

    # the database query returns a list of tuples, each of which contains one country name
    rows = dbexec.Query( "countries" )

    # convert each row tuple to a string
    aCountries = [dbexec.RowToString(r) for r in rows]

    # dbexec interaction layout
    layout_dbexec = [
        html.H3("dropdown select -> query database -> result set -> dash"),
        dcc.Dropdown(aCountries, '', id='country_selection'),
        html.Ul(id='population_data_rows')
    ]

    # fsexec interaction layout
    layout_fsexec = [
        html.H3("local CSV file select -> upload to database server -> load into database table -> result set -> dash"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and drop or click to select a file to upload"]),
            style={
                "width": '320px',
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True
        )
    ]
    
    app.layout = [
        html.H1(children=app.title, style={'textAlign':'center', 'color':'brown'}),
        html.Div(id='dbexec_test', children=layout_dbexec,style={'width': '100%', 'border':'solid', 'border-width':'1px'}),
        html.Div(id='fsexec_test', children=layout_fsexec,style={'width': '100%', 'border':'solid', 'border-width':'1px'})
    ]

# callback: country list dropdown selection
@callback( Output('population_data_rows', 'children'),
           Input('country_selection', 'value'),
           prevent_initial_call=True )
def initTable(value) -> list:

    # the database implementation returns query results as a list of tuples
    rows = dbexec.Query( "population_data", [value] )

    # concatenate the row data into strings for HTML display
    return [html.Li(dbexec.RowToString(r)) for r in rows]

# callback: file upload
@callback( ## TODO: Output("file-list", "children"),
           [Input("upload-data", "filename"), Input("upload-data", "contents")] )
def writeUploadedFiles(aFileNames: list[str], aFileContents:list[str]) -> None:

    print( 'writeUploadedFiles...')

    if aFileNames is not None and aFileContents is not None:
        for fileName, fileContents in zip(aFileNames, aFileContents, strict=True):
            cb = fsexec.UploadBase64File(fileName, fileContents)


            ### TODO: GET RID OF THIS ASAP
            print( f"Uploaded {fileName}: {cb} bytes")
            print( f"Upload status: {fsexec.FileUploadStatus(fileName)}" )

    return  ## should populate a list of uploaded files and statuses



# Web application setup
#
# The loader-assigned module name lets us determine whether we are loaded by the dash debug server
#  or by gunicorn.
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
    hostName = 'localhost'
    tcpPort = 8050              # port 8050 for debugging

else:

    # We assume this script is loaded as a module by gunicorn...
    #
    # - We need to provide a flask wrapper.
    #
    # - For gunicorn:  the module name (i.e., the bare filename) and the global variable that
    #    references the flask instance must be referenced in the command line, e.g.:
    #
    #       gunicorn --workers=2 --bind="hplc-pc.che.caltech.edu:8051" main:srvFlask
    #
    # YMMV if you use a web server other than gunicorn!  (We haven't tested this code with anything else.)
    #
    srvFlask = Flask(__name__)
    app = Dash(__name__, server=srvFlask)   # (corresponds to "main:srvFlask" in the gunicorn command line)

    debugDash = False
    hostName = 'hplc-pc.che.caltech.edu'
    tcpPort = 8051              # port 8051 for users

# initialize the web page layout
_initWebPage( debugDash )

# gunicorn will not load this app correctly unless the script ends with the
#  following two-line voodoo
if __name__ == '__main__' :
    app.run( debug=debugDash, host=hostName, port=tcpPort, use_reloader=debugDash )
