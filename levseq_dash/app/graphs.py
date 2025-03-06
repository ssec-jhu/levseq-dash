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

    # filter by cas and plate
    filtered_df = df[(df[gs.c_cas] == cas_number) & (df[gs.c_plate] == plate_number)].copy()

    # Sort by 'fitness value'
    df_sorted = filtered_df.sort_values(by=gs.c_fitness_value, ascending=False).reset_index(drop=True)

    # Create a rank column (1-based index)
    df_sorted["rank"] = df_sorted.index + 1

    # color by type
    # color_scale = px.colors.sample_colorscale(px.colors.diverging.RdBu, 96)
    # RGB colr values are extracted from px.colors.diverging.RdBu,
    # but hard coding them for convenience we don't have to sample everytime
    # https://app.py.cafe/app/nataliatsyporkin/plotly-colorscale-selection
    color_map = {
        "#PARENT#": "rgba(178,24,43,1)",  # red-ish
        "#N.A.#": "rgba(128,128,128,0.4)",  # gray-ish
        "#LOW#": "rgba(128,128,128,0.6)",  # gray-ish
        "-": "rgba(0,0,0,1)",  # black
    }
    mutations_label = "variant"
    mutations_color = f"rgba(33, 102, 172, 1.0)"  # blue-ish
    df_sorted["color_groups"] = df_sorted[gs.c_substitutions].apply(lambda x: x if x in color_map else mutations_label)

    fig = px.scatter(
        df_sorted,
        x="rank",
        y=gs.c_fitness_value,
        labels={
            "rank": "Rank",
            gs.c_fitness_value: "Fitness Value",
            gs.c_substitutions: "Substitutions",
            "color_groups": "Data",
            "other_color": "other",
        },
        hover_data={gs.c_well: True, gs.c_substitutions: True, "rank": True},
        color="color_groups",
        # setting a bit of ap=alpha on the gray here so the text is legible
        color_discrete_map={**color_map, mutations_label: mutations_color},
    )

    fig.update_layout(margin=dict(l=0, r=0, b=0))  # Remove all margins
    return fig
