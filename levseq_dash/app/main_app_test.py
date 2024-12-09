# TODO: delete this file before making the repo public

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html, no_update

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

# Create Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, dbc_css],
)

server = app.server

app.layout = html.Div(
    [
        html.Div(style={"margin-bottom": "40px"}),
        html.Div(
            [
                dbc.Button(
                    children="Click me",
                    color="primary",
                    id="id-button",
                    n_clicks=0,
                ),
            ],
            className="d-grid gap-2 col-6 mx-auto",
        ),
        html.Div(id="output", style={"margin-top": "20px", "font-size": "20px"}),
    ]
)


@app.callback(Output("output", "children"), Input("id-button", "n_clicks"))
def on_button_click(n_clicks):
    if n_clicks > 0:
        # you run whatever python code you want here
        # and return whatever you want in the string
        my_string = "Yay! Click worked. You can dump any string output here."
        return my_string

    else:
        return no_update


if __name__ == "__main__":
    app.run_server(debug=True)
