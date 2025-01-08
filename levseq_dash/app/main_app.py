import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from dash_bootstrap_templates import load_figure_template

from levseq_dash.app import global_strings as gs
from levseq_dash.app import layout_upload, parser

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
# dbmgr = db_manager.DBManager()

app.layout = dbc.Container(
    [
        layout_upload.upload_form_layout,
        html.Div(id="temp-output", className="mt-4"),  # TODO: temp
        dcc.Store(id="id-data-exp"),
        dcc.Store(id="id-data-structure"),
    ],
    # fluid=True,
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
    Output("temp-output", "children"),
    Input("id-button-submit", "n_clicks"),
    State("id-input-experiment-name", "value"),
    State("id-experiment-date", "date"),
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

        # TODO: also add an upload time stamp here
        # TODO: verify the CAS numbers here or on another callback
        # verify the experiment here or on another callback
        return f"Experiment contains {rows} rows and {cols} columns."
    else:
        return no_update


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
