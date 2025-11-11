import base64
import time
from datetime import datetime

import dash_bootstrap_components as dbc
import dash_molstar
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
from dash_molstar.utils import molstar_helper

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import column_definitions as cd
from levseq_dash.app.components import graphs, vis
from levseq_dash.app.components.layout import (
    layout_about,
    layout_bars,
    layout_experiment,
    layout_explore,
    layout_landing,
    layout_matching_sequences,
    layout_upload,
)
from levseq_dash.app.components.widgets import get_alert
from levseq_dash.app.config import settings
from levseq_dash.app.data_manager.base import BaseDataManager
from levseq_dash.app.data_manager.experiment import Experiment
from levseq_dash.app.data_manager.manager import singleton_data_mgr_instance
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

# app.server.config.update(SECRET_KEY=settings.load_config()["db-service"]["session_key"])

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
        dcc.Store(id="id-uploaded-experiment-redirect"),
        # stores for clearing results
        dcc.Store(id="id-cleared-run-seq-matching", data=False),
        dcc.Store(id="id-cleared-run-exp-related-variants", data=False),
        # store for all experiments table filter persistence
        dcc.Store(id="id-table-all-experiments-filter-store", storage_type="session"),
        dcc.Location(id="url", refresh=False),
    ],
    fluid=True,
)


# @app.callback(
#     Output("memory-usage-display", "children"),
#     Input("interval", "n_intervals")
# )
# def update_memory(n):
#     """Calculates the total memory usage of the Dash application instance.
#
#     This function accounts for multiple worker processes, such as those managed by Gunicorn.
#     It identifies the main process and sums the memory usage of all its child processes
#     to provide a total memory footprint for the app.
#
#     """
#     try:
#         # Get the current process based on its process ID
#         current_process = psutil.Process(os.getpid())
#
#         # Start with the current process's memory
#         total_mem = current_process.memory_info().rss
#
#         # Include memory of all child processes. This is crucial for servers like Gunicorn
#         # where the main process spawns multiple workers.
#         children = current_process.children(recursive=True)
#         for child in children:
#             total_mem += child.memory_info().rss
#
#         # Convert from bytes to megabytes
#         mem_mb = total_mem / (1024 * 1024)
#         return f"{mem_mb:.2f} MB CH:{len(children)}"
#     except psutil.NoSuchProcess:
#         # Process may have been terminated between calls
#         return "Process not found"
#     except Exception as e:
#         # General exception handling
#         return f"Error: {e}"


@app.callback(Output("id-page-content", "children"), Input("url", "pathname"))
def route_page(pathname):
    if pathname == "/":
        return layout_landing.get_layout()
    elif pathname == gs.nav_experiment_path:
        return layout_experiment.get_layout()
    elif pathname == gs.nav_upload_path:
        return layout_upload.get_layout()
    elif pathname == gs.nav_find_seq_path:
        return layout_matching_sequences.get_layout()
    elif pathname == gs.nav_about_path:
        return layout_about.get_layout()
    elif pathname == gs.nav_explore_path:
        return layout_explore.get_layout()
    else:
        return html.Div([html.H2("Page not found!")])


# -------------------------------
#   Lab Landing Page (all experiments) related
# -------------------------------
@app.callback(
    Output("id-table-all-experiments", "rowData"),
    Output("id-table-all-experiments", "filterModel"),
    Input("id-table-all-experiments", "columnDefs"),
    State("id-table-all-experiments-filter-store", "data"),
)
def load_explore_page(temp_text, filter_store):
    list_of_all_lab_experiments_with_meta = singleton_data_mgr_instance.get_all_lab_experiments_with_meta_data()

    # all_substrate, all_product = utils.extract_all_substrate_product_smiles_from_lab_data(
    #     list_of_all_lab_experiments_with_meta
    # )
    #
    # # it's Ok if the substrate_svg_image or product_svg_image are None to any issues in the smiles
    # # UI will just not have an image, but won't fail
    # substrate_svg_image = u_reaction.create_mols_grid(all_substrate)
    # product_svg_image = u_reaction.create_mols_grid(all_product)
    return list_of_all_lab_experiments_with_meta, filter_store


@app.callback(
    Output("id-table-all-experiments-filter-store", "data"),
    Input("id-table-all-experiments", "filterModel"),
    prevent_initial_call=True,
)
def save_table_filter_state(filter_model):
    """Save filter state to browser session storage only when filters change"""
    if filter_model is None:
        return no_update
    else:
        return filter_model


@app.callback(
    Output("id-experiment-selected", "data"),
    Output("id-button-delete-experiment", "disabled"),
    Output("id-button-goto-experiment", "disabled"),
    Output("id-button-download-all-experiments", "disabled"),
    Input("id-table-all-experiments", "selectedRows"),
    prevent_initial_call=True,
)
def update_explore_page_buttons(selected_rows):
    # Display selected row info
    if not selected_rows:
        # disable all buttons
        return no_update, True, True, True

    # store the experiment id if there is exactly one selected row
    experiment_id = selected_rows[0]["experiment_id"] if len(selected_rows) == 1 else no_update

    # Manage button states based on number of selected rows
    go_to_experiment_btn_disabled = len(selected_rows) != 1  # enabled if there is only one selected row
    delete_btn_disabled = go_to_experiment_btn_disabled  # delete button will have the same behavior as the "go" button
    download_btn_disabled = len(selected_rows) < 1  # enabled if there is at least one selected row

    return experiment_id, delete_btn_disabled, go_to_experiment_btn_disabled, download_btn_disabled


@app.callback(
    Output("id-download-all-experiments-zip", "data"),
    Input("id-button-download-all-experiments", "n_clicks"),
    State("id-table-all-experiments", "selectedRows"),  # Get the selected rows instead of all table data
    prevent_initial_call=True,
    # in case the download takes time this will disable the button
    # so multiple cliks don't happen
    running=[(Output("id-button-download-all-experiments", "disabled"), True, False)],  # requires the latest Dash 2.16
)
def on_download_selected_experiments(n_clicks, selected_rows):
    if not selected_rows:
        raise PreventUpdate

    experiments_with_meta_data_dict = selected_rows if selected_rows else []

    if not experiments_with_meta_data_dict:
        return None

    zip_data = singleton_data_mgr_instance.get_experiments_zipped(experiments_with_meta_data_dict)

    # timestamp the file
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    zip_filename = f"EnzEngDB_Experiments_{timestamp}.zip"

    # dash dcc.Download component
    zip_download_data = dict(
        content=base64.b64encode(zip_data).decode(), filename=zip_filename, base64=True, type="application/zip"
    )

    return zip_download_data


