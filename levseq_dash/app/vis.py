import pandas as pd
import plotly_express as px
from dash import html
from dash_iconify import DashIconify

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

border_row = {"border": "0px solid blue"}
border_column = {"border": "0px solid red"}
border_card = {"border": "0px solid cyan"}
border_table = {"border": "0px solid magenta"}
card_shadow = {"box-shadow": "1px 2px 7px 0px grey", "border-radius": "5px"}

top_card_head = "card-title fw-bold custom-card-header"
top_card_body = "text-primary-emphasis"

# --------------------
#   Icons
# --------------------
MEDIUM = 20
SMALL = 16

icon_del_exp = html.I(
    DashIconify(icon="fa-solid:trash", height=SMALL, width=SMALL),
    # style={"margin-right": "8px"} # add the margin if there is text next to it
    # style={"color": "var(--bs-danger)"}
)
icon_go_to_next = html.I(
    DashIconify(icon="fa-solid:chart-line", height=SMALL, width=SMALL), style={"margin-left": "8px"}
)
icon_home = DashIconify(icon="fa-solid:home", width=20)
icon_upload = DashIconify(icon="fa-solid:upload", width=20)
# icon_eye_open = DashIconify(icon="mdi-light:eye-outline", width=20)  # mdi:eye #fa6-solid:eye
# icon_eye_closed = DashIconify(icon="mdi-light:eye-off-outline", width=20)  # mdi:eye #fa6-solid:eye


# --------------------
#   AGGrid Cell colorings
# --------------------
def data_bars_colorscale(df, column):
    """
    colors the bars in the cells in the table
    color max and min is based on the column values max and min
    uses color scale

    """
    # this doesn't use the mean value as the center of the coloring
    n_bins = 200
    min_value = df[column].min()
    max_value = df[column].max()

    # Generate color scale from Plotly
    color_scale = px.colors.sample_colorscale(px.colors.diverging.RdBu, [i / n_bins for i in range(n_bins)])
    # rdbu goes from blue to red, I want it the other way
    color_scale.reverse()

    # color_scale = px.colors.sample_colorscale(color_scale, [i / n_bins for i in range(n_bins)])

    # Convert to RGBA with transparency
    alpha = 1.0
    color_scale = [color.replace("rgb", "rgba").replace(")", f", {alpha})") for color in color_scale]

    styles = []
    for i in range(1, n_bins + 1):
        ratio_min = min_value + (i - 1) * (max_value - min_value) / n_bins
        ratio_max = min_value + i * (max_value - min_value) / n_bins
        max_bound_percentage = (i / n_bins) * 100
        color = color_scale[i - 1]  # Pick color from scale

        if max_bound_percentage > 89:
            text_color = "white"
        else:
            text_color = "black"
        styles.append(
            {
                "condition": f"params.value >= {ratio_min}" + (f" && params.value < {ratio_max}" if i < n_bins else ""),
                "style": {
                    "background": f"""
                        linear-gradient(90deg,
                        {color} 0%,
                        {color} {max_bound_percentage}%,
                        white {max_bound_percentage}%,
                        white 100%)
                    """,
                    "color": text_color,
                },
            }
        )

    return styles


def data_bars_group_mean_colorscale(
    df, value_col="ratio", min_col="min_group", max_col="max_group", color_scale=px.colors.diverging.RdBu
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
