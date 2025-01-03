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
from ui_expt_list import UIexptList
from ui_query import UIquery


class UIsetUser(UIbase):

    # class-scope (static) variables
    UserDict = {}

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "fit-content",
            "float": "left",
        }

        # dropdown list contents
        cols, rows = wsexec.Query("get_usernames", [])  # type:ignore
        iv = cols.index("uid")
        iu = cols.index("username")
        ig = cols.index("groupname")

        # layout
        aUsers = [{"value": r[iv], "label": f"{r[iu]} ({r[ig]})"} for r in rows]

        self.contents = [
            html.H3("Select LevSeqUser"),
            dcc.Dropdown(aUsers, id="UIsetUser::trigger", style={"width": "160px"}, optionHeight=20),
            html.Label("Current user ID:", htmlFor="div_uid", style={"display": "inline-block"}),
            html.Div(
                id="div_uid",
                children="(not selected)",
                style={"display": "inline-block", "margin-left": "4px"},
            ),
        ]

        return

    # callback: user list dropdown selection
    @callback(
        Input("UIsetUser::trigger", "value"),
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(uid) -> None:
        print("UIsetUser callback...")

        # do nothing if the user-selection dropdown has no current value
        if uid is None:
            msg = "(not selected)"

        else:

            # save user ID, user name, group ID, and group name in session variables
            cols, rows = wsexec.Query("get_user_info", [uid])  # type:ignore
            flask.session["uid"] = uid
            flask.session["uname"] = rows[0][cols.index("username")]
            flask.session["gid"] = rows[0][cols.index("gid")]
            flask.session["groupname"] = rows[0][cols.index("groupname")]

            # save the IP address in the database table of users
            remoteIPaddr = str(flask.request.remote_addr)
            wsexec.Query("save_user_ip", [uid, remoteIPaddr])

            msg = str(uid)

        # update UI state
        dash.set_props("div_uid", dict(children=msg))
        dash.set_props("UIsetUser::error", dict(value=""))

        # refresh the UI
        UIexptList.RefreshUserExperimentList()
        UIquery.RefreshTestQueryList
        dash.set_props("div_unload_experiment_info", dict(children=""))

        # (we use dash.set_props instead of Output bindings)
        return
