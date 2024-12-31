#
# ui_upload.py
#
# Notes:
#  Defines a user interface for uploading experiment metadata and files.
#

import flask
import dash
from dash import dcc, html, callback, Input
import pandas

import wsexec
from ui_base import UIbase


class UIuploadData(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "fit-content",
            "border": "solid",
            "border-width": "1px",
            "float": "left",
        }

        # interaction layout: file upload
        self.contents = [
            html.H3("upload experiment metadata and files"),
            dcc.Upload(
                id=f"UIuploadData::trigger",  # (UIbase requires this format)
                children=html.Div(["Drag and drop or click to select files to upload"]),
                style={
                    "width": "320px",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=True,
                accept=".csv,.cif,.pdb",
            ),
            html.Div(id="div_filenames", children="(none yet)"),
        ]

        return

    # callback: file load
    #
    # This Dash implementation is as ugly as it could possibly be:
    #
    #  - The Upload component triggers a callback only when the contents of its "filename"
    #     and/or "contents" properties change, even if the user re-selects the same file(s)
    #     in the component interactive dialog.
    #
    #  - This means we need to reset these properties explicitly by binding them as Output
    #     in this callback implementation.
    #
    #  - But changing the properties triggers another callback! So that means we need to
    #     handle the re-entrant condition explicitly.  We do it by examining the "filename"
    #     value.
    #
    #  - Finally, in the re-entrant situation, we need to preserve the state of any other Output
    #     components.
    #
    # Apparently this horrible implementation is by design.  See, for example,
    #  https://community.plotly.com/t/upload-attributes-not-cleared-after-callback-runs/40697
    #
    # This entire trap can be avoided by NOT using the Upload component to actually upload
    #  anything!  Instead, the code can be written to keep the filenames and content around
    #  until some other UI component does something with them. (Typically "pythonic" approach:
    #  a few lines of code come at the expense of megabytes of bloat.) AARGH!
    #
    @callback(
        [
            Input("UIuploadData::trigger", "filename"),
            Input("UIuploadData::trigger", "contents"),
        ],
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(aFileNames: list[str], aFileContents: list[str]) -> None:
        print(f"UIuploadData callback: aFileNames: {aFileNames}")

        # If this callback was triggered by resetting the Upload component's "filename" and/or
        #  "contents" properties (see below), all we need to do is ensure that the UI state
        #  doesn't change.
        if len(aFileNames) == 0:
            ## TODO: set_props here???
            return

        uid = flask.session["uid"]
        eid = flask.session["eid"]

        # clear any previous error info
        dash.set_props("UIuploadData::error", dict(value=""))

        rval = ""
        for fileName, fileContents in zip(aFileNames, aFileContents, strict=True):

            # upload the file data
            print("UIuploadData callback: start query...")
            cb = wsexec.Query("load_file", [uid, eid, fileName, fileContents])
            print("UIuploadData callback: query ends")

            # append uploaded file info
            rval += f"Uploaded {fileName}: ({cb} bytes); "

        # show uploaded file info
        dash.set_props("div_filenames", dict(children=rval))

        # refresh the user experiment list
        cols, rows = wsexec.Query("get_user_experiments", [uid])  # type:ignore
        df = pandas.DataFrame(data=rows, columns=cols)  # type:ignore
        dash.set_props("tbl_experiment_list", dict(selected_rows=[]))
        dash.set_props("tbl_experiment_list", dict(data=df.to_dict("records")))

        # clear the Upload component filename and contents
        dash.set_props("UIuploadData::trigger", dict(filename=[], contents=[]))

        # update UI state
        dash.set_props("div_eid", dict(children=""))
        flask.session["eid"] = None

        # (we use dash.set_props instead of Output bindings)
        return