# -------------------------------
#   Lab Landing Page - DELETE an experiment related
# -------------------------------
@app.callback(
    Output("id-delete-confirmation-modal", "is_open"),
    Output("id-delete-modal-body", "children"),
    Input("id-button-delete-experiment", "n_clicks"),
    State("id-table-all-experiments", "selectedRows"),
    prevent_initial_call=True,
)
def on_delete_experiment_open_modal(delete_clicks, selected_rows):
    """Opens the delete confirmation modal when delete button is clicked."""
    if ctx.triggered_id == "id-button-delete-experiment":
        if not selected_rows or len(selected_rows) != 1:
            raise PreventUpdate

        experiment_name = selected_rows[0].get("experiment_name", "Unknown")
        experiment_id = selected_rows[0]["experiment_id"]

        modal_message = html.Div(
            [
                html.P("Are you sure you want to delete the following experiment?"),
                html.P(
                    [
                        html.Strong("Name: "),
                        html.Span(experiment_name),
                    ]
                ),
                html.P(
                    [
                        html.Strong("ID: "),
                        html.Span(experiment_id),
                    ]
                ),
                html.P("This action will move the experiment to the DELETED_EXP folder.", className="text-muted small"),
            ]
        )

        return True, modal_message

    raise PreventUpdate


@app.callback(
    Output("id-delete-confirmation-modal", "is_open", allow_duplicate=True),
    Input("id-delete-modal-cancel", "n_clicks"),
    prevent_initial_call=True,
)
def on_delete_experiment_modal_cancel(cancel_clicks):
    """Closes the delete confirmation modal when Cancel or Delete is clicked."""
    if ctx.triggered_id == "id-delete-modal-cancel":
        return False

    raise PreventUpdate


@app.callback(
    Output("id-table-all-experiments", "deleteSelectedRows", allow_duplicate=True),
    Output("id-alert-explore", "children"),
    Output("id-delete-confirmation-modal", "is_open", allow_duplicate=True),
    Input("id-delete-modal-confirm", "n_clicks"),
    State("id-table-all-experiments", "selectedRows"),
    prevent_initial_call=True,
)
def on_delete_experiment_modal_confirmed(confirm_clicks, selected_rows):
    """Deletes the experiment after user confirms in the modal."""
    if confirm_clicks == 0 or ctx.triggered_id != "id-delete-modal-confirm":
        raise PreventUpdate

    if not selected_rows or len(selected_rows) != 1:
        raise PreventUpdate

    experiment_id = selected_rows[0]["experiment_id"]
    experiment_name = selected_rows[0].get("experiment_name", "Unknown")
    aggrid_deleteSelectedRows = no_update
    modal_open = False
    try:
        singleton_data_mgr_instance.delete_experiment(experiment_id)
    except Exception as e:
        error_message = (
            f"Error deleting experiment '{experiment_name}': {e}. Please see admin for deleting your experiment."
        )
        alert = get_alert(error_message, error=True)
    else:
        # Trigger AG Grid to remove the selected row from the table
        # this will trigger a refresh in the table
        success_message = f"Experiment '{experiment_name}' (ID: {experiment_id}) has been deleted successfully!"
        alert = get_alert(success_message, error=False)
        aggrid_deleteSelectedRows = True

    return aggrid_deleteSelectedRows, alert, modal_open


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
    assay_list = singleton_data_mgr_instance.get_assays()
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
        return "No file uploaded.", no_update
    else:
        try:
            base64_encoded_string = utils.decode_dash_upload_data_to_base64_encoded_string(dash_upload_string_contents)

            # convert the bytes string into a data frame
            df, csv_file_bytes = utils.decode_csv_file_base64_string_to_dataframe(base64_encoded_string)

            # check if this experiment already exists in the db
            # this will raise an exception if a duplicate is found
            csv_checksum = BaseDataManager.calculate_file_checksum(csv_file_bytes)
            singleton_data_mgr_instance.check_for_duplicate_experiment(csv_checksum)

            # sanity check will raise exceptions if any check is not passed
            checks_passed = Experiment.run_sanity_checks_on_experiment_file(df)
            if checks_passed:
                rows, cols = df.shape
                # checks have passed so we can extract this info
                unique_smiles_in_data = ".".join(df[gs.c_smiles].unique().tolist())
                info = [
                    html.Div(
                        [
                            html.Span("Uploaded Experiment: ", style={"fontWeight": "bold"}),
                            html.Span(filename, style={"color": "var(--cal-tech-color-2)"}),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("# Rows: ", style={"fontWeight": "bold"}),
                            html.Span(rows, style={"color": "var(--cal-tech-color-2)"}),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("# Columns: ", style={"fontWeight": "bold"}),
                            html.Span(cols, style={"color": "var(--cal-tech-color-2)"}),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("SMILEs in file: ", style={"fontWeight": "bold"}),
                            html.Span(unique_smiles_in_data, style={"color": "var(--cal-tech-color-2)"}),
                        ]
                    ),
                ]
                return info, base64_encoded_string
        except Exception as e:
            # a check did not pass
            info = [
                html.Div("Error found in file: ", style={"fontWeight": "bold", "color": "red"}),
                html.Div(str(e), style={"color": "red"}),
            ]
            alert = dbc.Alert(
                children=info,
                is_open=True,
                dismissable=True,
                class_name="user-alert-error",
            )
            return alert, no_update


@app.callback(
    Output("id-button-upload-structure-info", "children"),
    Output("id-exp-upload-structure", "data"),
    Input("id-button-upload-structure", "contents"),
    State("id-button-upload-structure", "filename"),
    State("id-button-upload-structure", "last_modified"),
)
def on_upload_structure_file(dash_upload_string_contents, filename, last_modified):
    if not dash_upload_string_contents:
        return "No file uploaded.", no_update
    else:
        try:
            base64_encoded_string = utils.decode_dash_upload_data_to_base64_encoded_string(dash_upload_string_contents)
            info = [
                html.Div(
                    [
                        html.Span("Uploaded Structure: ", style={"fontWeight": "bold"}),
                        html.Span(filename, style={"color": "var(--cal-tech-color-2)"}),
                    ]
                ),
            ]
            return info, base64_encoded_string
        except Exception as e:
            alert = get_alert(f"Error: {e}")
            return alert, no_update


