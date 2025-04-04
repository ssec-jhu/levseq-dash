import base64

import dash
import dash_bootstrap_components as dbc
import dash_molstar
from dash import Input, Output, dcc, html
from dash_molstar.utils import molstar_helper

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout for the app
app.layout = html.Div(
    [
        html.H1("Testing protein Viewer with Dash Mol*star"),
        dcc.Upload(
            id="id-upload-pdb",
            children=dbc.Button("Upload PDB/CIF File", color="secondary", outline=True),
            multiple=False,  # Allow only single file upload
        ),
        html.Div(id="file-name"),
        dash_molstar.MolstarViewer(
            id="id-molstar-viewer",
            style={"width": "auto", "height": "600px"},
        ),
    ]
)


# Callback to update the viewer with the uploaded PDB file
@app.callback(
    Output("id-molstar-viewer", "data"),
    Output("file-name", "children"),
    Input("id-upload-pdb", "contents"),
)
def update_molstar_viewer(contents):
    if contents is None:
        return "", "No file uploaded yet."

    # Extract the file content from the uploaded file (base64 encoded string)
    content_type, content_string = contents.split(",")
    pdb_bytes = base64.b64decode(content_string)

    # works with cif files for now
    try:
        pdb_cif = molstar_helper.parse_molecule(pdb_bytes, fmt="cif")
    except Exception as e:
        print(f"exception:{e}")

    # Decode the base64 string back into bytes
    decoded_file = base64.b64decode(content_string)

    # Return the decoded file to be shown in the Mol*star viewer
    return pdb_cif, f"File uploaded: {content_type}"


if __name__ == "__main__":
    app.run(debug=True)
