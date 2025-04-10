import math

import dash_bootstrap_components as dbc
import dash_molstar
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
from dash_molstar.utils import molstar_helper

from levseq_dash.app import column_definitions as cd
from levseq_dash.app import global_strings as gs
from levseq_dash.app import (
    graphs,
    settings,
    utils,
    utils_seq_alignment,
    vis,
)
from levseq_dash.app.data_manager import DataManager
from levseq_dash.app.layout import (
    layout_bars,
    layout_experiment,
    layout_landing,
    layout_matching_sequences,
    layout_upload,
)
from levseq_dash.app.sequence_aligner import bio_python_pairwise_aligner

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
            [html.Div([layout_bars.get_sidebar(), html.Div(id="id-page-content", className="content")])],
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
    elif pathname == "/explore-sequences":
        return layout_matching_sequences.get_seq_align_layout()
    else:
        return html.Div([html.H2("Page not found!")])


# -------------------------------
#   Lab Landing Page (all experiments) related
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


@app.callback(
    Output("id-experiment-selected", "data"),
    Output("id-button-delete-experiment", "disabled"),
    Output("id-button-goto-experiment", "disabled"),
    # Output("id-selected-row-info", "children"),
    Input("id-table-all-experiments", "selectedRows"),
    prevent_initial_call=True,
)
def update_landing_page_buttons(selected_rows):
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


# -------------------------------
#   Uploading Experiment related
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


# ----------------------------------------
#   Matching Sequences Dashboard related
# ----------------------------------------
@app.callback(
    Output("id-table-matched-sequences", "rowData"),
    Output("id-table-matched-sequences-exp-hot-cold-data", "rowData"),
    Output("id-div-matched-sequences-info", "children"),
    Output("id-div-seq-alignment-results", "style"),
    Input("id-button-run-seq-matching", "n_clicks"),
    State("id-input-query-sequence", "value"),
    State("id-input-query-sequence-threshold", "value"),
    State("id-input-num-hot-cold", "value"),
    prevent_initial_call=True,
)
def on_load_matching_sequences(n_clicks, query_sequence, threshold, n_top_hot_cold):
    if n_clicks != 0 and ctx.triggered_id == "id-button-run-seq-matching":
        # get all the lab sequences
        all_lab_sequences = data_mgr.get_lab_sequences()

        # get the alignment and the base score
        lab_seq_match_data, base_score = bio_python_pairwise_aligner.get_alignments(
            query_sequence=query_sequence, threshold=float(threshold), targets=all_lab_sequences
        )

        n_matches = len(lab_seq_match_data)

        seq_match_row_data = list(dict())

        # for each matching experiment pull out it's metadata
        hot_cold_row_data = pd.DataFrame()
        for i in range(len(lab_seq_match_data)):
            # add experiment id
            exp_id = lab_seq_match_data[i][gs.cc_experiment_id]

            # get the experiment core data for the db
            exp = data_mgr.get_experiment(exp_id)

            # extract the top N (hot) and bottom N (cold) fitness values of this experiment
            hot_cold_spots_merged_df, hot_cold_residue_per_cas = exp.exp_hot_cold_spots(int(n_top_hot_cold))

            # add the experiment id to this data
            hot_cold_spots_merged_df[gs.cc_experiment_id] = exp_id

            # concatenate this info with the rest of the hot and cold spot data
            hot_cold_row_data = pd.concat([hot_cold_row_data, hot_cold_spots_merged_df], ignore_index=True)

            # expand the data of each row per CAS - request by PI
            seq_match_row_data = utils_seq_alignment.gather_seq_alignment_data_per_cas(
                df_hot_cold_residue_per_cas=hot_cold_residue_per_cas,
                seq_match_data=lab_seq_match_data[i],
                exp_meta_data=exp.exp_meta_data_to_dict(),
                seq_match_row_data=seq_match_row_data,
            )

        info = f"# Matched Sequences: {n_matches}"
        return seq_match_row_data, hot_cold_row_data.to_dict("records"), info, vis.display_block

    raise PreventUpdate


@app.callback(
    Output("id-div-selected-matched-sequence-info", "children"),
    Output("id-viewer-selected-seq-matched-protein", "children"),
    Input("id-table-matched-sequences", "selectedRows"),
    prevent_initial_call=True,
)
def display_selected_matching_sequences_protein_visualization(selected_rows):
    if selected_rows:
        # extract the info from the table
        substitutions = f"{selected_rows[0][gs.cc_seq_alignment_mismatches]}"
        hot_spots = f"{selected_rows[0][gs.cc_hot_indices_per_cas]}"
        cold_spots = f"{selected_rows[0][gs.cc_cold_indices_per_cas]}"
        experiment_id = selected_rows[0][gs.cc_experiment_id]

        # get the experiment info from the db
        exp = data_mgr.get_experiment(experiment_id)
        geometry_file = exp.geometry_file_path

        # if there is no geometry for the file ignore it
        if geometry_file:
            # gather the rendering components per the indices
            list_of_rendered_components = vis.get_molstar_rendered_components(
                hot_residue_indices_list=hot_spots,
                cold_residue_indices_list=cold_spots,
                substitution_residue_list=substitutions,
            )

            # set up the molecular viewer and render it
            pdb_cif = molstar_helper.parse_molecule(
                geometry_file,
                component=list_of_rendered_components,
                preset={"kind": "empty"},
                fmt="cif",
            )
            viewer = [
                dash_molstar.MolstarViewer(
                    data=pdb_cif,
                    style={"width": "auto", "height": vis.seq_match_protein_viewer_height},
                    # focus=analyse,
                )
            ]
            notes = f"""
                     **ExperimentID:** {experiment_id}
                     **CAS:** {selected_rows[0][gs.c_cas]}
                    """
        else:
            viewer = no_update
            notes = f"""
                     **ExperimentID:** {experiment_id}
                     **CAS:** {selected_rows[0][gs.c_cas]}
                     **No geometry file was found for the selected experiment:**
                    """

        return notes, viewer
    else:
        raise PreventUpdate


