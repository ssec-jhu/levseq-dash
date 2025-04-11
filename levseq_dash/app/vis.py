import ast

import pandas as pd
import plotly_express as px
from dash import html
from dash_iconify import DashIconify
from dash_molstar.utils import molstar_helper
from dash_molstar.utils.representations import Representation

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
seq_match_table_height = "650px"
seq_match_protein_viewer_height = "700px"
seq_match_card_height = (
    "850px"  # this number must be seq_match_table_height + any text written above the table or viewer
)

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
icon_home = DashIconify(icon="fa-solid:home", width=MEDIUM)
icon_upload = DashIconify(icon="fa-solid:upload", width=MEDIUM)
icon_menu = DashIconify(icon="fa-solid:bars", width=MEDIUM)
icon_info = html.I(
    DashIconify(icon="fa6-solid:circle-info", height=SMALL, width=SMALL),
    # style={"color": "var(--bs-info)"}
)
icon_sequence = DashIconify(icon="fa-solid:dna", width=MEDIUM)
icon_download = DashIconify(icon="mdi:tray-download", height=MEDIUM, width=MEDIUM)


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


def get_molstar_rendered_components_seq_alignment(
    hot_residue_indices_list, cold_residue_indices_list, substitution_residue_list
):
    """
    Generate Dash Molstar components for each of the  list of indices
    """

    mismatch_residues = list(map(int, ast.literal_eval(substitution_residue_list)))
    hot_residues = list(map(int, ast.literal_eval(hot_residue_indices_list)))
    cold_residues = list(map(int, ast.literal_eval(cold_residue_indices_list)))

    # extract the residues that are both in hot and cold groups and isolate the others out
    both_hs_and_cs = list(set(hot_residues).intersection(set(cold_residues)))
    hs_only = [item for item in hot_residues if item not in both_hs_and_cs]
    cs_only = [item for item in cold_residues if item not in both_hs_and_cs]

    # make the representations
    # main chain
    rep_cartoon_gray = Representation(type="cartoon", color="uniform")
    rep_cartoon_gray.set_type_params({"alpha": 0.5})

    # hot spots
    rep_hot = Representation(type="cartoon", color="uniform", size="uniform")
    rep_hot.set_color_params({"value": 0xC41E3A})
    rep_hot.set_size_params({"value": 1.15})

    # cold spots
    rep_cold = Representation(type="cartoon", color="uniform", size="uniform")
    rep_cold.set_color_params({"value": 0x0047AB})
    rep_cold.set_size_params({"value": 1.5})

    # both hot and cold
    rep_hot_cold = Representation(type="cartoon", color="uniform", size="uniform")
    rep_hot_cold.set_color_params({"value": 0xB57EDC})
    rep_hot_cold.set_size_params({"value": 1.5})

    # mismatches
    rep_mismatches = Representation(type="ball-and-stick")

    main_chain = molstar_helper.get_targets(chain="A")
    hot_residue = molstar_helper.get_targets(chain="A", residue=hs_only)
    # analyse = molstar_helper.get_focus(hot_residue, analyse=True)
    analyse = molstar_helper.get_focus(main_chain, analyse=False)
    cold_residue = molstar_helper.get_targets(chain="A", residue=cs_only)
    both_hot_and_cold_residue = molstar_helper.get_targets(chain="A", residue=both_hs_and_cs)
    mismatch_residue = molstar_helper.get_targets(chain="A", residue=mismatch_residues)

    component_main_chain = molstar_helper.create_component(
        label="main", targets=main_chain, representation=rep_cartoon_gray
    )
    component_hot_residue = molstar_helper.create_component(
        label=gs.cc_hot_indices_per_cas, targets=hot_residue, representation=rep_hot
    )
    component_cold_residue = molstar_helper.create_component(
        label=gs.cc_cold_indices_per_cas, targets=cold_residue, representation=rep_cold
    )
    component_both_residue = molstar_helper.create_component(
        label=gs.cc_hot_and_cold_indices_per_cas, targets=both_hot_and_cold_residue, representation=rep_hot_cold
    )
    component_mismatch_residue = molstar_helper.create_component(
        label=gs.c_substitutions, targets=mismatch_residue, representation=rep_mismatches
    )
    return [
        component_main_chain,
        component_hot_residue,
        component_cold_residue,
        component_both_residue,
        component_mismatch_residue,
    ]


def get_molstar_rendered_components_related_variants(substitution_residue_list):
    """ """

    sub_residues_list = list(map(int, substitution_residue_list))

    # make the representations
    # main chain
    rep_by_seq_id = Representation(type="cartoon", color="sequence-id")
    rep_by_seq_id.set_type_params({"alpha": 0.5})

    rep_uniform_red = Representation(type="cartoon", color="uniform", size="uniform")
    rep_uniform_red.set_color_params({"value": 0xC41E3A})
    rep_uniform_red.set_size_params({"value": 1.15})

    rep_ball_stick = Representation(type="ball-and-stick")

    main_chain = molstar_helper.get_targets(chain="A")
    analyse = molstar_helper.get_focus(main_chain, analyse=False)
    sub_residue = molstar_helper.get_targets(chain="A", residue=sub_residues_list)

    component_main_chain = molstar_helper.create_component(
        label="main", targets=main_chain, representation=rep_by_seq_id
    )

    component_sub_residue = molstar_helper.create_component(
        label=gs.c_substitutions, targets=sub_residue, representation=rep_uniform_red
    )
    component_sub_residue_2 = molstar_helper.create_component(
        label=f"{gs.c_substitutions}_2", targets=sub_residue, representation=rep_ball_stick
    )
    return [component_main_chain, component_sub_residue, component_sub_residue_2]
