import numpy as np
import plotly_express as px

from levseq_dash.app import global_strings as gs


def format_mutation_annotation(text):
    """
    This function will run on the annotations dataframe extracted from the data.
    Format the mutations to remove the underscore and stack them on top of each other up to 3
    mutations. If it's more than 3, set the annotation as 4Mut*
    """
    items = text.split("_")  # Split by underscore

    if len(items) < 4:
        return "<br>".join(items)  # Stack them vertically
    else:
        cnt = len(items)
        annotation = f"{cnt}Mut*"
        return annotation


def creat_heatmap(df, plate_number, property, cas_number):
    # Need to create a .copy() of the original df. Pandas did not like appending the columns
    # to the original later in the code here, and it raised many warnings.
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

    filtered_df = df[(df[gs.c_cas] == cas_number) & (df[gs.c_plate] == plate_number)].copy()
    filtered_df = filtered_df.fillna(0)

    # set up the well indices for the grid
    # well numbers on the Y  , letters on the X
    # filtered_df["X-L"] = filtered_df[gs.c_well].str[0]
    # filtered_df["Y-N"] = filtered_df[gs.c_well].str[1:].astype(int)
    # well numbers on the X  , letters on the Y
    filtered_df["Y-L"] = filtered_df[gs.c_well].str[0]
    filtered_df["X-N"] = filtered_df[gs.c_well].str[1:].astype(int)

    # extract the required property
    heatmap_data = filtered_df.pivot(index="Y-L", columns="X-N", values=property)

    # extract the mutations data for the annotations
    # this has no formatting
    annotations_data = filtered_df.pivot(index="Y-L", columns="X-N", values=gs.c_substitutions)

    fig = px.imshow(
        heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        # aspect argument to "auto" will instead fill the plotting area with the heatmap, using non-square tiles
    )
    annotations_data_stacked = annotations_data.map(format_mutation_annotation)

    # thought the text on the graph itself is stacked and stripped of the underscore
    # the hover data is the original annotations.
    hover_template = "Well: %{x}%{y}<br>Value: %{z}<br>Mut: %{customdata}"

    # Add annotations as hover data
    fig.update_traces(
        # text on the figure
        text=annotations_data_stacked,
        texttemplate="%{text}",
        textfont_size=10,
        # hover data
        hovertemplate=hover_template,
        customdata=annotations_data,
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(len(heatmap_data.index))),  # Tick positions
        ticktext=heatmap_data.index,
        ticks="outside",
    )
    fig.update_xaxes(
        tickmode="array",
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # list(range(len(heatmap_data.index))),  # Tick positions
        ticktext=heatmap_data.columns,
        ticks="outside",  # this adds a tick and distances the values from the axis
    )

    # removing paddings
    fig.update_layout(
        margin=dict(l=0, r=0, b=0),  # Remove all margins
        # height=600,  # Adjust figure height
        # xaxis_title="",
        # yaxis_title="",
        # template=gs.dbc_template_name,
        # paper_bgcolor="white",  # Set the figure background to white
        # plot_bgcolor="white",  # Remove plot background color
        # axis=dict(showgrid=False, zeroline=False, showticklabels=False),
        # yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    # shrink the axes if it's on the right
    # fig.update_coloraxes(colorbar=dict(thickness=10, xpad=0))

    # put the color axes on the top
    fig.update_coloraxes(
        colorbar=dict(
            thickness=12,
            orientation="h",  # Horizontal color bar
            xanchor="center",  # Center it
        )
    )

    return fig


def creat_rank_plot(df, plate_number, cas_number):
    # Need to create a .copy() of the original df. Pandas did not like appending the columns
    # to the original later in the code here, and it raised many warnings.
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

    filtered_df = df[(df[gs.c_cas] == cas_number) & (df[gs.c_plate] == plate_number)].copy()
    filtered_df = filtered_df.fillna(0)

    # Sort the DataFrame by 'fitness'
    df_sorted = filtered_df.sort_values(by=gs.c_fitness_value, ascending=False).reset_index(drop=True)

    # Create a rank column (1-based index)
    df_sorted["rank"] = df_sorted.index + 1

    fig = px.scatter(
        df_sorted,
        x="rank",
        y=gs.c_fitness_value,
        labels={"rank": "Rank", gs.c_fitness_value: "Fitness Value", gs.c_substitutions: "Substitutions"},
        # title="Ranked Fitness Plot",
        hover_data={gs.c_well: True, gs.c_substitutions: True, "rank": True},
        # TODO:
        #  do we want the size to be reflected or is the color enough?
        #  remember to remove the marker size below if you enable this
        # size="ratio",
        color="ratio",  # Maps colors to "ratio" values
        color_continuous_scale="RdBu_r",
    )

    # Identify parent points
    red_mask = df_sorted[gs.c_substitutions] == "#PARENT#"
    fig.update_traces(
        marker=dict(
            symbol=np.where(red_mask, "star", "circle"),  # different shape for parent, circle for others
            # TODO:
            #  do we want the size to be reflected or is the color enough?
            #  remember to remove the marker size below if you enable this
            size=12,
            line=dict(color="rgba(0.75, 0.75, 0.75, 1)", width=1),  # remove the white boundary
        )
    )

    fig.update_layout(margin=dict(l=0, r=0, b=0))  # Remove all margins
    return fig


# def is_valid_format(s):
#     return bool(re.fullmatch(r"[A-Za-z]\d+[A-Za-z]", s))

# def extract_numbers(s):
#     match = re.findall(r"\d+", s)
#     return "_".join(match) if match else "NoNumbers"
#
#
# def create_sunburst(df):
#     # Sor on fitness
#     sorted_by_fitness = df.sort_values(by="fitness_value", ascending=False)
#
#     # Extract the top 20 rows
#     top_fitness_values = sorted_by_fitness[
#         ["cas_number", "plate", "well", "amino_acid_substitutions", "fitness_value"]
#     ].head(200)
#
#     # Process data to create hierarchical relationships
#     processed_data = []
#     # for item in data:
#     for _, row in top_fitness_values.iterrows():
#         item = row["amino_acid_substitutions"]
#         if "#" not in item:
#             components = item.split("_")
#             components = [c for c in components if is_valid_format(c)]  # Keep only valid components
#             n_components = len(components)  # Number of valid components in the string
#             for component in components:
#                 numeric_part = extract_numbers(component)
#                 processed_data.append(
#                     {
#                         "Index": int(numeric_part),
#                         "Group Size": f"PairingSize={n_components}",
#                         "Combination": item,  # "_".join(components),
#                         "Fitness": row["fitness_value"],
#                     }
#                 )
#
#     # Convert processed data to a DataFrame for sunburst and treemap charts
#     df_hierarchy = pd.DataFrame(processed_data)
#
#     pairing_size = df_hierarchy.groupby("Group Size")["Index"].transform("count")
#     df_hierarchy["pairing_size"] = pairing_size
#
#     df_hierarchy = df_hierarchy.sort_values(by="Index", ascending=True)
#     fig_sunburst_color_by_fitness = px.sunburst(
#         df_hierarchy,
#         title=" colored by fitness",
#         path=["Index", "Group Size", "Combination"],  # Hierarchical path
#         color="Fitness",
#         color_continuous_scale="RdBu",
#         # values="Group Size",
#         # color_discrete_map={'5': 'black', '1': 'gold'}
#         # title="Hierarchical Relationships by Index (Sunburst)"
#         # to use with the custom colors
#         # color="Custom Color",  # Use the custom color column
#     )
#     fig_sunburst_color_by_fitness.update_traces(sort=False, selector=dict(type="sunburst"))
#     # ------------------------------
#     fig_sunburst_no_index = px.sunburst(
#         df_hierarchy,
#         title=" colored by fitness - no index",
#         path=["Group Size", "Combination"],  # Hierarchical path
#         color_continuous_scale="RdBu",
#         color="Fitness",
#     )
#     fig_sunburst_no_index.update_traces(sort=False, selector=dict(type="sunburst"))
#     # ------------------------------
#     fig_sunburst_color_by_paring = px.sunburst(
#         df_hierarchy,
#         title=" colored by pairing size",
#         path=["Index", "Group Size", "Combination"],  # Hierarchical path
#         color_continuous_scale="RdBu",
#         color="pairing_size",  # Use the count of items for coloring
#     )
#     # ------------------------------
#
#     fig_ice_color_by_paring = px.icicle(
#         df_hierarchy,
#         title=" same as previous: colored by pairing size",
#         path=["Index", "Group Size", "Combination"],  # Hierarchical path
#         # color="count",
#         # color_continuous_scale="RdBu",
#         color="pairing_size",  # Use the count of items for coloring
#         color_continuous_scale="RdBu",  # Customize the color scale
#     )
#     fig_ice_color_by_paring.update_traces(root_color="lightblue")  # Set root node's color explicitly
#
#     # ------------------------------
#
#     # size_counts = df_hierarchy.groupby("Index")["Group Size"].nunique()
#     size_counts_2 = df_hierarchy.groupby("Index")["Group Size"].nunique().reset_index(name="Unique Group Sizes")
#     # Merge back to the original DataFrame
#     df_hierarchy_with_group_counts = df_hierarchy.merge(size_counts_2, on="Index", how="left")
#     fig_sunburst_color_by_group_size = px.sunburst(
#         df_hierarchy_with_group_counts,
#         title=" colored by unique group size",
#         path=["Index", "Group Size", "Combination"],  # Hierarchical path
#         # color="Fitness",
#         color_continuous_scale="Blues",
#         color="Unique Group Sizes",  # Use the count of items for coloring
#     )
#     fig_sunburst_color_by_group_size_ice = px.icicle(
#         df_hierarchy_with_group_counts,
#         title=" colored by unique group size",
#         path=["Index", "Group Size", "Combination"],  # Hierarchical path
#         # color="Fitness",
#         color_continuous_scale="Blues",
#         color="Unique Group Sizes",  # Use the count of items for coloring
#     )
#
#     fig_sunburst_color_by_fitness.show()
#     fig_sunburst_no_index.show()
#     fig_sunburst_color_by_paring.show()
#     # fig_ice_color_by_paring.show()
#     fig_sunburst_color_by_group_size.show()
#     fig_sunburst_color_by_group_size_ice.show()


# from levseq_dash.app.tests.conftest import my_experimnet
#
# ratio_df = utils.calculate_group_mean_ratios_per_cas_and_plate(my_experimnet.data_df)
# creat_rank_plot(df=ratio_df,
#                 plate_number=my_experimnet.plates[1],
#                 property=gs.experiment_heatmap_properties_list[0],
#                 cas_number=my_experimnet.unique_cas_in_data[0])
