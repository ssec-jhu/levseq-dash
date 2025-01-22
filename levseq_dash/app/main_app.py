import re
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
from dash_molstar.utils import molstar_helper

from levseq_dash.app import global_strings as gs
from levseq_dash.app import layout_experiment, layout_upload, parser
from levseq_dash.app.file_manager import FileManager

# Initialize the app
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(
    __name__,
    title=gs.web_title,
    external_stylesheets=[dbc.themes.PULSE, dbc_css, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

# VERY important line of code for running with gunicorn
# you run the 'server' not the 'app'. VS. you run the 'app' with uvicorn
server = app.server

load_figure_template(gs.dbc_template_name)
# Define the form layout

# app keeps one instance of the db manager
# TODO: this may be replaced
data_mgr = FileManager()

app.layout = dbc.Container(
    [
        # top_navbar,
        layout_upload.upload_form_layout,
        html.Div(id="temp-output", className="mt-4"),  # TODO: temp
        html.Br(),
        layout_experiment.layout,
        dcc.Store(id="id-data-exp"),
        dcc.Store(id="id-data-structure"),
    ],
    fluid=True,
)


@app.callback(
    # Output("temp-output", "children"),
    Output("id-button-upload-data-info", "children"),
    # Output("id-button-upload-data", "style"),
    Output("id-data-exp", "data"),
    Input("id-button-upload-data", "contents"),
    State("id-button-upload-data", "filename"),
    State("id-button-upload-data", "last_modified"),
)
def on_upload_experiment(contents, filename, last_modified):
    if not contents:
        # TODO add the alert
        return "No file uploaded.", no_update
    else:
        info, content_string = parser.parse_contents(contents, filename, last_modified)

        if "Error" in info:  # TODO: mange error uploads properly here.
            return info, no_update
        else:
            return info, content_string


@app.callback(
    # Output("temp-output", "children"),
    Output("id-button-upload-structure-info", "children"),
    # Output("id-button-upload-structure", "style"),
    Output("id-data-structure", "data"),
    Input("id-button-upload-structure", "contents"),
    State("id-button-upload-structure", "filename"),
    State("id-button-upload-structure", "last_modified"),
)
def on_upload_structure(contents, filename, last_modified):
    if not contents:
        # TODO add the alert
        return "No file uploaded.", no_update
    else:
        info, content_string = parser.parse_contents(contents, filename, last_modified)

        if "Error" in info:  # TODO: mange error uploads properly here.
            return info, no_update
        else:
            return info, content_string


@app.callback(
    Output("id-table-top-variants", "rowData"),
    Output("temp-output", "children"),
    Output("id-experiment-name", "children"),
    Output("id-experiment-sequence", "children"),
    Output("id-experiment-mutagenesis-method", "children"),
    Output("id-experiment-date", "children"),
    Output("id-experiment-plate-count", "children"),
    Output("id-experiment-sub-cas", "children"),
    Output("id-experiment-product-cas", "children"),
    Output("id-experiment-assay", "children"),
    Output("id-viewer", "data"),
    Input("id-button-submit", "n_clicks"),
    State("id-input-experiment-name", "value"),
    State("id-input-experiment-date", "date"),
    State("id-input-substrate-cas", "value"),
    State("id-input-product-cas", "value"),
    State("id-list-assay", "value"),
    State("id-radio-epr", "value"),
    State("id-data-structure", "data"),
    State("id-data-exp", "data"),
    prevent_initial_call=True,
)
def on_submit_experiment(
    n_clicks,
    experiment_name,
    experiment_date,
    substrate_cas,
    product_cas,
    assay,
    epr,
    structure_content,
    experiment_content,
):
    if ctx.triggered_id == "id-button-submit":
        # for testing purposes only
        df = parser.convert_experiment_upload_to_dataframe(experiment_content)
        rows, cols = df.shape

        index = data_mgr.add_new_experiment(
            user_id="uer_name",
            experiment_name=experiment_name,
            experiment_time_stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            experiment_date=experiment_date,
            substrate_cas_number=substrate_cas,
            product_cas_number=product_cas,
            assay=assay,
            mutagenesis_method=epr,
            experiment_content=experiment_content,
            geometry_content=structure_content,
        )

        info = f"Experiment contains {rows} rows and {cols} columns."

        exp = data_mgr.get_experiment(index)
        # TODO: verify the CAS numbers somewhere or in another callback
        # verify the experiment here or on another callback
        # file_bytes = base64.b64decode(content_string)
        pdb_cif = molstar_helper.parse_molecule(exp.geometry_file, fmt="cif")
        return (
            exp.data_df.to_dict("records"),
            info,
            exp.experiment_name,
            exp.parent_sequence,
            exp.mutagenesis_method,
            exp.experiment_time,
            exp.plates_count,
            exp.substrate_cas_number,
            exp.product_cas_number,
            exp.assay,
            pdb_cif,
        )
    else:
        return no_update


@app.callback(Output("selected-row-value", "children"), Input("id-table-top-variants", "selectedRows"))
def display_selected_row(selected_rows):
    if selected_rows:
        return f"Selected Column B Value: {selected_rows[0]['amino_acid_substitutions']}"
    return "No row selected."


@app.callback(
    Output("id-viewer", "selection"),
    Output("id-viewer", "focus"),
    Input("id-table-top-variants", "selectedRows"),
    prevent_initial_call=True,
)
def focus_select_output(selected_rows):
    if selected_rows:
        mutations = f"{selected_rows[0]['amino_acid_substitutions']}"
        mutations_split = mutations.split("_") if "_" in mutations else [mutations]
        residues = list()
        for mutation in mutations_split:
            match = re.search(r"[A-Za-z](\d+)[A-Za-z]", mutation)
            if match:
                number = match.group(1)  # Extract the captured number
                residues.append(number)

        # residue = list(range(1, 26)) # you can provide a list
        if len(residues) != 0:
            target = molstar_helper.get_targets(
                chain="A",
                residue=residues,
                auth=True,
                # if it's a CIF file to select the authentic chain names and residue
                # numbers
            )
            sel = molstar_helper.get_selection(
                target,
                # select by default, it will put a green highlight on the atoms
                # default select mode (true) or hover mode (false)
                # select=False,  # default select mode (true) or hover mode (false)
                add=False,
            )  # TODO: do we want to add to the list?
            foc = molstar_helper.get_focus(target, analyse=True)
            return sel, foc

    raise PreventUpdate


@app.callback(
    Output("id-list-assay", "options"),
    Input("id-list-assay", "options"),
    # prevent_initial_call=True,
)
def set_assay_list(assay_list):
    # TODO: check if this gets called back multiple times or not
    assay_list = data_mgr.get_assays()
    return assay_list


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
