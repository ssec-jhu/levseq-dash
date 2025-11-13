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
seq_match_table_height = "75vh"  # 75% of the viewport
seq_match_protein_viewer_height = "55vh"
seq_match_card_height = "95vh"  # 95% of the viewport, 100 is too tight

# related variants of an experiment table and protein viewer need to have close height
# it depends on components above the table and or the viewer
related_variants_table_height = "65vh"
related_protein_viewer_height = "65vh"

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
main_page_class = "p-1"  # this will align all titles and location the pages in the same location

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


def get_icon(icon_string, size=MEDIUM):
    """
    Create a Dash Iconify icon component.

    Args:
        icon_string: Icon identifier string (e.g., 'fa6-solid:house').
        size: Icon size in pixels (default: MEDIUM).

    Returns:
        DashIconify: Configured icon component.
    """
    return DashIconify(icon=icon_string, width=size)


def data_bars_group_mean_colorscale(
    df,
    value_col=gs.cc_ratio,
    min_col="min_group_ratio",
    max_col="max_group_ratio",
):
    """
    Generate AG Grid cell styles with color gradient bars for ratio visualization.

    Creates conditional cell styles with background color gradients based on normalized
    ratio values, using min/max values for proper scaling.

    Args:
        df: DataFrame containing the data.
        value_col: Column name for ratio values (default: gs.cc_ratio).
        min_col: Column name for minimum group ratio (default: 'min_group_ratio').
        max_col: Column name for maximum group ratio (default: 'max_group_ratio').

    Returns:
        list: List of style dictionaries for AG Grid cellClassRules.
    """

    styles = []

    # Fast early return if required columns don't exist or are entirely null
    if value_col not in df.columns or min_col not in df.columns or max_col not in df.columns:
        return styles

    # Fast check: if the entire ratio column is null/NaN, return empty styles
    if df[value_col].isna().all() or df[value_col].isnull().all():
        return styles

    # Also check if min/max columns are entirely null, which would make coloring meaningless
    if df[min_col].isna().all() or df[max_col].isna().all():
        return styles

    if gs.hashtag_parent not in df[gs.c_substitutions].values:
        return styles

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
