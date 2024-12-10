import dash_bootstrap_components as dbc
from dash import Dash
from dash_bootstrap_templates import load_figure_template

from levseq_dash.app import layout_upload
from levseq_dash.app import global_strings as gs

# Initialize the app
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(
    __name__,
    title=gs.web_title,
    external_stylesheets=[dbc.themes.FLATLY, dbc_css, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

# VERY important line of code for running with gunicorn
# you run the 'server' not the 'app'. VS. you run the 'app' with uvicorn
server = app.server

load_figure_template(gs.dbc_template_name)
# Define the form layout


app.layout = dbc.Container(
    [layout_upload.upload_form_layout],
    # fluid=True,
)
# Run the app
if __name__ == "__main__":
    app.run()
