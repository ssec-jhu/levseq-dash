#
# ui_set_user.py
#
# Notes:
#  Defines a user interface for setting the current LevSeq user.
#

import flask
import dash
from dash import dcc, html, callback, Input

import wsexec
from ui_base import UIbase


class UIsetUser(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

    # initialize data (if any) and layout
    def Init(self) -> None:

        # CSS style for the DIV wrapper
        self.wrapperStyle = {
            "width": "fit-content",
            "border": "solid",
            "border-width": "1px",
            "float": "left",
        }

        # dropdown list contents
        cols, rows = wsexec.Query("get_usernames", [])  # type:ignore
        iv = cols.index("uid")
        iu = cols.index("username")
        ig = cols.index("groupname")
        aUsers = [{"value": r[iv], "label": f"{r[iu]} ({r[ig]})"} for r in rows]

        # layout
        # TODO: DON'T HARDCODE THE INITIALLY SELECTED USER!!!
        self.contents = [
            html.H3("Select LevSeqUser"),
            dcc.Dropdown(aUsers, value=5, id="dropdown_users", style={"width": "160px"}),
            html.Div(id="div_user_info"),
        ]

        return

    # callback: user list dropdown selection
    @callback(
        Input("dropdown_users", "value"),
        prevent_initial_call=False,
    )
    @staticmethod
    def selectUser(uid) -> None:
        print("UIsetMetadata callback...")

        # do nothing if the user-selection dropdown has no current value
        if uid is None:
            msg = ["Current user ID: (none)"]

        else:

            if flask.has_request_context():
                remoteIPaddr = str(flask.request.remote_addr)
                flask.session["uid"] = uid
            else:  # (this should not happen)
                remoteIPaddr = "?.?.?.?"

            # save the IP address in the database table of users
            wsexec.Query("save_user_ip", [uid, remoteIPaddr])

            # get user session config
            cols, rows = wsexec.Query("get_user_info", [uid])  # type:ignore
            flask.session["groupname"] = rows[0][cols.index("groupname")]

            msg = f"Current user ID: {uid}"

        # update UI state
        dash.set_props("div_user_info", dict(children=msg))

        # (we use dash.set_props instead of Output bindings)
        return
