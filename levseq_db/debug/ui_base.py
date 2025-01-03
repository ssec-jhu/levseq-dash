#
# ui_base.py
#
# Notes:
#  Implements a base class for Dash control layout and exception handling.
#   The idea is to clump UI interactions together, with multiple display and
#   data-entry components bound to each Dash callback.
#
#  To make this work, a class derived from UIbase must do the following:
#
#  - Set the "id" property of the Dash component that triggers the callback to
#    "<classname>::trigger" or "<classname>--<additional_name>::trigger".  (See
#    the implementation of callbackException() below.)
#
#  - Use dash.set_prop() instead of binding to Output component properties.  (Both
#     the callback and exception-handler methods must return None.)
#
#  - Designate the Dash callback implementation as a static method (@staticmethod)
#
#  - [optionally] Use the general-purpose exception handler by using the following
#     parameter in the @callback decorator:
#       on_error=UIbase.callbackException
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
        self.innerStyle = {"width": "fit-content"}

        self.contents = html.Div(
            id=f"{self.baseName}::placeholder",
            children=f"({self.baseName}::placeholder)",
            style=self.innerStyle,
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
                style=self.innerStyle,
            ),
            html.Textarea(id=f"{self.baseName}::error", style={"width": "auto"}),
        ]

        return html.Div(id=f"{self.baseName}", className="UIbase", children=inner, style=self.outerStyle)

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
        print(f"callbackException: {ctx.triggered_id}")

        # emit exception text
        aText = "\n".join(UIbase.getExceptionText(ex))

        # extract the basename from the ID of the component that triggered the callback;
        #  (the ID must be formatted as "<basename>[--<other_characters>]::trigger")
        baseName = ctx.triggered_id.split("::")[0]  # type:ignore
        baseName = baseName.split("--")[0]

        # put error text into the corresponding Textarea; the Textarea id is
        dash.set_props(f"{baseName}::error", dict(value=aText))

        # callbacks must not bind to Output properties (use dash.set_props() instead)
        return None

    # Scrape the entire Dash app layout for the component with the specified "id" property
    #  value.
    #
    #  (we don't use this here, but maybe it will come in handy someday)
    #
    # @staticmethod
    # def FindDashComponentById(id: str):

    #     # we use a closure here to keep the specified string in scope without passing it
    #     #  as a parameter
    #     @staticmethod
    #     def getTriggeredComponent(p):
    #         rval = None

    #         if isinstance(p, list):
    #             for c in p:
    #                 rval = getTriggeredComponent(c)
    #                 if rval is not None:
    #                     return rval

    #         if "id" in p.__dict__:
    #             if p.__getattribute__("id") == id:
    #                 return p

    #         if "children" in p.__dict__:
    #             ac = p.__getattribute__("children")
    #             if ac is not None and not isinstance(ac, str):
    #                 for c in ac:
    #                     rval = getTriggeredComponent(c)
    #                     if rval is not None:
    #                         return rval

    #         return rval

    #     return getTriggeredComponent(dash.get_app().layout)
