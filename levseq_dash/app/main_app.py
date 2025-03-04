import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

from levseq_dash.app import (
    components,
    graphs,
    layout_bars,
    layout_experiment,
    layout_landing,
    layout_upload,
    settings,
    utils,
    vis,
)
from levseq_dash.app import global_strings as gs
from levseq_dash.app.data_manager import DataManager

# Initialize the app
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(
    __name__,
    title=gs.web_title,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.FLATLY, dbc_css, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

# VERY important line of code for running with gunicorn
# you run the 'server' not the 'app'. VS. you run the 'app' with uvicorn
server = app.server

load_figure_template(gs.dbc_template_name)

app.server.config.update(SECRET_KEY=settings.load_config()["db-service"]["session_key"])

# app keeps one instance of the db manager
# TODO: this may be replaced
data_mgr = DataManager()

app.layout = dbc.Container(
    [
        layout_bars.get_navbar(),
        dbc.Row(
            [
                # Left column with a logo
                dbc.Col(
                    layout_bars.get_sidebar(),
                    width=2,
                    style={"border-right": "1px solid #dee2e6"},
                ),
                # Main content
                dbc.Col(
                    html.Div(id="id-page-content"),
                    width=10,
                    style=vis.border_column,
                ),
            ],
            # className="g-0",
        ),
        # stores
        dcc.Store(id="id-exp-upload-csv"),
        dcc.Store(id="id-exp-upload-structure"),
        dcc.Store(id="id-experiment-selected"),
        dcc.Store(id="id-store-heatmap-data"),
        dcc.Location(id="url", refresh=False),
    ],
    fluid=True,
)


@app.callback(Output("id-page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/":
        return layout_landing.get_landing_page()
    elif pathname == "/experiment":
        return layout_experiment.get_experiment_page()
    elif pathname == "/upload":
        return layout_upload.layout
    else:
        return html.Div([html.H2("Page not found!")])


# -------------------------------
#   Lab Landing Page (all experiments)
# -------------------------------
@app.callback(
    Output("id-table-all-experiments", "rowData"),
    Output("id-lab-experiment-count", "children"),
    Output("id-lab-experiment-all-cas", "children"),
    Input("id-table-all-experiments", "columnDefs"),
    # prevent_initial_call=True,
)
def load_landing_page(temp_text):
    list_of_all_lab_experiments_with_meta = data_mgr.get_lab_experiments_with_meta_data()

    # extract all the uniques substrate cas in the projects
    all_cas = utils.extract_all_unique_cas_from_lab_data(list_of_all_lab_experiments_with_meta)
    number_of_experiments = len(list_of_all_lab_experiments_with_meta)
    return (
        list_of_all_lab_experiments_with_meta,
        number_of_experiments,  # number of experiments
        all_cas,  # for lab dashboard stats
    )


# -------------------------------
#   Uploading Experiment
# -------------------------------
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
    Output("id-button-upload-data-info", "children"),
    # Output("id-button-upload-data", "style"),
    Output("id-exp-upload-csv", "data"),
    Input("id-button-upload-data", "contents"),
    State("id-button-upload-data", "filename"),
    State("id-button-upload-data", "last_modified"),
)
def on_upload_experiment_file(dash_upload_string_contents, filename, last_modified):
    if not dash_upload_string_contents:
        # TODO add the alert
        return "No file uploaded.", no_update
    else:
        base64_encoded_string = utils.decode_dash_upload_data_to_base64_encoded_string(dash_upload_string_contents)

        df = utils.decode_csv_file_base64_string_to_dataframe(base64_encoded_string)
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
    Output("id-exp-upload-structure", "data"),
    Input("id-button-upload-structure", "contents"),
    State("id-button-upload-structure", "filename"),
    State("id-button-upload-structure", "last_modified"),
)
def on_upload_structure_file(dash_upload_string_contents, filename, last_modified):
    if not dash_upload_string_contents:
        # TODO add the alert
        return "No file uploaded.", no_update
    else:
        base64_encoded_string = utils.decode_dash_upload_data_to_base64_encoded_string(dash_upload_string_contents)

        info = (
            f"Uploaded File: {filename}  "
            # f"Size:{parser.get_file_size(base64_encoded_string)}"
        )

        return info, base64_encoded_string


@app.callback(
    Output("id-alert-upload", "children"),
    Output("id-alert-upload", "is_open"),
    Input("id-button-submit", "n_clicks"),
    State("id-input-experiment-name", "value"),
    State("id-input-experiment-date", "date"),
    State("id-input-substrate-cas", "value"),
    State("id-input-product-cas", "value"),
    State("id-list-assay", "value"),
    State("id-radio-epr", "value"),
    State("id-exp-upload-structure", "data"),
    State("id-exp-upload-csv", "data"),
    prevent_initial_call=True,
)
def on_submit_experiment(
    n_clicks,
    experiment_name,
    experiment_date,
    substrate_cas,
    product_cas,
    assay,
    mutagenesis_method,
    geometry_content_base64_encoded_string,
    experiment_content_base64_encoded_string,
):
    if n_clicks > 0 and ctx.triggered_id == "id-button-submit":
        # TODO: verify the CAS numbers somewhere or in another callback

        experiment_id = data_mgr.add_experiment_from_ui(
            user_id="some_user_name",
            experiment_name=experiment_name,
            experiment_date=experiment_date,
            substrate_cas_number=substrate_cas,
            product_cas_number=product_cas,
            assay=assay,
            mutagenesis_method=mutagenesis_method,
            experiment_content_base64_string=experiment_content_base64_encoded_string,
            geometry_content_base64_string=geometry_content_base64_encoded_string,
        )

        # you can verify the information here
        # exp = data_mgr.get_experiment(index)
        # TODO: return a success alert here
        success = f"Experiment {experiment_id} has been added successfully!"
        return success, True
    else:
        raise PreventUpdate


# -------------------------------
#   Experiment Dashboard
# -------------------------------
@app.callback(
    Output("url", "pathname"),
    # this seems like a duplicate but adding this will actually
    # trigger the callback with the components in the layout
    Output("id-page-content", "children", allow_duplicate=True),
    Input("id-button-goto-experiment", "n_clicks"),
    # State("url", "pathname"),
    prevent_initial_call=True,
)
def redirect_to_experiment_page(n_clicks):
    if n_clicks != 0 and ctx.triggered_id == "id-button-goto-experiment":
        return "/experiment", layout_experiment.get_experiment_page()
    else:
        raise PreventUpdate


@app.callback(
    # Variant table
    Output("id-table-top-variants", "rowData"),
    Output("id-table-top-variants", "columnDefs"),
    # Protein
    Output("id-viewer", "data"),
    # Meta data
    Output("id-experiment-name", "children"),
    Output("id-experiment-sequence", "children"),
    Output("id-experiment-mutagenesis-method", "children"),
    Output("id-experiment-date", "children"),
    Output("id-experiment-upload", "children"),
    Output("id-experiment-plate-count", "children"),
    Output("id-experiment-file-cas", "children"),
    Output("id-experiment-sub-cas", "children"),
    Output("id-experiment-product-cas", "children"),
    Output("id-experiment-assay", "children"),
    # Heat map dropdowns options and defaults
    Output("id-list-plates", "options"),
    Output("id-list-plates", "value"),
    Output("id-list-cas-numbers", "options"),
    Output("id-list-cas-numbers", "value"),
    Output("id-list-properties", "options"),
    Output("id-list-properties", "value"),
    # Heat map figure
    Output("id-experiment-heatmap", "figure"),
    # Ranking plot dropdowns options and defaults
    Output("id-list-plates-ranking-plot", "options"),
    Output("id-list-plates-ranking-plot", "value"),
    Output("id-list-cas-numbers-ranking-plot", "options"),
    Output("id-list-cas-numbers-ranking-plot", "value"),
    # Ranking plot figure
    Output("id-experiment-ranking-plot", "figure"),
    # Output("id-store-heatmap-data", "data"),
    # Inputs
    Input("url", "pathname"),
    State("id-experiment-selected", "data"),
    prevent_initial_call=True,
)
def on_load_experiment_dashboard(pathname, experiment_id):
    if pathname == "/experiment":
        exp = data_mgr.get_experiment(experiment_id)

        # viewer data
        # TODO : this needs to be moved out of here so it can pickup the file format
        pdb_cif = utils.get_geometry_for_viewer(exp)

        # load the dropdown for the plots with default values
        default_plate = exp.plates[0]
        default_cas = exp.unique_cas_in_data[0]
        default_experiment_heatmap_properties_list = gs.experiment_heatmap_properties_list[0]

        # create the heatmap with default values
        fig_experiment_heatmap = graphs.creat_heatmap(
            df=exp.data_df,
            plate_number=default_plate,
            property=default_experiment_heatmap_properties_list,
            cas_number=default_cas,
        )

        # in order to color the fitness ratio I have to calculate the mean of the parents per cas per plate.
        # coloring only works if I add the column
        df_filtered_with_ratio = utils.calculate_group_mean_ratios_per_cas_and_plate(exp.data_df)
        columnDefs_with_ratio = components.get_top_variant_column_defs(df_filtered_with_ratio)

        # creat the ranking plot with default values
        # rank plot uses the ratio data to color
        fig_experiment_rank_plot = graphs.creat_rank_plot(
            df=df_filtered_with_ratio,
            plate_number=default_plate,
            cas_number=default_cas,
        )

        # heatmap_df = exp.data_df[[gs.c_cas, gs.c_plate, gs.c_well, gs.c_alignment_count,
        #                          gs.c_alignment_probability, gs.c_fitness_value]]
        # heatmap_json = heatmap_df.to_json(date_format='iso', orient='records')
        # Convert to JSON
        # json_data = json.dumps(exp.exp_to_dict(), indent=4)
        # json_data = json.dumps(exp, cls=CustomEncoder, indent=4)

        # exp_dict = json.loads(exp_json)
        # exp = Experiment.exp_from_dict(exp_dict)

        return (
            df_filtered_with_ratio.to_dict("records"),  # rowData
            columnDefs_with_ratio,
            pdb_cif,
            exp.experiment_name,
            exp.parent_sequence,
            exp.mutagenesis_method,
            exp.experiment_date,
            exp.upload_time_stamp,
            exp.plates_count,
            exp.unique_cas_in_data,
            exp.substrate_cas_number,
            exp.product_cas_number,
            exp.assay,
            # -------------------------------
            # heatmap dropdowns and figure
            # -------------------------------
            exp.plates,  # Heatmap:  list of plates
            default_plate,  # Heatmap:  default plate
            exp.unique_cas_in_data,  # Heatmap: list of cas values
            default_cas,  # Heatmap:  default Cas
            gs.experiment_heatmap_properties_list,  # Heatmap: property list
            gs.experiment_heatmap_properties_list[0],  # Heatmap: property default
            fig_experiment_heatmap,  # Heatmap: figure
            # -------------------------------
            # rank plot dropdowns and figure
            # --------------------------------
            exp.plates,  # rank plot:  list of plates
            default_plate,  # rank plot:  default plate
            exp.unique_cas_in_data,  # rank plot: list of cas values
            default_cas,  # rank plot:  default Cas
            fig_experiment_rank_plot,  # Heatmap: figure
        )
    else:
        return no_update


@app.callback(
    Output("id-experiment-heatmap", "figure", allow_duplicate=True),
    Output("id-list-cas-numbers", "disabled"),
    Output("id-list-cas-numbers", "className"),
    Input("id-list-plates", "value"),
    Input("id-list-cas-numbers", "value"),
    Input("id-list-properties", "value"),
    State("id-table-top-variants", "rowData"),  # TODO: does this have a performance hit?
    # State("id-store-heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_heatmap(selected_plate, selected_cas_number, selected_stat_property, rowData):
    # TODO: does this have a performance hit? if so we can just put the 3 columns in the user session
    df = pd.DataFrame(rowData)

    show_cas_numbers = selected_stat_property == gs.experiment_heatmap_properties_list[0]

    stat_heatmap = graphs.creat_heatmap(
        df, plate_number=selected_plate, property=selected_stat_property, cas_number=selected_cas_number
    )
    if not show_cas_numbers:
        class_name = "opacity-50 text-secondary dbc"
    else:
        class_name = "dbc"
    return stat_heatmap, not show_cas_numbers, class_name


@app.callback(
    Output("id-experiment-ranking-plot", "figure", allow_duplicate=True),
    Input("id-list-plates-ranking-plot", "value"),
    Input("id-list-cas-numbers-ranking-plot", "value"),
    State("id-table-top-variants", "rowData"),  # TODO: does this have a performance hit?
    # State("id-store-heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_rank_plot(selected_plate, selected_cas_number, rowData):
    # TODO: does this have a performance hit? if so we can just put the 3 columns in the user session
    df = pd.DataFrame(rowData)

    rank_plot = graphs.creat_rank_plot(df, plate_number=selected_plate, cas_number=selected_cas_number)
    return rank_plot


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
        residues = utils.gather_residues_from_selection(selected_rows)

        # residue = list(range(1, 26)) # you can provide a list
        if len(residues) != 0:
            sel, foc = utils.get_selection_focus(residues)
            return sel, foc

    raise PreventUpdate


@app.callback(
    Output("id-experiment-selected", "data"),
    Output("id-button-delete-experiment", "disabled"),
    Output("id-button-goto-experiment", "disabled"),
    # Output("id-selected-row-info", "children"),
    Input("id-table-all-experiments", "selectedRows"),
    prevent_initial_call=True,
)
def update_ui(selected_rows):
    # Display selected row info
    if not selected_rows:
        raise PreventUpdate

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
    return experiment_id, delete_btn_disabled, show_btn_disabled  # ,selected_row_info


@app.callback(
    Output("id-viewer", "selection", allow_duplicate=True),
    Output("id-viewer", "focus", allow_duplicate=True),
    # Input("id-switch-residue-view", "checked"), #DMC
    Input("id-switch-residue-view", "value"),  # DBC
    State("id-table-top-variants", "rowData"),
    prevent_initial_call=True,
)
def on_view_all_residue(view, rowData):
    if view and rowData:
        df = pd.DataFrame(rowData)
        residues = sorted(df[gs.c_substitutions].str.extractall(r"(\d+)")[0].unique().tolist())
        if len(residues) != 0:
            sel, foc = utils.get_selection_focus(residues, analyse=False)
    else:
        sel = utils.reset_selection()
        foc = no_update

    return sel, foc


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