@app.callback(
    Output("id-input-substrate", "valid"),
    Output("id-input-substrate", "invalid"),
    Input("id-input-substrate", "value"),
    prevent_initial_call=True,
)
def validate_substrate_smiles(substrate):
    valid, invalid = utils.validate_smiles_string(substrate)

    return valid, invalid


@app.callback(
    Output("id-input-product", "valid"),
    Output("id-input-product", "invalid"),
    Input("id-input-product", "value"),
    prevent_initial_call=True,
)
def validate_product_smiles(product):
    valid, invalid = utils.validate_smiles_string(product)

    return valid, invalid


@app.callback(
    Output("id-button-submit", "disabled"),
    Input("id-exp-upload-csv", "data"),
    Input("id-exp-upload-structure", "data"),
    Input("id-input-substrate", "valid"),
    Input("id-input-product", "valid"),
    prevent_initial_call=True,
)
def enable_submit_experiment(experiment_success, structure_success, valid_substrate, valid_product):
    """
    This callback is used to enable the submit button once all requirements are met
    """
    if (
        experiment_success
        and structure_success
        and valid_substrate
        and valid_product
        and settings.is_data_modification_enabled()
    ):
        return False
    else:
        return True


@app.callback(
    Output("id-alert-upload", "children"),
    # empty out the stores
    Output("id-exp-upload-structure", "data", allow_duplicate=True),
    Output("id-exp-upload-csv", "data", allow_duplicate=True),  # empty them out
    # redirect - use dedicated redirect store
    Output("id-uploaded-experiment-redirect", "data"),
    Input("id-button-submit", "n_clicks"),
    State("id-input-experiment-name", "value"),
    State("id-input-experiment-date", "date"),
    State("id-input-substrate", "value"),
    State("id-input-product", "value"),
    State("id-list-assay", "value"),
    State("id-radio-epr", "value"),
    State("id-input-experiment-doi", "value"),
    State("id-input-experiment-info", "value"),
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
    experiment_doi,
    experiment_additional_info,
    geometry_content_base64_encoded_string,
    experiment_content_base64_encoded_string,
):
    if n_clicks > 0 and ctx.triggered_id == "id-button-submit":
        try:
            experiment_id = singleton_data_mgr_instance.add_experiment_from_ui(
                experiment_name=experiment_name,
                experiment_date=experiment_date,
                substrate=substrate,
                product=product,
                assay=assay,
                mutagenesis_method=mutagenesis_method,
                experiment_doi=experiment_doi,
                experiment_additional_info=experiment_additional_info,
                experiment_content_base64_string=experiment_content_base64_encoded_string,
                geometry_content_base64_string=geometry_content_base64_encoded_string,
            )

            # you can verify the information here
            # exp = data_mgr.get_experiment(index)

            success = (
                f"Experiment with UUID: {experiment_id} has been added successfully! Redirecting to experiment page..."
            )
            alert = get_alert(success, error=False)

            return (
                alert,
                None,
                None,  # clear stores
                experiment_id,  # set experiment id in redirect store (triggers redirect)
            )

        except Exception as e:
            alert = get_alert(f"Error: {e}")

        return (
            alert,
            None,
            None,  # clear the data stores
            no_update,  # don't trigger redirect
        )

    else:
        raise PreventUpdate


@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("id-page-content", "children", allow_duplicate=True),
    Output("id-experiment-selected", "data", allow_duplicate=True),
    Output("id-uploaded-experiment-redirect", "data", allow_duplicate=True),
    Input("id-uploaded-experiment-redirect", "data"),
    prevent_initial_call=True,
)
def redirect_to_experiment_page_after_upload(experiment_id):
    """Redirect to experiment page immediately after successful upload."""
    if experiment_id is not None:
        return (
            gs.nav_experiment_path,
            layout_experiment.get_layout(),
            experiment_id,  # set the experiment as selected
            None,  # clear the redirect store
        )
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
    Output("id-cleared-run-seq-matching", "data"),  # flag
    Output("id-summary-seq-alignment", "children"),  # warning if any
    Output("id-alert-seq-alignment", "children"),  # alert
    Input("id-cleared-run-seq-matching", "data"),  # flag
    State("id-button-run-seq-matching", "n_clicks"),  # keep the button so "loading" works
    State("id-input-query-sequence", "value"),
    State("id-input-query-sequence-threshold", "value"),
    State("id-input-num-hot-cold", "value"),
    prevent_initial_call=True,
    running=[(Output("id-button-run-seq-matching", "disabled"), True, False)],  # requires the latest Dash 2.16
)
def on_load_matching_sequences(results_are_cleared, n_clicks, query_sequence, threshold, n_top_hot_cold):
    if ctx.triggered_id == "id-cleared-run-seq-matching" and results_are_cleared:
        try:
            # get all the lab sequences
            if settings.is_sequence_alignment_profiling_enabled():
                start_time = time.time()

            # get all the lab sequences
            all_lab_sequences = singleton_data_mgr_instance.get_all_lab_sequences()

            if settings.is_sequence_alignment_profiling_enabled():
                utils.log_with_context(
                    f"[PROFILING] on_load_matching_sequences: get_all_lab_sequences() {time.time() - start_time} s",
                    log_flag=settings.is_sequence_alignment_profiling_enabled(),
                )
                start_time = time.time()

            # get the alignment and the base score
            lab_seq_match_data, base_score, warning_info = bio_python_pairwise_aligner.get_alignments(
                query_sequence=query_sequence, threshold=float(threshold), targets=all_lab_sequences
            )

            if settings.is_sequence_alignment_profiling_enabled():
                utils.log_with_context(
                    f"[PROFILING] on_load_matching_sequences: get_alignments() {time.time() - start_time} s",
                    log_flag=settings.is_sequence_alignment_profiling_enabled(),
                )
                start_time = time.time()

            n_matches = len(lab_seq_match_data)

            # alert the user that no matches were found
            if n_matches == 0:
                raise Exception("Sequence alignment returned 0 matches.")

            seq_match_row_data = list(dict())

            # for each matching experiment pull out it's metadata
            hot_cold_row_data = pd.DataFrame()
            for i in range(len(lab_seq_match_data)):
                # add experiment id
                exp_id = lab_seq_match_data[i][gs.cc_experiment_id]

                # get the experiment core data for the db
                exp = singleton_data_mgr_instance.get_experiment(exp_id)
                experiment_meta_data = singleton_data_mgr_instance.get_experiment_metadata(exp_id)

                # extract the top N (hot) and bottom N (cold) fitness values of this experiment
                hot_cold_spots_merged_df, hot_cold_residue_per_smiles = exp.exp_hot_cold_spots(int(n_top_hot_cold))

                # add the experiment id to this data
                hot_cold_spots_merged_df[gs.cc_experiment_id] = exp_id
                # add the experiment name to the data
                hot_cold_spots_merged_df[gs.c_experiment_name] = experiment_meta_data[gs.c_experiment_name]

                # add the parent sequence to the data
                hot_cold_spots_merged_df["parent_sequence"] = experiment_meta_data["parent_sequence"]

                # concatenate this info with the rest of the hot and cold spot data
                hot_cold_row_data = pd.concat([hot_cold_row_data, hot_cold_spots_merged_df], ignore_index=True)

                # expand the data of each row per smiles - request by PI
                seq_match_row_data = u_seq_alignment.gather_seq_alignment_data_per_smiles(
                    df_hot_cold_residue_per_smiles=hot_cold_residue_per_smiles,
                    seq_match_data=lab_seq_match_data[i],
                    exp_meta_data=experiment_meta_data,
                    seq_match_row_data=seq_match_row_data,
                )

                del exp
                del hot_cold_spots_merged_df

            if settings.is_sequence_alignment_profiling_enabled():
                utils.log_with_context(
                    f"[PROFILING] on_load_matching_sequences: finding gof/lof {time.time() - start_time} s",
                    log_flag=settings.is_sequence_alignment_profiling_enabled(),
                )

            info = f"# Matched Sequences: {n_matches}"

            if len(warning_info) != 0:
                warning = get_alert(warning_info, error=False, is_markdown=True)
            else:
                warning = no_update

            return (
                seq_match_row_data,  # the results in records format for ag-grid table: id-table-matched-sequences
                hot_cold_row_data.to_dict("records"),  # table: id-table-matched-sequences-exp-hot-cold-data
                info,
                vis.display_block,  # set the visibility on
                False,  # make sure cleared is set to False
                warning,  # warning if any
                no_update,  # alert
            )
        except Exception as e:
            # put the exception message in an alert box
            # alert_message = exceptions.alert_message_from_exception(e)
            alert = get_alert(f"Error: {e}")
            return no_update, no_update, no_update, no_update, False, no_update, alert
    else:
        raise PreventUpdate


