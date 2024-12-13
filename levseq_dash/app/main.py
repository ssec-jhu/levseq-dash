#
# main.py
#
# Notes:
#  This script is the web application program entry point.
#

### TODO: GET RID OF IMPORTS THAT ARE NO LONGER USED (SEE BELOW)
import sys
import base64
import os
from urllib.parse import quote as urlquote

from flask import Flask, send_from_directory
from dash import Dash, dcc, html, callback, Output, Input

import dbexec
import global_strings as gs


### TODO: DELETE THIS JUNK
### tuples = dbexec.doFetch( "countries" )
### tuples = dbexec.doFetch( "population_data", ["Turkey"] )
### tuples = dbexec.doFetch( "population_data_3", ["France", "Italy", "Oz"] )



def initWebPage( debugDash : bool ) -> None:

    app.title = f"{gs.web_title}{' (DEBUG)' if debugDash else ''}"

    # the database fetch returns a list of tuples, each of which contains one country name;
    #  the join "stringizes" a tuple, so the list comprehension builds a list of country name strings
    tuples = dbexec.doFetch( "countries" )
    aCountries = [''.join(t) for t in tuples]

    app.layout = [
        html.H1(children=app.title, style={'textAlign':'center','color':'brown'}),
        dcc.Dropdown(aCountries, '', id='dropdown-selection'),
        html.Ul(id="population_data_rows")
    ]


@callback( Output('population_data_rows', 'children'),
           Input('dropdown-selection', 'value'),
           prevent_initial_call=True )
def initTable(value):

    tuples = dbexec.doFetch( "population_data", [value] )

    # Each row in the result set is a tuple that needs to be "stringified".
    #
    # - For each tuple, we add an HTML LI element to the predefined parent UL element:
    #       for raw_tuple in tuples
    # - The text of the LI requires an iteration across the tuple's items:
    #       for t in raw_tuple
    # - The join concatenates the stringified value of each item in the tuple:
    #       ' '.join( ... )
    #
    # This ugly code should probably be avoided by letting the database server
    #  "stringify" the rows.
    #
    return [html.Li(' '.join( tuple(str(t) for t in raw_tuple) ) ) for raw_tuple in tuples]



if False :
    ### TODO DELETE THIS OLD JUNK ASAP
    import upload

    pathToHostDir = "/mnt/Data/ssec-devuser/uploads"


    if not os.path.exists(upload.pathToHostDir):
        os.makedirs(upload.pathToHostDir)


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


sScriptName = os.path.basename(__file__)
print(f"\nStart {sScriptName} __name__={__name__} pid={os.getpid()}, python v{sys.version.split('|')[0]}...")

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

    # We assume this script is loaded as a module by a web server...
    #
    # - We need to provide a flask wrapper.
    #
    # - For gunicorn:  the module name (i.e., the bare filename) and the global variable that
    #    references the flask instance must be referenced in the command line, e.g.:
    #
    #       gunicorn --workers=2 --bind="hplc-pc.che.caltech.edu:8051" main:srvFlask
    #
    srvFlask = Flask(__name__)
    app = Dash(__name__, server=srvFlask)   # (corresponds to "main:srvFlask" in the gunicorn command line)

    debugDash = False
    hostName = 'hplc-pc.che.caltech.edu'
    tcpPort = 8051              # port 8051 for users

# initialize the web page layout
initWebPage( debugDash )

# gunicorn will not load this app correctly unless the script ends with following
#  two-line magic incantation
if __name__ == '__main__' :
    app.run( debug=debugDash, host=hostName, port=tcpPort, use_reloader=debugDash )
