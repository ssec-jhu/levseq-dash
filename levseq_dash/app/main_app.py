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
from levseq_dash.app import graphs, settings, vis
from levseq_dash.app.data_manager import DataManager
from levseq_dash.app.layout import (
    layout_bars,
    layout_experiment,
    layout_landing,
    layout_matching_sequences,
    layout_upload,
)
from levseq_dash.app.sequence_aligner import bio_python_pairwise_aligner
from levseq_dash.app.utils import u_protein_viewer, u_reaction, u_seq_alignment, utils

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
    # image of all the substrate and products in the lab
    Output("id-lab-substrate", "src"),
    Output("id-lab-product", "src"),
    Input("id-table-all-experiments", "columnDefs"),
)
def load_landing_page(temp_text):
    list_of_all_lab_experiments_with_meta = data_mgr.get_lab_experiments_with_meta_data()

    all_substrate, all_product = utils.extract_all_substrate_product_smiles_from_lab_data(
        list_of_all_lab_experiments_with_meta
    )

    # it's Ok if the substrate_svg_image or product_svg_image are None to any issues in the smiles
    # UI will just not have an image, but won't fail
    substrate_svg_image = u_reaction.create_mols_grid(all_substrate)
    product_svg_image = u_reaction.create_mols_grid(all_product)
    return (
        list_of_all_lab_experiments_with_meta,
        substrate_svg_image,
        product_svg_image,
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
    State("id-input-substrate", "value"),
    State("id-input-product", "value"),
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
    substrate,
    product,
    assay,
    mutagenesis_method,
    geometry_content_base64_encoded_string,
    experiment_content_base64_encoded_string,
):
    if n_clicks > 0 and ctx.triggered_id == "id-button-submit":
        # TODO: verify the smiles numbers somewhere or in another callback

        experiment_id = data_mgr.add_experiment_from_ui(
            user_id="some_user_name",
            experiment_name=experiment_name,
            experiment_date=experiment_date,
            substrate=substrate,
            product=product,
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
            hot_cold_spots_merged_df, hot_cold_residue_per_smiles = exp.exp_hot_cold_spots(int(n_top_hot_cold))

            # add the experiment id to this data
            hot_cold_spots_merged_df[gs.cc_experiment_id] = exp_id

            # concatenate this info with the rest of the hot and cold spot data
            hot_cold_row_data = pd.concat([hot_cold_row_data, hot_cold_spots_merged_df], ignore_index=True)

            # expand the data of each row per smiles - request by PI
            seq_match_row_data = u_seq_alignment.gather_seq_alignment_data_per_smiles(
                df_hot_cold_residue_per_smiles=hot_cold_residue_per_smiles,
                seq_match_data=lab_seq_match_data[i],
                exp_meta_data=exp.exp_meta_data_to_dict(),
                seq_match_row_data=seq_match_row_data,
            )

        info = f"# Matched Sequences: {n_matches}"
        return seq_match_row_data, hot_cold_row_data.to_dict("records"), info, vis.display_block

    raise PreventUpdate


@app.callback(
    Output("id-viewer-selected-seq-matched-protein", "children"),
    Output("id-selected-seq-matched-reaction-image", "src"),
    Output("id-selected-seq-matched-substrate", "children"),
    Output("id-selected-seq-matched-product", "children"),
    Input("id-table-matched-sequences", "selectedRows"),
    prevent_initial_call=True,
)
def display_selected_matching_sequences_protein_visualization(selected_rows):
    if selected_rows and len(selected_rows) > 0:
        # extract the info from the table
        substitutions = f"{selected_rows[0][gs.cc_seq_alignment_mismatches]}"
        hot_spots = f"{selected_rows[0][gs.cc_hot_indices_per_smiles]}"
        cold_spots = f"{selected_rows[0][gs.cc_cold_indices_per_smiles]}"
        experiment_id = selected_rows[0][gs.cc_experiment_id]
        experiment_smiles = selected_rows[0][gs.c_smiles]
        # TODO: this should not be a list, where is it getting a list??
        substrate = selected_rows[0][gs.cc_substrate][0]
        product = selected_rows[0][gs.cc_product][0]

        # get the experiment info from the db
        exp = data_mgr.get_experiment(experiment_id)
        geometry_file = exp.geometry_file_path

        svg_src_image = u_reaction.create_reaction_image(substrate, product)

        # if there is no geometry for the file ignore it
        if geometry_file:
            # gather the rendering components per the indices
            list_of_rendered_components = u_protein_viewer.get_molstar_rendered_components_seq_alignment(
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
        else:
            # if something goes down with the geometry file, it will still show everything else
            viewer = no_update
        return (
            viewer,
            svg_src_image,
            substrate,
            product,
        )
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
    # -------------------------------
    # Top variant table
    # -------------------------------
    Output("id-table-exp-top-variants", "rowData"),
    Output("id-table-exp-top-variants", "columnDefs"),
    # -------------------------------
    # Protein viewer
    # -------------------------------
    Output("id-viewer", "data"),
    # -------------------------------
    # Meta data
    # -------------------------------
    Output("id-experiment-name", "children"),
    Output("id-experiment-sequence", "children"),
    Output("id-experiment-mutagenesis-method", "children"),
    Output("id-experiment-date", "children"),
    Output("id-experiment-upload", "children"),
    Output("id-experiment-plate-count", "children"),
    Output("id-experiment-file-smiles", "children"),
    Output("id-experiment-substrate", "children"),
    Output("id-experiment-product", "children"),
    Output("id-experiment-assay", "children"),
    # -------------------------------
    # heatmap dropdowns and figure
    # -------------------------------
    Output("id-list-plates", "options"),
    Output("id-list-plates", "value"),
    Output("id-list-smiles", "options"),
    Output("id-list-smiles", "value"),
    Output("id-list-properties", "options"),
    Output("id-list-properties", "value"),
    Output("id-experiment-heatmap", "figure"),
    # -------------------------------
    # rank plot dropdowns and figure
    # --------------------------------
    Output("id-list-plates-ranking-plot", "options"),
    Output("id-list-plates-ranking-plot", "value"),
    Output("id-list-smiles-ranking-plot", "options"),
    Output("id-list-smiles-ranking-plot", "value"),
    Output("id-experiment-ranking-plot", "figure"),
    # -------------------------------
    # residue highlight slider
    # --------------------------------
    Output("id-slider-ratio", "marks"),
    Output("id-slider-ratio", "max"),
    Output("id-list-smiles-residue-highlight", "options"),
    Output("id-list-smiles-residue-highlight", "value"),
    # -------------------------------
    # related sequences
    # --------------------------------
    Output("id-input-exp-related-variants-query-sequence", "children"),
    # -------------------------------
    # reaction
    # --------------------------------
    Output("id-experiment-reaction-image", "src"),
    # Output("id-store-heatmap-data", "data"),
    # --------------------------------
    # Inputs
    # --------------------------------
    Input("url", "pathname"),
    State("id-experiment-selected", "data"),
    prevent_initial_call=True,
)
def load_experiment_page(pathname, experiment_id):
    if pathname == "/experiment":
        exp = data_mgr.get_experiment(experiment_id)

        # viewer data
        # TODO : this needs to be moved out of here so it can pickup the file format
        pdb_cif = u_protein_viewer.get_geometry_for_viewer(exp)

        # load the dropdown for the plots with default values
        default_plate = exp.plates[0]
        default_smiles = exp.unique_smiles_in_data[0]
        default_experiment_heatmap_properties_list = gs.experiment_heatmap_properties_list[0]
        unique_smiles_in_data = "; ".join(exp.unique_smiles_in_data)

        # create the heatmap with default values
        fig_experiment_heatmap = graphs.creat_heatmap(
            df=exp.data_df,
            plate_number=default_plate,
            property=default_experiment_heatmap_properties_list,
            smiles=default_smiles,
        )

        # in order to color the fitness ratio I have to calculate the mean of the parents per smiles per plate.
        # coloring only works if I add the column
        df_filtered_with_ratio = utils.calculate_group_mean_ratios_per_smiles_and_plate(exp.data_df)
        columnDefs_with_ratio = cd.get_top_variant_column_defs(df_filtered_with_ratio)

        # creat the ranking plot with default values
        # rank plot uses the ratio data to color
        fig_experiment_rank_plot = graphs.creat_rank_plot(
            df=df_filtered_with_ratio,
            plate_number=default_plate,
            smiles=default_smiles,
        )

        # set up the slider
        # get the max value of the ratio column, round up
        max_value = np.ceil(df_filtered_with_ratio["ratio"].max())
        # generate the slider marks based on the max value
        # make sure the value is an int
        slider_marks = utils.generate_slider_marks_dict(int(max_value))

        # heatmap_df = exp.data_df[[gs.c_smiles, gs.c_plate, gs.c_well, gs.c_alignment_count,
        #                          gs.c_alignment_probability, gs.c_fitness_value]]
        # heatmap_json = heatmap_df.to_json(date_format='iso', orient='records')
        # Convert to JSON
        # json_data = json.dumps(exp.exp_to_dict(), indent=4)
        # json_data = json.dumps(exp, cls=CustomEncoder, indent=4)

        # exp_dict = json.loads(exp_json)
        # exp = Experiment.exp_from_dict(exp_dict)
        # TODO: fix this list issue
        substrate = exp.substrate[0]
        product = exp.product[0]
        svg_src_image = u_reaction.create_reaction_image(substrate, product)

        return (
            # -------------------------------
            # Top variant table
            # -------------------------------
            df_filtered_with_ratio.to_dict("records"),  # rowData
            columnDefs_with_ratio,
            # -------------------------------
            # Protein viewer
            # -------------------------------
            pdb_cif,
            # -------------------------------
            # Meta data
            # -------------------------------
            exp.experiment_name,
            exp.parent_sequence,
            exp.mutagenesis_method,
            exp.experiment_date,
            exp.upload_time_stamp,
            exp.plates_count,
            unique_smiles_in_data,
            exp.substrate,
            exp.product,
            exp.assay,
            # -------------------------------
            # heatmap dropdowns and figure
            # -------------------------------
            exp.plates,  # Heatmap:  list of plates
            default_plate,  # Heatmap:  default plate
            exp.unique_smiles_in_data,  # Heatmap: list of smiles values
            default_smiles,  # Heatmap:  default smiles
            gs.experiment_heatmap_properties_list,  # Heatmap: property list
            gs.experiment_heatmap_properties_list[0],  # Heatmap: property default
            fig_experiment_heatmap,  # Heatmap: figure
            # -------------------------------
            # rank plot dropdowns and figure
            # --------------------------------
            exp.plates,  # rank plot:  list of plates
            default_plate,  # rank plot:  default plate
            exp.unique_smiles_in_data,  # rank plot: list of smiles values
            default_smiles,  # rank plot:  default smiles
            fig_experiment_rank_plot,  # Heatmap: figure
            # -------------------------------
            # residue highlight slider
            # --------------------------------
            slider_marks,
            max_value,
            exp.unique_smiles_in_data,  # list of smiles values
            default_smiles,  # default smiles
            # -------------------------------
            # related sequences
            # --------------------------------
            exp.parent_sequence,
            # -------------------------------
            # reaction
            # --------------------------------
            svg_src_image,
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("id-experiment-heatmap", "figure", allow_duplicate=True),
    Output("id-list-smiles", "disabled"),
    Output("id-list-smiles", "className"),
    Input("id-list-plates", "value"),
    Input("id-list-smiles", "value"),
    Input("id-list-properties", "value"),
    State("id-table-exp-top-variants", "rowData"),  # TODO: does this have a performance hit?
    # State("id-store-heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_heatmap(selected_plate, selected_smiles, selected_stat_property, rowData):
    # TODO: does this have a performance hit? if so we can just put the 3 columns in the user session
    df = pd.DataFrame(rowData)

    show_smiles = selected_stat_property == gs.experiment_heatmap_properties_list[0]

    stat_heatmap = graphs.creat_heatmap(
        df, plate_number=selected_plate, property=selected_stat_property, smiles=selected_smiles
    )
    if not show_smiles:
        class_name = "opacity-50 text-secondary dbc"
    else:
        class_name = "dbc"
    return stat_heatmap, not show_smiles, class_name


@app.callback(
    Output("id-experiment-ranking-plot", "figure", allow_duplicate=True),
    Input("id-list-plates-ranking-plot", "value"),
    Input("id-list-smiles-ranking-plot", "value"),
    State("id-table-exp-top-variants", "rowData"),  # TODO: does this have a performance hit?
    # State("id-store-heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_rank_plot(selected_plate, selected_smiles, rowData):
    # TODO: does this have a performance hit? if so we can just put the 3 columns in the user session
    df = pd.DataFrame(rowData)

    rank_plot = graphs.creat_rank_plot(df, plate_number=selected_plate, smiles=selected_smiles)
    return rank_plot


@app.callback(
    Output("id-viewer", "selection"),
    Output("id-viewer", "focus"),
    Input("id-table-exp-top-variants", "selectedRows"),
    prevent_initial_call=True,
)
def focus_select_output(selected_rows):
    if selected_rows:
        # residues = utils.gather_residues_from_selection(selected_rows)
        residues = utils.extract_all_indices(f"{selected_rows[0][gs.c_substitutions]}")
        if len(residues) != 0:
            sel, foc = u_protein_viewer.get_selection_focus(residues)
            return sel, foc

    raise PreventUpdate


@app.callback(
    Output("id-viewer", "selection", allow_duplicate=True),
    Output("id-viewer", "focus", allow_duplicate=True),
    Output("id-slider-ratio", "disabled"),
    Output("id-list-smiles-residue-highlight", "disabled"),
    Input("id-switch-residue-view", "checked"),  # DMC
    # Input("id-switch-residue-view", "value"),  # DBC
    Input("id-slider-ratio", "value"),
    Input("id-list-smiles-residue-highlight", "value"),
    State("id-table-exp-top-variants", "rowData"),
    prevent_initial_call=True,
)
def on_view_all_residue(view, slider_value, selected_smiles, rowData):
    # default the values
    sel = u_protein_viewer.reset_selection()
    foc = no_update
    enable_components = (not view) if view else no_update
    if view and rowData:
        df = pd.DataFrame(rowData)
        # filter by smiles value
        if selected_smiles:
            df_smiles = df[df[gs.c_smiles] == selected_smiles]
        else:
            df_smiles = df

        # apply the slider values
        delta = math.fabs(slider_value[0] - slider_value[1])
        if delta != 0:
            df_filtered = df_smiles[df_smiles[gs.cc_ratio].between(slider_value[0], slider_value[1])]
            # extract the residue indices for the viewer
            # residues = sorted(df_filtered[gs.c_substitutions].str.extractall(r"(\d+)")[0].unique().tolist())
            residues = (
                df_filtered[gs.c_substitutions]
                .apply(lambda x: utils.extract_all_indices(x))
                .explode()  # flatten the series
                .dropna()  # remove all the na
                .unique()
                .tolist()
            )

            # set up the protein viewer selection and focus
            if len(residues) != 0:
                sel, foc = u_protein_viewer.get_selection_focus(residues, analyse=False)

    return sel, foc, enable_components, enable_components


@app.callback(
    Output("id-table-exp-related-variants", "rowData"),
    # Output("id-exp-related-variants-protein-viewer", "children"),
    # Output("id-div-exp-related-variants-section", "style"),
    # inputs
    Input("id-button-run-seq-matching-exp", "n_clicks"),
    # from the form
    State("id-input-exp-related-variants-query-sequence", "children"),
    State("id-input-exp-related-variants-threshold", "value"),
    # State("id-input-exp-related-variants-hot-cold", "value"),
    State("id-input-exp-related-variants-residue", "value"),
    State("id-experiment-selected", "data"),
    # State("id-table-exp-top-variants", "rowData"),
    prevent_initial_call=True,
    running=[(Output("id-button-run-seq-matching-exp", "disabled"), True, False)],  # requires the latest Dash 2.16
)
def on_exp_related_variants(
    n_clicks,
    query_sequence,
    threshold,
    lookup_residues,
    experiment_id,
    # experiment_top_variants_row_data,
):
    if n_clicks != 0 and ctx.triggered_id == "id-button-run-seq-matching-exp":
        # get all the lab sequences
        all_lab_sequences = data_mgr.get_lab_sequences()

        # get the alignment and the base score
        lab_seq_match_data, base_score = bio_python_pairwise_aligner.get_alignments(
            query_sequence=query_sequence, threshold=float(threshold), targets=all_lab_sequences
        )

        # get the lookup list
        lookup_residues_list = lookup_residues.split(",")

        # gather final list of records data for table here
        exp_results_row_data = list(dict())
        for i in range(len(lab_seq_match_data)):
            # get experiment id of the matched sequence
            mathc_exp_id = lab_seq_match_data[i][gs.cc_experiment_id]

            # skip if it's the same experiment we're on
            if mathc_exp_id == experiment_id:
                continue

            # does my experiments variant show up in the other experiment
            # get the experiment core data from the db
            match_exp = data_mgr.get_experiment(mathc_exp_id)
            exp_results_row_data = u_seq_alignment.search_and_gather_variant_info_for_matching_experiment(
                experiment=match_exp,
                experiment_id=mathc_exp_id,
                lookup_residues_list=lookup_residues_list,
                seq_match_data=lab_seq_match_data[i],
                exp_results_row_data=exp_results_row_data,
            )
        return exp_results_row_data
    raise PreventUpdate


@app.callback(
    Output("id-exp-related-variants-selected-subs", "children"),
    # --------------
    # selected protein related
    # --------------
    Output("id-exp-related-variants-selected-protein-viewer", "children", allow_duplicate=True),
    Output("id-exp-related-variants-selected-id", "children"),
    Output("id-exp-related-variants-selected-reaction-image", "src"),
    Output("id-exp-related-variants-selected-substrate", "children"),
    Output("id-exp-related-variants-selected-product", "children"),
    # --------------
    # Query protein related
    # --------------
    Output("id-exp-related-variants-protein-viewer", "children", allow_duplicate=True),
    Output("id-exp-related-variants-id", "children"),
    Output("id-exp-related-variants-reaction-image", "src"),
    Output("id-exp-related-variants-substrate", "children"),
    Output("id-exp-related-variants-product", "children"),
    Input("id-table-exp-related-variants", "selectedRows"),
    State("id-experiment-selected", "data"),
    prevent_initial_call=True,
)
def display_selected_matching_sequences_protein_visualization_exp(selected_rows, experiment_id):
    if selected_rows:
        # selected experiment from the table
        selected_experiment_id = selected_rows[0][gs.cc_experiment_id]
        selected_substitutions = f"{selected_rows[0][gs.c_substitutions]}"
        selected_substitutions_list = utils.extract_all_indices(selected_substitutions)
        selected_substrate = f"{selected_rows[0][gs.cc_substrate][0]}"  # TODO: fix the list issue here
        selected_product = f"{selected_rows[0][gs.cc_product][0]}"

        # get the experiment info from the db
        # TODO: need to add a function to only get the geometry file not the whole experiment
        selected_experiment = data_mgr.get_experiment(selected_experiment_id)
        selected_experiment_geometry_file = selected_experiment.geometry_file_path

        experiment = data_mgr.get_experiment(experiment_id)
        experiment_geometry_file = experiment.geometry_file_path

        # if there is no geometry for the file ignore it
        if selected_experiment_geometry_file and experiment_geometry_file:
            # -------------------
            # Setup the selected row's molecular viewer
            # --------------------
            pdb_cif_selection = molstar_helper.parse_molecule(
                selected_experiment_geometry_file,
                component=u_protein_viewer.get_molstar_rendered_components_related_variants(
                    selected_substitutions_list
                ),
                preset={"kind": "empty"},
                fmt="cif",
            )

            selected_experiment_viewer = [
                dash_molstar.MolstarViewer(
                    data=pdb_cif_selection,
                    style={"width": "auto", "height": vis.related_protein_viewer_height},
                    # focus=analyse,
                )
            ]

            # -------------------
            # Setup the experiment's molecular viewer
            # --------------------
            pdb_cif_query = molstar_helper.parse_molecule(
                experiment_geometry_file,
                component=u_protein_viewer.get_molstar_rendered_components_related_variants(
                    selected_substitutions_list
                ),
                preset={"kind": "empty"},
                fmt="cif",
            )

            query_experiment_viewer = [
                dash_molstar.MolstarViewer(
                    data=pdb_cif_query,
                    style={"width": "auto", "height": vis.related_protein_viewer_height},
                    # focus=analyse,
                )
            ]

            # create the reaction image
            selected_svg_src = u_reaction.create_reaction_image(selected_substrate, selected_product)
            experiment_substrate = experiment.substrate[0]  # TODO: fix the list here
            experiment_product = experiment.product[0]
            experiment_svg_src = u_reaction.create_reaction_image(experiment_substrate, experiment_product)
            return (
                selected_substitutions,
                # --------------
                # selected experiment related
                # --------------
                selected_experiment_viewer,
                selected_experiment_id,
                selected_svg_src,
                selected_substrate,
                selected_product,
                # --------------
                # query protein related
                # --------------
                query_experiment_viewer,
                experiment_id,
                experiment_svg_src,
                experiment_substrate,
                experiment_product,
            )

    raise PreventUpdate


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
