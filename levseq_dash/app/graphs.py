import numpy as np
import pandas as pd
import plotly_express as px
import regex as re

from levseq_dash.app import global_strings as gs


def creat_heatmap(df, plate_number, property_stat, cas_number):
    # Need to create a .copy() of the original df. Pandas did not like appending the columns
    # to the original later in the code here, and it raised many warnings.
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

    filtered_df = df[(df[gs.c_cas] == cas_number) & (df[gs.c_plate] == plate_number)].copy()

    # set up the well indices for the grid
    filtered_df["X-L"] = filtered_df[gs.c_well].str[0]
    filtered_df["Y-N"] = filtered_df[gs.c_well].str[1:].astype(int)

    heatmap_data = filtered_df.pivot(index="Y-N", columns="X-L", values=property_stat)

    annotations_data = filtered_df.pivot(index="Y-N", columns="X-L", values=gs.mutations)

    fig = px.imshow(
        heatmap_data.values,
        # labels=dict(x="testing", y="", color="Values"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="Viridis",  # uncomment to pickup the dbc tempalte
        # color_continuous_scale="RdBu_r",
        aspect="auto",
        # aspect argument to "auto" will instead fill the plotting area with the heatmap, using non-square tiles
    )
    # annotations_data = annotations_data.applymap(lambda x: x.replace("_", " "))
    annotations_data = annotations_data.map(lambda x: x.replace("_", ", ").replace(" ", "<br>", 1))
    # formatted_text = annotations_data.applymap(lambda x: f"<b>{x}</b>" if "#PARENT#" in x else x)

    fig.update_traces(
        text=annotations_data,
        # text=formatted_text.values,
        texttemplate="%{text}",
        textfont_size=10,
        hovertemplate="<b>Value</b>: %{z}<br>" + "<b>Well</b>: %{x}%{y}<br>",
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(len(heatmap_data.columns))),  # Tick positions
        ticktext=heatmap_data.columns,  # Custom tick labels (letters A-H)
    )
    fig.update_yaxes(
        tickmode="array",
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # list(range(len(heatmap_data.index))),  # Tick positions
        ticktext=heatmap_data.index,  # Custom tick labels (numbers 1-12, reversed)
    )
    # fig.update_xaxes(visible=False)
    # fig.update_yaxes(visible=False)

    # removing paddings
    fig.update_layout(
        margin=dict(l=0, r=0, b=0),  # Set all margins to 0
        # width=500,  # Adjust figure width
        height=600,  # Adjust figure height
        xaxis_title="",
        yaxis_title="",
        template=gs.dbc_template_name,
    )
    fig.update_coloraxes(colorbar=dict(thickness=10, xpad=0))  # shrink the axes on the right
    # fig.update_coloraxes(showscale=False)
    # fig.update_layout(autosize=False)  # TODO: do I need this

    fig.show()
    # # #####
    # # Create the surface plot using Plotly Express
    # filtered_df_2 = df[(df[gs.c_cas] == cas_number) & (df[gs.c_plate] == plate_number)]
    # filtered_df_2 = filtered_df_2.fillna(0)
    # selected_columns = filtered_df_2[["x_coordinate", "y_coordinate", "fitness_value"]]
    #
    # z = filtered_df.pivot(index="y_coordinate", columns="x_coordinate", values="fitness_value").values
    # #x = np.sort(df["X"].unique())
    # #y = np.sort(df["Y"].unique())
    # # fig = px.imshow(
    #     z,
    #     x="x_coordinate",
    #     y="y_coordinate",
    #     color_continuous_scale="Viridis",
    #     labels={"x": "X Coordinates", "y": "Y Coordinates", "color": "Fitness"},
    # )
    # fig.show()
    #
    # # Update layout for better aesthetics
    # fig.update_layout(
    #     title="Surface Plot of Fitness",
    #     margin=dict(l=0, r=0, t=50, b=0),
    # )
    #
    # # Customize hover template
    # fig.update_traces(
    #     hovertemplate="X: %{x}<br>Y: %{y}<br>Fitness: %{z}<extra></extra>"
    # )
    #
    # # Show the plot
    # fig.show()
    #
    #
    # # Show the plot
    # fig.show()

    #####

    return fig


def is_valid_format(s):
    return bool(re.fullmatch(r"[A-Za-z]\d+[A-Za-z]", s))

    # Helper function to extract numbers from valid strings


def extract_numbers(s):
    match = re.findall(r"\d+", s)
    return "_".join(match) if match else "NoNumbers"