@app.callback(
    Output("id-table-matched-sequences-exp-hot-cold-data", "exportDataAsCsv"),
    Output("id-table-matched-sequences-exp-hot-cold-data", "csvExportParams"),
    Input("id-button-download-hot-cold-results", "n_clicks"),
    State("id-button-download-hot-cold-results-options", "value"),
    prevent_initial_call=True,
    # in case the download takes time this will disable the button
    # so multiple cliks don't happen
    running=[(Output("id-button-download-hot-cold-results", "disabled"), True, False)],  # requires the latest Dash 2.16
)
def export_data_as_csv_jiq(n_clicks, option):
    return utils.export_data_as_csv(option, gs.filename_download_residue_info)


# -------------------------------
#   Experiment Dashboard related
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
    Output("id-table-exp-top-variants", "rowData"),
    Output("id-table-exp-top-variants", "columnDefs"),
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
    # slider setup
    Output("id-slider-ratio", "marks"),
    Output("id-slider-ratio", "max"),
    Output("id-list-cas-numbers-residue-highlight", "options"),
    Output("id-list-cas-numbers-residue-highlight", "value"),
    # Output("id-store-heatmap-data", "data"),
    # Inputs
    Input("url", "pathname"),
    State("id-experiment-selected", "data"),
    prevent_initial_call=True,
)
def load_experiment_page(pathname, experiment_id):
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
        columnDefs_with_ratio = cd.get_top_variant_column_defs(df_filtered_with_ratio)

        # creat the ranking plot with default values
        # rank plot uses the ratio data to color
        fig_experiment_rank_plot = graphs.creat_rank_plot(
            df=df_filtered_with_ratio,
            plate_number=default_plate,
            cas_number=default_cas,
        )

        # set up the slider
        # get the max value of the ratio column, round up
        max_value = np.ceil(df_filtered_with_ratio["ratio"].max())
        # generate the slider marks based on the max value
        # make sure the value is an int
        slider_marks = utils.generate_slider_marks_dict(int(max_value))

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
            # -------------------------------
            # residue highlight slider
            # --------------------------------
            slider_marks,
            max_value,
            exp.unique_cas_in_data,  # list of cas values
            default_cas,  # default Cas
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
    State("id-table-exp-top-variants", "rowData"),  # TODO: does this have a performance hit?
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
    State("id-table-exp-top-variants", "rowData"),  # TODO: does this have a performance hit?
    # State("id-store-heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_rank_plot(selected_plate, selected_cas_number, rowData):
    # TODO: does this have a performance hit? if so we can just put the 3 columns in the user session
    df = pd.DataFrame(rowData)

    rank_plot = graphs.creat_rank_plot(df, plate_number=selected_plate, cas_number=selected_cas_number)
    return rank_plot


@app.callback(
    Output("id-viewer", "selection"),
    Output("id-viewer", "focus"),
    Input("id-table-exp-top-variants", "selectedRows"),
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
    Output("id-viewer", "selection", allow_duplicate=True),
    Output("id-viewer", "focus", allow_duplicate=True),
    Output("id-slider-ratio", "disabled"),
    Output("id-list-cas-numbers-residue-highlight", "disabled"),
    Input("id-switch-residue-view", "checked"),  # DMC
    # Input("id-switch-residue-view", "value"),  # DBC
    Input("id-slider-ratio", "value"),
    Input("id-list-cas-numbers-residue-highlight", "value"),
    State("id-table-exp-top-variants", "rowData"),
    prevent_initial_call=True,
)
def on_view_all_residue(view, slider_value, cas_value, rowData):
    # default the values
    sel = utils.reset_selection()
    foc = no_update
    enable_components = (not view) if view else no_update
    if view and rowData:
        df = pd.DataFrame(rowData)
        # filter by cas value
        if cas_value:
            df_cas = df[df[gs.c_cas] == cas_value]
        else:
            df_cas = df

        # apply the slider values
        delta = math.fabs(slider_value[0] - slider_value[1])
        if delta != 0:
            df_filtered = df_cas[df_cas["ratio"].between(slider_value[0], slider_value[1])]
            # extract the residue indices for the viewer
            residues = sorted(df_filtered[gs.c_substitutions].str.extractall(r"(\d+)")[0].unique().tolist())
            # set up the protein viewer selection and focus
            if len(residues) != 0:
                sel, foc = utils.get_selection_focus(residues, analyse=False)

    return sel, foc, enable_components, enable_components


@app.callback(
    Output("id-sidebar", "className"),
    Input("id-menu-icon", "n_clicks"),
    State("id-sidebar", "className"),
    prevent_initial_call=True,
)
def toggle_sidebar(toggle_clicks, sidebar_class):
    if ctx.triggered_id == "id-menu-icon":
        if "expanded" in sidebar_class:
            return "thin-sidebar collapsed"
        else:
            return "thin-sidebar expanded"

    return sidebar_class  # no changes


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
