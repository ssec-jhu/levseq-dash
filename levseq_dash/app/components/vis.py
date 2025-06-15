import pandas as pd
import plotly_express as px
from dash_iconify import DashIconify

from levseq_dash.app import global_strings as gs

# --------------------
#   Inline styles
# --------------------
upload_default = {
    "borderWidth": "1px",
    "borderStyle": "dashed",
    "padding": "10px",
    "textAlign": "center",
    "cursor": "pointer",
}
upload_success = success_style = {
    "borderWidth": "4px",
    "borderStyle": "dashed",
    "padding": "10px",
    "textAlign": "center",
    "cursor": "pointer",
    "borderColor": "green",
}

# Sequence Match table and the protein viewer need to have close height
# seq_match_card_height number must be seq_match_table_height + any text written above the table or viewer
seq_match_table_height = "650px"
seq_match_protein_viewer_height = "600px"
seq_match_card_height = "850px"

# related variants of an experiment table and protein viewer need to have close height
# it depends on components above the table and or the viewer
related_variants_table_height = "750px"
related_protein_viewer_height = "600px"

border_row = {"border": "0px solid blue"}
border_column = {"border": "0px solid red"}
border_card = {"border": "0px solid cyan"}
border_table = {"border": "0px solid magenta"}
card_shadow = {"box-shadow": "1px 2px 7px 0px grey", "border-radius": "5px"}
section_vis = {"visibility": "hidden", "height": "70px"}
display_block = {"display": "block"}
display_none = {"display": "none"}

top_card_head = "card-title fw-bold custom-card-header"
top_card_body = "text-primary-emphasis"

experiment_info = {"fontWeight": "bold", "marginRight": "15px"}

# level_4_titles = {"color": "var(--cal-tech-color-2)"}
main_page_class = "p-4"  # this will align all titles and location the pages in the same location

# --------------------
#   Icons
# --------------------


# Font Awesome 6 Solid: https://icon-sets.iconify.design/fa6-solid/
LARGE = 50
MEDIUM = 20
SMALL = 16
icon_home = "fa6-solid:house"
icon_menu = "fa6-solid:bars"
icon_upload = "fa6-solid:upload"
icon_download = "fa6-solid:download"
icon_info = "fa6-solid:circle-info"
icon_sequence = "fa6-solid:dna"
icon_search = "fa6-solid:magnifying-glass"
icon_about = "fa6-solid:circle-question"
icon_del_exp = "fa6-solid:trash-can"
icon_go_to_next = "fa6-solid:circle-chevron-right"
icon_database = "fa6-solid:database"


# # Material Symbols Light https://icon-sets.iconify.design/material-symbols-light/
# LARGE = 80
# MEDIUM = 30
# SMALL = 16
# icon_home = "material-symbols:home-rounded"  # can add -rounded
# icon_menu = "material-symbols:menu-rounded"  # -rounded
# icon_upload = "material-symbols:upload-rounded"  # -rounded or -sharp
# icon_download = "material-symbols:download-rounded"  # -rounded or -sharp
# icon_info = "material-symbols:info-rounded"  # -rounded
# icon_sequence = "material-symbols:genetics-rounded"  # -rounded
# icon_search = "material-symbols:search-rounded"  # -rounded
# icon_about = "material-symbols:help-rounded"  # -rounded
# icon_del_exp = "material-symbols:delete-forever-rounded"
# icon_go_to_next = "material-symbols:chevron-right-rounded"  # -rounded
# icon_database = "material-symbols:database-outline-rounded"


def get_icon(icon_string, size=MEDIUM):
    return DashIconify(icon=icon_string, width=size)


# --------------------
#   AGGrid Cell colorings
# --------------------
# def data_bars_colorscale(df, column):
#     """
#     colors the bars in the cells in the table
#     color max and min is based on the column values max and min
#     uses color scale
#
#     """
#     # this doesn't use the mean value as the center of the coloring
#     n_bins = 200
#     min_value = df[column].min()
#     max_value = df[column].max()
#
#     # Generate color scale from Plotly
#     color_scale = px.colors.sample_colorscale(px.colors.diverging.RdBu, [i / n_bins for i in range(n_bins)])
#     # rdbu goes from blue to red, I want it the other way
#     color_scale.reverse()
#
#     # color_scale = px.colors.sample_colorscale(color_scale, [i / n_bins for i in range(n_bins)])
#
#     # Convert to RGBA with transparency
#     alpha = 1.0
#     color_scale = [color.replace("rgb", "rgba").replace(")", f", {alpha})") for color in color_scale]
#
#     styles = []
#     for i in range(1, n_bins + 1):
#         ratio_min = min_value + (i - 1) * (max_value - min_value) / n_bins
#         ratio_max = min_value + i * (max_value - min_value) / n_bins
#         max_bound_percentage = (i / n_bins) * 100
#         color = color_scale[i - 1]  # Pick color from scale
#
#         if max_bound_percentage > 89:
#             text_color = "white"
#         else:
#             text_color = "black"
#         styles.append(
#             {
#                 "condition": f"params.value >= {ratio_min}" +
#                              (f" && params.value < {ratio_max}" if i < n_bins else ""),
#                 "style": {
#                     "background": f"""
#                         linear-gradient(90deg,
#                         {color} 0%,
#                         {color} {max_bound_percentage}%,
#                         white {max_bound_percentage}%,
#                         white 100%)
#                     """,
#                     "color": text_color,
#                 },
#             }
#         )
#
#     return styles


def data_bars_group_mean_colorscale(
    df, value_col=gs.cc_ratio, min_col="min_group", max_col="max_group", color_scale=px.colors.diverging.RdBu
):
    """
    Generate Dash AG Grid cell styles with a color gradient bar.
    """

    styles = []
    n_bins = 96
    color_scale = px.colors.sample_colorscale(px.colors.diverging.RdBu, [i / n_bins for i in range(n_bins)])
    color_scale.reverse()

    # Normalize function for color scale mapping
    def normalize(value, min_val, max_val):
        return (value - min_val) / (max_val - min_val) if max_val - min_val != 0 else 0.5  # Avoid div by zero

    # Get color scale range (from -1 to 1)
    n_colors = len(color_scale)

    for _, row in df.iterrows():
        ratio = row[value_col]
        min_value = row[min_col]
        max_value = row[max_col]

        if pd.isna(ratio) or pd.isna(min_value) or pd.isna(max_value):
            continue  # Skip missing values

        # Normalize value to range (0, 1) for color mapping
        norm_ratio = normalize(ratio, min_value, max_value)
        color_index = int(norm_ratio * (n_colors - 1))  # Scale to color map index
        bar_color = color_scale[color_index]  # Pick color from scale

        # Determine bar width
        bar_width = int(norm_ratio * 100)  # Convert to percentage
        if bar_width > 89:
            text_color = "white"
        else:
            text_color = "black"
        # Define bar style using CSS linear gradient
        background_style = f"""
            linear-gradient(90deg,
            {bar_color} 0%,
            {bar_color} {bar_width}%,
            white {bar_width}%,
            white 100%)
        """

        styles.append(
            {
                "condition": f"params.value == {ratio}",
                "style": {
                    "background": background_style,
                    "color": text_color,
                    # "textAlign": "center",
                },
            }
        )

    return styles