def create_sunburst(df):
    # Sor on fitness
    sorted_by_fitness = df.sort_values(by="fitness_value", ascending=False)

    # Extract the top 20 rows
    top_fitness_values = sorted_by_fitness[
        ["cas_number", "plate", "well", "amino_acid_substitutions", "fitness_value"]
    ].head(200)

    # Process data to create hierarchical relationships
    processed_data = []
    # for item in data:
    for _, row in top_fitness_values.iterrows():
        item = row["amino_acid_substitutions"]
        if "#" not in item:
            components = item.split("_")
            components = [c for c in components if is_valid_format(c)]  # Keep only valid components
            n_components = len(components)  # Number of valid components in the string
            for component in components:
                numeric_part = extract_numbers(component)
                processed_data.append(
                    {
                        "Index": int(numeric_part),
                        "Group Size": f"PairingSize={n_components}",
                        "Combination": item,  # "_".join(components),
                        "Fitness": row["fitness_value"],
                    }
                )

    # Convert processed data to a DataFrame for sunburst and treemap charts
    df_hierarchy = pd.DataFrame(processed_data)

    pairing_size = df_hierarchy.groupby("Group Size")["Index"].transform("count")
    df_hierarchy["pairing_size"] = pairing_size

    df_hierarchy = df_hierarchy.sort_values(by="Index", ascending=True)
    fig_sunburst_color_by_fitness = px.sunburst(
        df_hierarchy,
        title=" colored by fitness",
        path=["Index", "Group Size", "Combination"],  # Hierarchical path
        color="Fitness",
        color_continuous_scale="RdBu",
        # values="Group Size",
        # color_discrete_map={'5': 'black', '1': 'gold'}
        # title="Hierarchical Relationships by Index (Sunburst)"
        # to use with the custom colors
        # color="Custom Color",  # Use the custom color column
    )
    fig_sunburst_color_by_fitness.update_traces(sort=False, selector=dict(type="sunburst"))
    # ------------------------------
    fig_sunburst_no_index = px.sunburst(
        df_hierarchy,
        title=" colored by fitness - no index",
        path=["Group Size", "Combination"],  # Hierarchical path
        color_continuous_scale="RdBu",
        color="Fitness",
    )
    fig_sunburst_no_index.update_traces(sort=False, selector=dict(type="sunburst"))
    # ------------------------------
    fig_sunburst_color_by_paring = px.sunburst(
        df_hierarchy,
        title=" colored by pairing size",
        path=["Index", "Group Size", "Combination"],  # Hierarchical path
        color_continuous_scale="RdBu",
        color="pairing_size",  # Use the count of items for coloring
    )
    # ------------------------------

    fig_ice_color_by_paring = px.icicle(
        df_hierarchy,
        title=" same as previous: colored by pairing size",
        path=["Index", "Group Size", "Combination"],  # Hierarchical path
        # color="count",
        # color_continuous_scale="RdBu",
        color="pairing_size",  # Use the count of items for coloring
        color_continuous_scale="RdBu",  # Customize the color scale
    )
    fig_ice_color_by_paring.update_traces(root_color="lightblue")  # Set root node's color explicitly

    # ------------------------------

    # size_counts = df_hierarchy.groupby("Index")["Group Size"].nunique()
    size_counts_2 = df_hierarchy.groupby("Index")["Group Size"].nunique().reset_index(name="Unique Group Sizes")
    # Merge back to the original DataFrame
    df_hierarchy_with_group_counts = df_hierarchy.merge(size_counts_2, on="Index", how="left")
    fig_sunburst_color_by_group_size = px.sunburst(
        df_hierarchy_with_group_counts,
        title=" colored by unique group size",
        path=["Index", "Group Size", "Combination"],  # Hierarchical path
        # color="Fitness",
        color_continuous_scale="Blues",
        color="Unique Group Sizes",  # Use the count of items for coloring
    )
    fig_sunburst_color_by_group_size_ice = px.icicle(
        df_hierarchy_with_group_counts,
        title=" colored by unique group size",
        path=["Index", "Group Size", "Combination"],  # Hierarchical path
        # color="Fitness",
        color_continuous_scale="Blues",
        color="Unique Group Sizes",  # Use the count of items for coloring
    )

    # fig_sunburst_color_by_fitness.show()
    # fig_sunburst_no_index.show()
    # fig_sunburst_color_by_paring.show()
    # fig_ice_color_by_paring.show()
    fig_sunburst_color_by_group_size.show()
    fig_sunburst_color_by_group_size_ice.show()


# from levseq_dash.app.tests.conftest import experiment_ep_example
#
# # create_sunburst(experiment_ep_example.data_df)
#
# creat_heatmap(df=experiment_ep_example.data_df,
#               plate_number=experiment_ep_example.plates[0],
#               property_stat=gs.stat_list[0],
#               cas_number=experiment_ep_example.cas_unique_values[0])
