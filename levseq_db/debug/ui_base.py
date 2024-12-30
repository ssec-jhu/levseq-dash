#
# ui_base.py
#
# Notes:
#  Implements a base class for UI units (Dash control layout and exception handling).
#
#  To make this work, a class derived from UIbase must do the following:
#
#  - Set the "id" property of the Dash component that triggers the callback to
#    "<classname>::trigger".
#
#  - Use dash.set_prop() instead of binding to Output component properties.  (Both
#     the callback and exception-handler methods must return None.)
#
# We wrap the layout defined in a derived class inside an HTML DIV in order to add
#  a Dash Textarea that can display error text.
#

import re
import dash
from dash import html, ctx


# implements a "unit" of user interface interaction whose contents are...
#  - wrapped by an HTML DIV
#  - initialized by Init()
#  - laid out as defined by Layout()
class UIbase:

    def __init__(self, _baseName):
        self.baseName = _baseName
        self.outerStyle = {"width": "fit-content"}
        self.wrapperStyle = {"width": "fit-content", "textAlign": "center"}

        self.contents = html.Div(
            id=f"{self.baseName}::placeholder",
            children=f"({self.baseName}::placeholder)",
            style=self.wrapperStyle,
        )

    # initialize bound data and layout
    def Init(self) -> None:
        return

    # return layout
    def Layout(self) -> html.Div:

        print(f"Layout: {self.baseName}")

        inner = [
            html.Div(
                id=f"{self.baseName}::contents",
                children=self.contents,
                style=self.wrapperStyle,
            ),
            html.Textarea(id=f"{self.baseName}::error", style={"width": "auto"}),
        ]

        return html.Div(id=f"{self.baseName}", children=inner, style=self.outerStyle)

    # try to clean the specified Exception string representation
    @staticmethod
    def getExceptionText(ex: Exception) -> list[str]:

        # convert embedded newline markers in the Exception string to HTML markup
        aLines = re.split(r"\n|\\n", str(ex))

        # if we have only one line of text, return the repr (which includes the python exception name)
        if len(aLines) == 1:
            aLines = [ex.__repr__()]

        return aLines

    @staticmethod
    def callbackException(ex: Exception) -> None:
        print("callbackException")

        # emit exception text
        aText = "\n".join(UIbase.getExceptionText(ex))

        # put error text into the corresponding Textarea
        baseName = ctx.triggered_id.split("::")[0]
        dash.set_props(f"{baseName}::error", dict(value=aText))

        # callbacks must not bind to Output properties (use dash.set_props() instead)
        return None

    # scrape the entire Dash app layout for the component that triggered the callback exception
    #  (we don't use this here, but maybe it will come in handy someday)
    #
    # (call like this:  UIbase.getTriggeredComponent(dash.get_app().layout))
    # @staticmethod
    # def getTriggeredComponent(p):
    #     rval = None

    #     if isinstance(p, list):
    #         for c in p:
    #             rval = UIbase.getTriggeredComponent(c)
    #             if rval is not None:
    #                 return rval

    #     if "id" in p.__dict__:
    #         if p.__getattribute__("id") == ctx.triggered_id:
    #             return p

    #     if "children" in p.__dict__:
    #         ac = p.__getattribute__("children")
    #         if ac is not None and not isinstance(ac, str):
    #             for c in ac:
    #                 rval = UIbase.getTriggeredComponent(c)
    #                 if rval is not None:
    #                     return rval

    #     return rval
