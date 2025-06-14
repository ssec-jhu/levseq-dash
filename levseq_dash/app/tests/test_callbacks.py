from contextvars import copy_context

import pytest
from dash import html, no_update
from dash._callback_context import context_value
from dash._utils import AttributeDict
from dash.exceptions import CallbackException

from levseq_dash.app import global_strings as gs


def run_callback_display_page(pathname):
    from levseq_dash.app.main_app import display_page

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "url.pathname"}]}))
    return display_page(pathname=pathname)


@pytest.mark.parametrize(
    "pathname", ["/", gs.nav_experiment_path, gs.nav_upload_path, gs.nav_find_seq_path, "any-other-random-string"]
)
def test_callback_display_page(pathname):
    ctx = copy_context()
    output = ctx.run(run_callback_display_page, pathname)
    assert isinstance(output, html.Div)


# ------------------------------------------------
def run_callback_update_landing_page_buttons(selected_rows):
    from levseq_dash.app.main_app import update_landing_page_buttons

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-table-all-experiments.selectedRows"}]}))
    return update_landing_page_buttons(selected_rows=selected_rows)


def test_callback_update_landing_page_buttons():
    selected_rows = [{"experiment_id": 2}]
    ctx = copy_context()
    output = ctx.run(run_callback_update_landing_page_buttons, selected_rows)
    assert len(output) == 3
    assert output[0] == 2
    assert output[1] is False
    assert output[2] is False


def test_callback_update_landing_page_buttons_multiple_selection():
    selected_rows = [{"experiment_id": 2}, {"experiment_id": 4}]
    ctx = copy_context()
    output = ctx.run(run_callback_update_landing_page_buttons, selected_rows)
    assert len(output) == 3
    assert output[0] == no_update
    assert output[1] is False
    assert output[2] is True


def test_callback_update_landing_page_buttons_no_row():
    # no selected rows raises PreventUpdate
    ctx = copy_context()
    with pytest.raises(CallbackException):
        ctx.run(run_callback_update_landing_page_buttons, None)


# ------------------------------------------------


def run_callback_enable_submit_experiment(experiment, structure):
    from levseq_dash.app.main_app import enable_submit_experiment

    # input trigger to the function
    context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "id-exp-upload-csv.data"}]}))
    return enable_submit_experiment(
        experiment_success=experiment,  # any strings
        structure_success=structure,
    )


# def test_callback_enable_submit_experiment_valid():
#     ctx = copy_context()
#     output = ctx.run(run_callback_enable_submit_experiment, "experiment-string", "structure-string")
#     assert output is False


# def test_callback_enable_submit_experiment_invalid():
#     ctx = copy_context()
#     output = ctx.run(run_callback_enable_submit_experiment, None, "structure-string")
#     assert output is True

# ------------------------------------------------
