import plotly_express as px

from levseq_dash.app import global_strings as gs


def format_mutation_annotation(text):
    """
    This function will run on the annotations dataframe extracted from the data.
    Format the mutations to remove the underscore and stack them on top of each other up to 3
    mutations. If it's more than 3, set the annotation as 4Mut*
    """
    # dataframe text can be empty
    annotation = ""

    if isinstance(text, str):
        items = text.split("_")  # Split by underscore

        if len(items) < 4:
            annotation = "<br>".join(items)  # Stack them vertically
        else:
            cnt = len(items)
            annotation = f"{cnt}Mut*"

    return annotation


def creat_heatmap(df, plate_number, property, smiles):
    # Need to create a .copy() of the original df. Pandas did not like appending the columns
    # to the original later in the code here, and it raised many warnings.
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

    filtered_df = df[(df[gs.c_smiles] == smiles) & (df[gs.c_plate] == plate_number)].copy()
    filtered_df = filtered_df.fillna(0)

    # set up the well indices for the grid
    # well numbers on the X  , letters on the Y
    c_y_letters = "Y-L"
    c_x_numbers = "X-N"
    filtered_df[c_y_letters] = filtered_df[gs.c_well].str[0]
    filtered_df[c_x_numbers] = filtered_df[gs.c_well].str[1:].astype(int)

    # extract the required property
    heatmap_data = filtered_df.pivot(index=c_y_letters, columns=c_x_numbers, values=property)

    # extract the mutations data for the annotations
    # this has no formatting
    annotations_data = filtered_df.pivot(index=c_y_letters, columns=c_x_numbers, values=gs.c_substitutions)

    fig = px.imshow(
        heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        # aspect argument to "auto" will instead fill the plotting area with the heatmap, using non-square tiles
    )

    # format the annotations stacked and cluster into Mut* if more than some number
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

    # removing paddings and margins
    fig.update_layout(margin=dict(l=0, r=0, b=0))

    # put the color axes on the top
    fig.update_coloraxes(
        colorbar=dict(
            thickness=12,
            orientation="h",  # Horizontal color bar
            xanchor="center",  # Center it
        )
    )

    return fig


def creat_rank_plot(df, plate_number, smiles):
    # Need to create a .copy() of the original df. Pandas did not like appending the columns
    # to the original later in the code here, and it raised many warnings.
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

    # filter by smiles and plate
    filtered_df = df[(df[gs.c_smiles] == smiles) & (df[gs.c_plate] == plate_number)].copy()

    # Sort by 'fitness value'
    df_sorted = filtered_df.sort_values(by=gs.c_fitness_value, ascending=False).reset_index(drop=True)

    #  create rank column based on the sort (1-based index)
    c_rank = "Rank"
    df_sorted[c_rank] = df_sorted.index + 1

    # Assign colors by the data type
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
    variant_label = "Variant"
    variant_color = f"rgba(33, 102, 172, 1.0)"  # blue-ish

    # apply the color mapping to the values and put in new column
    c_colors = "color_groups"
    df_sorted[c_colors] = df_sorted[gs.c_substitutions].apply(lambda x: x if x in color_map else variant_label)

    # assign colors based on the dictionary
    # unpack the color_map dictionary and merge with the variant key-value pairs
    custom_discrete_color_map = {**color_map, variant_label: variant_color}

    # make the plot
    fig = px.scatter(
        df_sorted,
        x=c_rank,
        y=gs.c_fitness_value,
        labels={
            gs.c_fitness_value: "Fitness Value",
            gs.c_substitutions: "Substitutions",
            c_colors: "Data Type",
        },
        hover_data={gs.c_well: True, gs.c_substitutions: True, c_rank: True},
        color=c_colors,
        color_discrete_map=custom_discrete_color_map,
        # the legent shows the data based on the order it sees
        # I am overriding the ordering of the legend here so Variant shows first, then Parent then...
        category_orders={c_colors: [variant_label, "#PARENT#", "#LOW#", "#N.A.#", "-"]},
    )
    # Remove all margins
    fig.update_layout(margin=dict(l=0, r=0, b=0))
    return fig