@app.callback(
    Output("id-alert-seq-alignment", "children", allow_duplicate=True),
    Output("id-div-seq-alignment-results", "style", allow_duplicate=True),
    Output("id-cleared-run-seq-matching", "data", allow_duplicate=True),
    Input("id-button-run-seq-matching", "n_clicks"),
    State("id-cleared-run-seq-matching", "data"),
    prevent_initial_call=True,
)
def on_button_run_seq_matching(n_clicks, results_are_cleared):
    """
    Upon id-button-run-seq-matching button click the previous
    results and alerts (if any) are cleared and flag is set to recalculate
    """
    if ctx.triggered_id == "id-button-run-seq-matching" and n_clicks > 0 and not results_are_cleared:
        return (
            # clear everything
            [],  # clear alert if any
            vis.display_none,  # clear seq_alignment page results
            True,  # set clear to true
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("id-table-matched-sequences", "selectedRows"),
    Input("id-table-matched-sequences", "virtualRowData"),
    prevent_initial_call=True,
)
def display_default_selected_matching_sequences(data):
    # set the default selected row to be the first row that is rendered on the front end
    # the table sets the sorting and all on the front end side after it is rendered, so we
    # can not select the first row of the data output that gets sent from the previous
    # callback.
    return utils.select_first_row_of_data(data)


