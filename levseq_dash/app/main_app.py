import re

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
from dash_molstar.utils import molstar_helper

from levseq_dash.app import global_strings as gs
from levseq_dash.app import graphs, layout_experiment, layout_landing, parser
from levseq_dash.app.data_manager import DataManager
from levseq_dash.app.settings import CONFIG

# Initialize the app
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(
    __name__,
    title=gs.web_title,
    external_stylesheets=[dbc.themes.MINTY, dbc_css, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

# VERY important line of code for running with gunicorn
# you run the 'server' not the 'app'. VS. you run the 'app' with uvicorn
server = app.server

load_figure_template(gs.dbc_template_name)

app.server.config.update(SECRET_KEY=CONFIG["db-service"]["session_key"])

# app keeps one instance of the db manager
# TODO: this may be replaced
data_mgr = DataManager()

app.layout = dbc.Container(
    [
        # top_navbar,
        # layout_upload.upload_form_layout,
        html.Div(id="temp-output", className="mt-4"),  # TODO: temp
        html.Br(),
        layout_landing.layout,
        html.Br(),
        layout_experiment.layout,
        dcc.Store(id="id-data-exp"),
        dcc.Store(id="id-data-structure"),
        dcc.Store(id="id-experiment-selected"),
    ],
    fluid=True,
)


@app.callback(
    Output("id-button-upload-data-info", "children"),
    # Output("id-button-upload-data", "style"),
    Output("id-data-exp", "data"),
    Input("id-button-upload-data", "contents"),
    State("id-button-upload-data", "filename"),
    State("id-button-upload-data", "last_modified"),
)
def on_upload_experiment_file(dash_upload_string_contents, filename, last_modified):
    if not dash_upload_string_contents:
        # TODO add the alert
        return "No file uploaded.", no_update
    else:
        base64_encoded_string = parser.decode_base64_binary_string_to_base64_bytes(dash_upload_string_contents)

        df = parser.decode_csv_file_base64_string_to_dataframe(base64_encoded_string)
        rows, cols = df.shape
        info = (
            f"Uploaded File: {filename} --- "
            # f"Size:{parser.get_file_size(base64_encoded_bytes)} --- "
            f"Rows:{rows} "
            f"Columns:{cols}"
        )

        return info, base64_encoded_string


@app.callback(
    Output("id-button-upload-structure-info", "children"),
    # Output("id-button-upload-structure", "style"),
    Output("id-data-structure", "data"),
    Input("id-button-upload-structure", "contents"),
    State("id-button-upload-structure", "filename"),
    State("id-button-upload-structure", "last_modified"),
)
def on_upload_structure_file(dash_upload_string_contents, filename, last_modified):
    if not dash_upload_string_contents:
        # TODO add the alert
        return "No file uploaded.", no_update
    else:
        base64_encoded_string = parser.decode_base64_binary_string_to_base64_bytes(dash_upload_string_contents)

        info = (
            f"Uploaded File: {filename}  "
            # f"Size:{parser.get_file_size(base64_encoded_string)}"
        )

        return info, base64_encoded_string


@app.callback(
    Output("temp-output", "children"),
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
    geometry_content_base64_encoded_string,
    experiment_base64_encoded_string,
):
    if ctx.triggered_id == "id-button-submit":
        # TODO: remove this later, this is just for debugging
        # df = parser.decode_csv_file_base64_string_to_dataframe(experiment_base64_encoded_string)
        # rows, cols = df.shape

        # TODO: fix the splitting here
        # sub_cas_split = substrate_cas.split(';')
        # substrate_cas_numbers = [item for item in sub_cas_split if item]
        #
        # product_cas_split = product_cas.split(';')
        # product_cas_numbers = [item for item in product_cas_split if item]

        # TODO: verify the CAS numbers somewhere or in another callback
        # verify the experiment here or on another callback
        # file_bytes = base64.b64decode(content_string)

        index = data_mgr.add_experiment_from_ui(
            user_id="some_user_name",
            experiment_name=experiment_name,
            experiment_date=experiment_date,
            substrate_cas_number=substrate_cas,
            product_cas_number=product_cas,
            assay=assay,
            mutagenesis_method=epr,
            experiment_content_base64_string=experiment_base64_encoded_string,
            geometry_content_base64_string=geometry_content_base64_encoded_string,
        )

        # you can verify the information here
        # exp = data_mgr.get_experiment(index)
        # TODO: return a success alert here
        info = f"Experiment {index} added."
        return info
    else:
        return no_update


@app.callback(
    Output("id-table-top-variants", "rowData"),
    Output("id-experiment-name", "children"),
    Output("id-experiment-sequence", "children"),
    Output("id-experiment-mutagenesis-method", "children"),
    Output("id-experiment-date", "children"),
    Output("id-experiment-plate-count", "children"),
    Output("id-experiment-sub-cas", "children"),
    Output("id-experiment-product-cas", "children"),
    Output("id-experiment-assay", "children"),
    Output("id-viewer", "data"),
    Output("id-list-plates", "options"),
    Output("id-list-plates", "value"),
    Output("id-list-cas-numbers", "options"),
    Output("id-list-cas-numbers", "value"),
    Output("id-list-properties", "options"),
    Output("id-list-properties", "value"),
    Output("id-experiment-heatmap", "figure"),
    Input("id-button-temp-use", "n_clicks"),
    Input("id-experiment-selected", "data"),
    prevent_initial_call=True,
)
def on_load_experiment_dashboard(n_clicks, experiment_id):
    # TODO: remove this button trigger and replace with table click trigger adn input experiment ID
    if ctx.triggered_id == "id-button-temp-use":
        # TODO: load from file for now
        # data_mgr.add_experiment(experiment_ep_example)
        exp = data_mgr.get_experiment(experiment_id)

        # viewer data
        # TODO : this needs to be moved out of here so it can pickup the file format
        # in the component. Hardcoded here for now.
        # bytes = parser.decode_base64_string_to_base64_bytes(exp.geometry_base64_string)
        # try:
        if exp.geometry_file_path:
            pdb_cif = molstar_helper.parse_molecule(exp.geometry_file_path, fmt="cif")
        else:
            pdb_cif = molstar_helper.parse_molecule(exp.geometry_base64_bytes, fmt="cif")

        # load the dropdown for the plots with default values
        default_plate = exp.plates[0]
        default_cas = exp.cas_unique_values[0]
        default_stat = gs.stat_list[0]
        stat_heatmap = graphs.creat_heatmap(exp.data_df, default_plate, default_stat, default_cas)
        # except Exception:
        #    raise PreventUpdate

        return (
            exp.data_df.to_dict("records"),
            exp.experiment_name,
            exp.parent_sequence,
            exp.mutagenesis_method,
            exp.experiment_time,
            exp.plates_count,
            exp.substrate_cas_number,
            exp.product_cas_number,
            exp.assay,
            pdb_cif,
            exp.plates,
            default_plate,
            exp.cas_unique_values,
            default_cas,
            gs.stat_list,
            gs.stat_list[0],
            stat_heatmap,
        )
    else:
        return no_update


@app.callback(
    Output("id-experiment-heatmap", "figure", allow_duplicate=True),
    Output("id-list-cas-numbers", "disabled"),
    Output("id-list-cas-numbers", "className"),
    Input("id-experiment-selected", "data"),
    Input("id-list-plates", "value"),
    Input("id-list-cas-numbers", "value"),
    Input("id-list-properties", "value"),
    prevent_initial_call=True,
)
def on_heatmap_selection(experiment_id, selected_plate, selected_cas_number, selected_stat_property):
    # TODO: transfer of data here
    exp = data_mgr.get_experiment(experiment_id)

    show_cas_numbers = selected_stat_property == gs.stat_list[0]

    stat_heatmap = graphs.creat_heatmap(
        exp.data_df, plate_number=selected_plate, property_stat=selected_stat_property, cas_number=selected_cas_number
    )
    if not show_cas_numbers:
        class_name = "opacity-50 text-secondary dbc"
    else:
        class_name = "dbc"
    return stat_heatmap, not show_cas_numbers, class_name


@app.callback(
    Output("selected-row-value", "children"),
    Input("id-table-top-variants", "selectedRows"),
    prevent_initial_call=True,
)
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


@app.callback(
    Output("id-table-all-experiments", "rowData"),
    Output("id-lab-experiment-count", "children"),
    Output("id-lab-experiment-all-cas", "children"),
    Input("id-table-all-experiments", "columnDefs"),
    # prevent_initial_call=True,
)
def load_landing_page(temp_text):
    df = data_mgr.get_lab_experiments_with_meta_data()
    rows, columns = df.shape
    unique_call_values = set(df["sub_cas"].str.split(", ").explode())
    sorted_string = ", ".join(map(str, sorted(unique_call_values)))
    return (
        df.to_dict("records"),
        rows,
        sorted_string,  # comma separated string
    )


@app.callback(
    Output("id-experiment-selected", "data"),
    Output("id-selected-row-info", "children"),
    Output("id-button-delete-experiment", "disabled"),
    Output("id-button-show-experiment", "disabled"),
    Input("id-table-all-experiments", "selectedRows"),
    prevent_initial_call=True,
)
def update_ui(selected_rows):
    # Display selected row info
    experiment_id = no_update
    if selected_rows and len(selected_rows) == 1:
        selected_row_info = f"Selected Row: {selected_rows[0]}"
        experiment_id = selected_rows[0]["experiment_id"]
    elif selected_rows and len(selected_rows) > 1:
        selected_row_info = f"Selected {len(selected_rows)} rows."
    else:
        selected_row_info = "No row selected."

    # Manage button states based on number of selected rows
    delete_btn_disabled = len(selected_rows) == 0 if selected_rows else True
    show_btn_disabled = not (selected_rows and len(selected_rows) == 1)
    return experiment_id, selected_row_info, delete_btn_disabled, show_btn_disabled


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