@app.callback(
    Output("id-viewer-selected-seq-matched-protein", "children"),
    Output("id-selected-seq-matched-reaction-image", "src"),
    Output("id-selected-seq-matched-substrate", "children"),
    Output("id-selected-seq-matched-product", "children"),
    # informative text
    Output("id-div-selected-seq-matched-protein-highlights-info1", "children"),
    Output("id-div-selected-seq-matched-protein-highlights-info2", "children"),
    Output("id-div-selected-seq-matched-protein-highlights-info3", "children"),
    # Input
    Input("id-table-matched-sequences", "selectedRows"),
    prevent_initial_call=True,
)
def display_selected_matching_sequences(selected_rows):
    if selected_rows and len(selected_rows) > 0:
        # extract the info from the table
        substitutions = f"{selected_rows[0][gs.cc_seq_alignment_mismatches]}"
        hot_spots = f"{selected_rows[0][gs.cc_hot_indices_per_smiles]}"
        cold_spots = f"{selected_rows[0][gs.cc_cold_indices_per_smiles]}"
        experiment_id = selected_rows[0][gs.cc_experiment_id]
        # experiment_smiles = selected_rows[0][gs.c_smiles]
        substrate = selected_rows[0][gs.cc_substrate]
        product = selected_rows[0][gs.cc_product]

        # get the experiment info from the db
        exp = singleton_data_mgr_instance.get_experiment(experiment_id)
        geometry_file = exp.geometry_base64_bytes

        svg_src_image = u_reaction.create_reaction_image(substrate, product)

        del exp

        # if there is no geometry for the file ignore it
        if geometry_file:
            # gather the rendering components per the indices
            list_of_rendered_components, hs_only, cs_only, both_hs_and_cs = (
                u_protein_viewer.get_molstar_rendered_components_seq_alignment(
                    hot_residue_indices_list=hot_spots,
                    cold_residue_indices_list=cold_spots,
                    substitution_residue_list=substitutions,
                )
            )

            # the lists are ints, need to convert back to string
            highlights_hot = ", ".join(str(num) for num in hs_only)
            highlights_cold = ", ".join(str(num) for num in cs_only)
            highlights_both = ", ".join(str(num) for num in both_hs_and_cs)

            # set up the molecular viewer and render it
            pdb_cif = molstar_helper.parse_molecule(
                geometry_file,
                component=list_of_rendered_components,
                preset={"kind": "empty"},  # need to keep this. not having this renders the chain as a component
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
            highlights_both,
            highlights_hot,
            highlights_cold,
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
def on_download_matched_sequences_exp_hot_cold_data_as_csv(n_clicks, option):
    return utils.export_data_as_csv(option, gs.filename_download_residue_info)


@app.callback(
    Output("id-table-matched-sequences", "exportDataAsCsv"),
    Output("id-table-matched-sequences", "csvExportParams"),
    Input("id-button-download-matched-sequences-results", "n_clicks"),
    State("id-button-download-matched-sequences-results-options", "value"),
    prevent_initial_call=True,
    # in case the download takes time this will disable the button
    # so multiple cliks don't happen
    running=[(Output("id-button-download-matched-sequences-results", "disabled"), True, False)],
)
def on_download_matched_sequence_data_as_csv(n_clicks, option):
    return utils.export_data_as_csv(option, gs.filename_download_matched_sequences)


# -------------------------------
#   Experiment Dashboard - Main Tab related
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
        return gs.nav_experiment_path, layout_experiment.get_layout()
    else:
        raise PreventUpdate


@app.callback(
    # -------------------------------
    # Tab name
    # -------------------------------
    Output("id-experiment-tab-1", "label"),
    # -------------------------------
    # Initialize the store with default values
    # -------------------------------
    Output("id-exp-listbox-store", "data"),
    # Output("id-temp-store-data", "data"),
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
    Output("id-experiment-doi", "children"),
    Output("id-experiment-additional-info", "children"),
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
    Output("id-ranking-plot-container", "style"),
    # -------------------------------
    # residue highlight slider
    # --------------------------------
    Output("id-slider-ratio", "value"),
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
    # -------------------------------
    # SSM plot dropdowns and figure
    # --------------------------------
    Output("id-list-ssm-residue-positions", "options"),
    Output("id-list-ssm-residue-positions", "value"),
    Output("id-list-smiles-ssm-plot", "options"),
    Output("id-list-smiles-ssm-plot", "value"),
    Output("id-experiment-ssm-plot", "figure"),
    Output("id-ssm-plot-container", "style"),
    # --------------------------------
    # Inputs
    # --------------------------------
    Input("url", "pathname"),
    State("id-experiment-selected", "data"),
    prevent_initial_call=True,
)
def on_load_experiment_page(pathname, experiment_id):
    if pathname == gs.nav_experiment_path:
        exp = singleton_data_mgr_instance.get_experiment(experiment_id)
        exp_meta_data = singleton_data_mgr_instance.get_experiment_metadata(experiment_id)
        experiment_name = exp_meta_data.get("experiment_name", "")
        parent_sequence = exp_meta_data.get("parent_sequence", "")
        substrate = exp_meta_data.get("substrate", "")
        product = exp_meta_data.get("product", "")
        experiment_additional_info = exp_meta_data.get("additional_information", "")
        experiment_doi = exp_meta_data.get("doi", "")

        # viewer data
        pdb_cif = molstar_helper.parse_molecule(exp.geometry_base64_bytes, fmt="cif")

        # load the dropdown for the plots with default values
        default_plate = exp.plates[0]
        default_smiles = exp.unique_smiles_in_data[0]
        default_experiment_heatmap_properties_list = gs.experiment_heatmap_properties_list[0]
        unique_smiles_in_data_str = ".".join(exp.unique_smiles_in_data)

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

        # drop unnecessary columns here.
        columns_to_drop = ["min", "max", "min_group_ratio", "max_group_ratio", "mean"]
        df_filtered_with_ratio = df_filtered_with_ratio.drop(
            columns=[col for col in columns_to_drop if col in df_filtered_with_ratio.columns]
        )

        # set up the slider
        # Fallback if no ratio column exists or values are not valid
        ratio_max = 5.0
        slider_default_value = [0.0, ratio_max]
        if gs.cc_ratio in df_filtered_with_ratio.columns:
            ratio_min = df_filtered_with_ratio[gs.cc_ratio].min()
            ratio_max = np.ceil(df_filtered_with_ratio[gs.cc_ratio].max())
            if ratio_max - ratio_min > 0:
                # Use reasonable defaults that fit within the data range
                slider_default_value = [ratio_min, ratio_max]

        svg_src_image = u_reaction.create_reaction_image(substrate, product)

        # Determine experiment type and setup conditional layouts
        mutagenesis_method = exp_meta_data.get("mutagenesis_method", "")

        # Check if this is a single-site mutagenesis experiment
        is_ssm_experiment = mutagenesis_method == gs.ssm

        store_data = {
            "heatmap": {
                "plate": default_plate,
                "smiles": default_smiles,
                "property": default_experiment_heatmap_properties_list,
            }
        }

        # Initialize rank plot and SSM plot outputs
        rank_plot_figure = None
        rank_plot_list_of_plates = no_update
        rank_plot_default_plate = no_update
        rank_plot_list_of_unique_smiles = no_update
        rank_plot_default_smiles = no_update
        rank_plot_container_style = no_update

        ssm_plot_figure = None
        ssm_plot_list_mutation_positions = no_update
        ssm_plot_default_site = no_update
        ssm_plot_list_of_unique_smiles = no_update
        ssm_plot_default_smiles = no_update
        ssm_plot_container_style = no_update

        if is_ssm_experiment:
            # Get available single-site mutation positions
            list_ssm_positions = graphs.extract_single_site_mutations(exp.data_df, default_smiles)

            # Create SSM plot if positions are available
            default_site = list_ssm_positions[0] if len(list_ssm_positions) > 0 else None

            # list of sites that may or may not be empty, regardless have a figure. May be parents only
            ssm_plot_figure = graphs.create_ssm_plot(
                df=exp.data_df, smiles_string=default_smiles, residue_number=default_site
            )

            # successful ssm plot creation
            if ssm_plot_figure is not None:
                store_data["ssm_plot"] = {"residue": default_site, "smiles": default_smiles}
                ssm_plot_list_mutation_positions = list_ssm_positions
                ssm_plot_default_site = default_site
                ssm_plot_list_of_unique_smiles = exp.unique_smiles_in_data
                ssm_plot_default_smiles = default_smiles
                ssm_plot_container_style = {"display": "block"}

        # fallback if ssm fails OR if the experiment is not ssm
        if ssm_plot_figure is None:
            # creat the ranking plot with default values
            # rank plot uses the ratio data to color
            rank_plot_figure = graphs.creat_rank_plot(
                df=df_filtered_with_ratio,
                plate_number=default_plate,
                smiles=default_smiles,
            )

            store_data["rank_plot"] = {"plate": default_plate, "smiles": default_smiles}
            rank_plot_list_of_plates = exp.plates
            rank_plot_default_plate = default_plate
            rank_plot_list_of_unique_smiles = exp.unique_smiles_in_data
            rank_plot_default_smiles = default_smiles
            rank_plot_container_style = {"display": "block"}

        return (
            # Tab name
            # -------------------------------
            f"Experiment #{experiment_id}:  {experiment_name}",
            # --------------------------------
            # Store data
            # --------------------------------
            store_data,
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
            experiment_name,
            parent_sequence,
            exp_meta_data.get("mutagenesis_method", ""),
            exp_meta_data.get("experiment_date", ""),
            exp_meta_data.get("upload_time_stamp", ""),
            exp_meta_data.get("plates_count", 0),
            unique_smiles_in_data_str,
            substrate,
            product,
            exp_meta_data.get("assay", ""),
            experiment_doi,
            experiment_additional_info,
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
            rank_plot_list_of_plates,
            rank_plot_default_plate,
            rank_plot_list_of_unique_smiles,
            rank_plot_default_smiles,
            rank_plot_figure,
            rank_plot_container_style,
            # -------------------------------
            # residue highlight slider
            # --------------------------------
            slider_default_value,
            ratio_max,
            exp.unique_smiles_in_data,  # list of smiles values
            default_smiles,  # default smiles
            # -------------------------------
            # related sequences
            # --------------------------------
            parent_sequence,
            # -------------------------------
            # reaction
            # --------------------------------
            svg_src_image,
            # --------------------------------
            # SSM plot dropdowns and figure
            # --------------------------------
            ssm_plot_list_mutation_positions,
            ssm_plot_default_site,
            ssm_plot_list_of_unique_smiles,
            ssm_plot_default_smiles,
            ssm_plot_figure,
            ssm_plot_container_style,
        )
    else:
        raise PreventUpdate


def check_early_return(rowData, store_data, plot_str, trigger_list):
    if rowData is None:
        raise PreventUpdate

    # If store is None or doesn't have heatmap data, this means it's the initial load
    # and the store hasn't been properly initialized yet
    if store_data is None or plot_str not in store_data:
        raise PreventUpdate

    # Only respond to actual user interactions with the heatmap controls
    if ctx.triggered_id not in trigger_list:
        raise PreventUpdate


@app.callback(
    Output("id-experiment-heatmap", "figure", allow_duplicate=True),
    Output("id-list-smiles", "disabled"),
    Output("id-list-smiles", "className"),
    Output("id-exp-listbox-store", "data", allow_duplicate=True),
    Input("id-list-plates", "value"),
    Input("id-list-smiles", "value"),
    Input("id-list-properties", "value"),
    State("id-table-exp-top-variants", "rowData"),
    State("id-exp-listbox-store", "data"),
    # State("id-store-heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_heatmap(selected_plate, selected_smiles, selected_stat_property, rowData, store_data):
    check_early_return(rowData, store_data, "heatmap", ["id-list-plates", "id-list-smiles", "id-list-properties"])

    # Check if values have actually changed from previous selection
    previous_heatmap_values = store_data.get("heatmap", {})
    current_heatmap_values = {"plate": selected_plate, "smiles": selected_smiles, "property": selected_stat_property}

    # If values haven't changed, prevent update
    if previous_heatmap_values == current_heatmap_values:
        raise PreventUpdate

    # Update store with new values
    store_data["heatmap"] = current_heatmap_values

    df = pd.DataFrame(rowData)

    show_smiles = selected_stat_property == gs.experiment_heatmap_properties_list[0]

    stat_heatmap = graphs.creat_heatmap(
        df, plate_number=selected_plate, property=selected_stat_property, smiles=selected_smiles
    )
    if not show_smiles:
        class_name = "opacity-50 text-secondary dbc"
    else:
        class_name = "dbc"
    return stat_heatmap, not show_smiles, class_name, store_data


@app.callback(
    Output("id-experiment-ranking-plot", "figure", allow_duplicate=True),
    Output("id-exp-listbox-store", "data", allow_duplicate=True),
    Input("id-list-plates-ranking-plot", "value"),
    Input("id-list-smiles-ranking-plot", "value"),
    State("id-table-exp-top-variants", "rowData"),
    State("id-exp-listbox-store", "data"),
    # State("id-store-heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_rank_plot(selected_plate, selected_smiles, rowData, store_data):
    check_early_return(rowData, store_data, "rank_plot", ["id-list-plates-ranking-plot", "id-list-smiles-ranking-plot"])

    # Check if values have actually changed from previous selection
    previous_rank_values = store_data.get("rank_plot", {})
    current_rank_values = {"plate": selected_plate, "smiles": selected_smiles}

    # If values haven't changed, prevent update
    if previous_rank_values == current_rank_values:
        raise PreventUpdate

    # Update store with new values
    store_data["rank_plot"] = current_rank_values

    df = pd.DataFrame(rowData)

    rank_plot = graphs.creat_rank_plot(df, plate_number=selected_plate, smiles=selected_smiles)

    return rank_plot, store_data


@app.callback(
    Output("id-experiment-ssm-plot", "figure", allow_duplicate=True),
    Output("id-exp-listbox-store", "data", allow_duplicate=True),
    Input("id-list-ssm-residue-positions", "value"),
    Input("id-list-smiles-ssm-plot", "value"),
    State("id-table-exp-top-variants", "rowData"),
    State("id-exp-listbox-store", "data"),
    prevent_initial_call=True,
)
def update_ssm_plot(selected_residue, selected_smiles, rowData, store_data):
    check_early_return(rowData, store_data, "ssm_plot", ["id-list-ssm-residue-positions", "id-list-smiles-ssm-plot"])

    # Check if values have actually changed from previous selection
    previous_ssm_values = store_data.get("ssm_plot", {})
    current_ssm_values = {"residue": selected_residue, "smiles": selected_smiles}

    # If values haven't changed, prevent update
    if previous_ssm_values == current_ssm_values:
        raise PreventUpdate

    # Update store with new values
    store_data["ssm_plot"] = current_ssm_values

    df = pd.DataFrame(rowData)

    ssm_plot = graphs.create_ssm_plot(df=df, smiles_string=selected_smiles, residue_number=selected_residue)

    return ssm_plot, store_data


@app.callback(
    Output("id-viewer", "selection"),
    Output("id-viewer", "focus"),
    Output("id-div-filtered-residue", "children"),
    Output("id-switch-residue-view", "value"),  # tur off the switch
    Input("id-table-exp-top-variants", "selectedRows"),
    prevent_initial_call=True,
)
def on_view_selected_residue_from_table(selected_rows):
    """
    This callback gets called when the user selects a row from the Top Variants table.
    Make sure changes here are consistent with the callback 'on_view_all_residue'
    """
    # default values
    sel = no_update  # u_protein_viewer.reset_selection()
    foc = no_update
    highlighted_residue_info = no_update
    view_all_residue_switch = no_update

    # highlight and focus on residues from the selected row
    if selected_rows:
        highlighted_residue_info = ""
        view_all_residue_switch = False  # turn the switch off to avoid confusion
        sel = u_protein_viewer.reset_selection()

        highlighted_residue_info += f"Highlighted Residues: "
        if selected_rows[0][gs.c_substitutions] == gs.hashtag_parent:
            highlighted_residue_info += gs.hashtag_parent
        else:
            residues = utils.extract_all_indices(f"{selected_rows[0][gs.c_substitutions]}")

            # set up the protein viewer selection and focus
            if len(residues) != 0:
                sel, foc = u_protein_viewer.get_selection_focus(residues)
                highlighted_residue_info += f"{', '.join(residues)}"
            else:
                # if there is no residue to show, just reset the selection
                highlighted_residue_info += f"None"

        return sel, foc, highlighted_residue_info, view_all_residue_switch


@app.callback(
    Output("id-viewer", "selection", allow_duplicate=True),
    Output("id-viewer", "focus", allow_duplicate=True),
    Output("id-slider-ratio", "disabled"),
    Output("id-list-smiles-residue-highlight", "disabled"),
    Output("id-div-filtered-residue", "children", allow_duplicate=True),
    Input("id-switch-residue-view", "value"),
    Input("id-slider-ratio", "value"),
    Input("id-list-smiles-residue-highlight", "value"),
    State("id-table-exp-top-variants", "rowData"),
    prevent_initial_call=True,
)
def on_view_all_residue(view, slider_value, selected_smiles, rowData):
    """
    This callback gets called when the user switches the 'view all residues' toggle switch.
    Make sure changes here are consistent with the callback 'on_view_selected_residue_from_table'
    """
    # default values
    sel = no_update  # u_protein_viewer.reset_selection()
    foc = no_update
    highlighted_residue_info = no_update
    slider_disabled = True
    listbox_disabled = True

    if view and rowData:
        # let's turn it on unless we have a reason turn it off
        slider_disabled = False
        listbox_disabled = False
        highlighted_residue_info = ""
        sel = u_protein_viewer.reset_selection()

        # filter by smiles value
        if selected_smiles:
            df = pd.DataFrame(rowData)
            df_smiles = df[df[gs.c_smiles] == selected_smiles]

            # Check if the filtered df_smiles has meaningful ratio values
            #  are only meaningful if there are multiple rows and they vary
            has_meaningful_ratios = False
            if len(df_smiles) > 1:
                # Check if ratio column exists and has non-null, varying values
                if gs.cc_ratio in df_smiles.columns:
                    ratio_values = df_smiles[gs.cc_ratio].dropna()
                    if len(ratio_values) > 1 and ratio_values.nunique() > 1:
                        has_meaningful_ratios = True

            if not has_meaningful_ratios:
                df_filtered = df_smiles
                # disable the slider when no meaningful ratios are present
                slider_disabled = True
                highlighted_residue_info += "No ratios for selected SMILES; "
            else:
                # apply the slider values since we have meaningful ratios
                df_filtered = df_smiles[df_smiles[gs.cc_ratio].between(slider_value[0], slider_value[1])]

            # after the filtering there may only be the parent left
            highlighted_residue_info += f" Highlighted Residues: "
            if df_filtered.shape[0] == 1 and df_filtered[gs.c_substitutions].iloc[0] == gs.hashtag_parent:
                residues = []
                highlighted_residue_info += gs.hashtag_parent
            else:
                # extract the indices for the protein viewer
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
                    highlighted_residue_info += f"{', '.join(residues)}"
                else:
                    # if there is no residue to show, just reset the selection
                    highlighted_residue_info += f"None"

    return (
        sel,
        foc,
        slider_disabled,  # slider
        listbox_disabled,  # list box
        highlighted_residue_info,
    )


# ----------------------------------------
#   Experiment Related Variants Tab related
# ----------------------------------------
@app.callback(
    Output("id-table-exp-related-variants", "rowData"),
    # --------------
    # Query protein related
    # --------------
    Output("id-exp-related-variants-id", "children"),
    Output("id-exp-related-variants-reaction-image", "src"),
    Output("id-exp-related-variants-substrate", "children"),
    Output("id-exp-related-variants-product", "children"),
    Output("id-div-exp-related-variants", "style"),
    Output("id-cleared-run-exp-related-variants", "data"),  # reset the flag
    Output("id-summary-exp-related-variants", "children"),
    Output("id-alert-exp-related-variants", "children"),  # alert
    # --------------
    # Inputs
    # --------------
    Input("id-cleared-run-exp-related-variants", "data"),
    State("id-button-run-seq-matching-exp", "n_clicks"),  # keep the button so "loading" works
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
def on_load_exp_related_variants(
    results_are_cleared,
    n_clicks,
    query_sequence,
    threshold,
    lookup_residues,
    experiment_id,
    # experiment_top_variants_row_data,
):
    if ctx.triggered_id == "id-cleared-run-exp-related-variants" and results_are_cleared:
        try:
            # get the lookup list
            if lookup_residues is None:
                raise Exception("Please provide at least one residue index for lookup.")

            lookup_residues_list = lookup_residues.split(",")

            if settings.is_sequence_alignment_profiling_enabled():
                start_time = time.time()

            # get all the lab sequences
            all_lab_sequences = singleton_data_mgr_instance.get_all_lab_sequences()

            if settings.is_sequence_alignment_profiling_enabled():
                print(f"[PROFILING] on_load_exp_related_variants: get_all_lab_sequences() {time.time() - start_time} s")
                start_time = time.time()

            # get the alignment and the base score
            lab_seq_match_data, base_score, warning_info = bio_python_pairwise_aligner.get_alignments(
                query_sequence=query_sequence, threshold=float(threshold), targets=all_lab_sequences
            )

            if settings.is_sequence_alignment_profiling_enabled():
                print(f"[PROFILING] on_load_exp_related_variants: get_alignments() {time.time() - start_time} s")
                start_time = time.time()

            if len(lab_seq_match_data) == 0:
                raise Exception("Sequence alignment returned 0 matches.")

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
                match_exp = singleton_data_mgr_instance.get_experiment(mathc_exp_id)
                match_exp_meta_data = singleton_data_mgr_instance.get_experiment_metadata(mathc_exp_id)
                exp_results_row_data = u_seq_alignment.search_and_gather_variant_info_for_matching_experiment(
                    experiment=match_exp,
                    experiment_meta_data=match_exp_meta_data,
                    lookup_residues_list=lookup_residues_list,
                    seq_match_data=lab_seq_match_data[i],
                    exp_results_row_data=exp_results_row_data,
                )

                del match_exp

            if settings.is_sequence_alignment_profiling_enabled():
                print(f"[PROFILING] on_load_exp_related_variants: finding residues {time.time() - start_time} s")

            if len(exp_results_row_data) == 0:
                raise Exception(
                    f"Among the {len(lab_seq_match_data)} sequence matches, "
                    f"residues: {lookup_residues_list} were not found."
                )

            # gather the info for making this experiments reaction image for use in comparison
            experiment_metadata = singleton_data_mgr_instance.get_experiment_metadata(experiment_id)
            experiment_substrate = experiment_metadata.get(gs.cc_substrate, "")
            experiment_product = experiment_metadata.get(gs.cc_product, "")

            experiment_svg_src = u_reaction.create_reaction_image(experiment_substrate, experiment_product)

            if len(warning_info) != 0:
                warning = get_alert(warning_info, error=False, is_markdown=True)
            else:
                warning = no_update

            return (
                exp_results_row_data,
                experiment_id,
                experiment_svg_src,
                experiment_substrate,
                experiment_product,
                vis.display_block,  # set the visibility on
                False,  # make sure cleared is set to False
                warning,
                no_update,  # no alert
            )

        except Exception as e:
            alert = get_alert(f"Error: {e}")
            return no_update, no_update, no_update, no_update, no_update, no_update, False, no_update, alert
    else:
        raise PreventUpdate


@app.callback(
    Output("id-alert-exp-related-variants", "children", allow_duplicate=True),
    Output("id-div-exp-related-variants", "style", allow_duplicate=True),
    Output("id-cleared-run-exp-related-variants", "data", allow_duplicate=True),
    Input("id-button-run-seq-matching-exp", "n_clicks"),
    State("id-cleared-run-exp-related-variants", "data"),
    prevent_initial_call=True,
)
def on_button_run_exp_related_variants(n_clicks, results_are_cleared):
    """
    Upon id-button-run-seq-matching-exp button click the previous
    results and alerts (if any) are cleared and flag is set to recalculate
    """
    if ctx.triggered_id == "id-button-run-seq-matching-exp" and n_clicks > 0 and not results_are_cleared:
        return (  # clear everything
            [],  # clear alert if any
            vis.display_none,  # seq_alignment page results
            True,  # set clear to true
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("id-table-exp-related-variants", "selectedRows"),
    Input("id-table-exp-related-variants", "virtualRowData"),
    prevent_initial_call=True,
)
def display_default_selected_exp_related_variants(data):
    # set the default selected row to be the first row that is rendered on the front end
    # the table sets the sorting and all on the front end side after it is rendered, so we
    # can not select the first row of the data output that gets sent from the previous
    # callback.
    return utils.select_first_row_of_data(data)


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
    Input("id-table-exp-related-variants", "selectedRows"),
    State("id-experiment-selected", "data"),
    prevent_initial_call=True,
)
def display_selected_exp_related_variants(selected_rows, experiment_id):
    if selected_rows:
        # selected experiment from the table
        selected_experiment_id = selected_rows[0][gs.cc_experiment_id]
        selected_substitutions = f"{selected_rows[0][gs.c_substitutions]}"
        selected_substitutions_list = utils.extract_all_indices(selected_substitutions)
        selected_substrate = f"{selected_rows[0][gs.cc_substrate]}"
        selected_product = f"{selected_rows[0][gs.cc_product]}"

        # get the experiment info from the db
        selected_experiment = singleton_data_mgr_instance.get_experiment(selected_experiment_id)
        selected_experiment_geometry_file = selected_experiment.geometry_base64_bytes

        experiment = singleton_data_mgr_instance.get_experiment(experiment_id)
        experiment_geometry_file = experiment.geometry_base64_bytes

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
                preset={"kind": "empty"},  # need to keep this. not having this renders the chain as a component
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
                preset={"kind": "empty"},  # need to keep this. not having this renders the chain as a component
                fmt="cif",
            )

            query_experiment_viewer = [
                dash_molstar.MolstarViewer(
                    data=pdb_cif_query,
                    style={"width": "auto", "height": vis.related_protein_viewer_height},
                    # focus=analyse,
                )
            ]

            # create the reaction image for the selected row
            selected_svg_src = u_reaction.create_reaction_image(selected_substrate, selected_product)

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
            )

    raise PreventUpdate


@app.callback(
    Output("id-table-exp-related-variants", "exportDataAsCsv"),
    Output("id-table-exp-related-variants", "csvExportParams"),
    Input("id-button-download-related-variants-results", "n_clicks"),
    State("id-button-download-related-variants-results-options", "value"),
    prevent_initial_call=True,
    # in case the download takes time this will disable the button
    # so multiple cliks don't happen
    running=[(Output("id-button-download-related-variants-results", "disabled"), True, False)],
)
def on_download_exp_relate_variants_results(n_clicks, option):
    return utils.export_data_as_csv(option, gs.filename_download_related_variants)


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
    app.run()
