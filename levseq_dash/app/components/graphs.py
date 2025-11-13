import re

import pandas as pd
import plotly.graph_objects as go
import plotly_express as px

from levseq_dash.app import global_strings as gs


def format_mutation_annotation(text):
    """
    Format mutation text for display in plot annotations.

    Removes underscores and stacks mutations vertically (up to 3).
    For more than 3 mutations, displays as 'NMut*' where N is the count.

    Args:
        text: Mutation string with underscores (e.g., 'A45S_D67F_L89P').

    Returns:
        str: Formatted annotation string with line breaks or mutation count.
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
    """
    Create a 96-well plate heatmap visualization.

    Generates a heatmap showing property values across plate wells with mutation annotations.

    Args:
        df: DataFrame containing experiment data.
        plate_number: Plate identifier to filter data.
        property: Column name for the property to visualize.
        smiles: SMILES string to filter data.

    Returns:
        go.Figure: Plotly heatmap figure with annotations.
    """
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
    """
    Create a scatter plot showing variants ranked by fitness value.

    Plots variants from highest to lowest fitness with color-coding for
    different data types (parent, variants, low quality, etc.).

    Args:
        df: DataFrame containing experiment data.
        plate_number: Plate identifier to filter data.
        smiles: SMILES string to filter data.

    Returns:
        go.Figure: Plotly scatter plot with ranked variants.
    """
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


# Amino acid list (just the single letter codes)
AA_LIST = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y", "*"]


def get_single_site_mutation_pattern(residue_number=None):
    """
    Generate regex pattern for matching single-site mutations.

    Args:
        residue_number: Specific residue position (e.g., 45). If None, matches any position.

    Returns:
        str: Regex pattern for single-site mutation matching.
    """
    if residue_number is not None:
        # Pattern for specific residue: A45S, A45*, etc.
        return rf"^[A-Z*]\s*{residue_number}\s*[A-Z*]$"
    else:
        # Pattern for any single-site mutation: A45S, D123F, etc.
        return r"^[A-Z*]\s*\d+\s*[A-Z*]$"


def filter_single_site_mutations(df, smiles_string=None, residue_number=None, include_parent=False):
    """
    Filter dataframe for single-site mutations with optional filters.

    Args:
        df: DataFrame containing mutation data.
        smiles_string: Optional SMILES filter.
        residue_number: Optional specific residue position filter.
        include_parent: Whether to include parent entries (default: False).

    Returns:
        pd.DataFrame: Filtered dataframe with single-site mutations.
    """
    # Filter by smiles string if provided
    if smiles_string is not None:
        filtered_df = df[df[gs.c_smiles] == smiles_string].copy()
    else:
        filtered_df = df.copy()

    # Get the appropriate mutation pattern
    mutation_pattern = get_single_site_mutation_pattern(residue_number)

    # Filter for single-site mutations
    single_site_mask = filtered_df[gs.c_substitutions].str.match(mutation_pattern, na=False)

    if include_parent:
        # Include parent entries
        parent_mask = filtered_df[gs.c_substitutions] == gs.hashtag_parent
        final_mask = single_site_mask | parent_mask
    else:
        final_mask = single_site_mask

    final = filtered_df[final_mask]
    return final


def extract_single_site_mutations(df, smiles_string=None):
    """
    Extract all single-site mutation positions from a dataframe.

    Args:
        df: DataFrame containing mutation data.
        smiles_string: Optional SMILES string filter. If None, processes all data.

    Returns:
        list: Sorted list of unique residue positions (e.g., [45, 67, 123]).
    """

    # Use shared filtering function for single-site mutations (any residue number, no parent entries)
    filtered_df = filter_single_site_mutations(df, smiles_string=smiles_string, include_parent=False)

    if filtered_df.empty:
        return []

    # Extract residue numbers from mutation strings using the shared pattern
    residue_numbers = set()
    single_mutations = filtered_df[gs.c_substitutions].dropna()

    # Use the same pattern as filtering, but add capture group for residue number
    base_pattern = get_single_site_mutation_pattern()  # Gets pattern for any residue
    residue_capture_pattern = base_pattern.replace(r"\d+", r"(\d+)")  # Capture the residue number

    for mutation in single_mutations:
        # Extract residue number using the shared pattern logic
        match = re.search(residue_capture_pattern, str(mutation))
        if match:
            residue_numbers.add(int(match.group(1)))

    # Return sorted list of unique residue positions
    return sorted(list(residue_numbers))


def create_ssm_plot(df, smiles_string, residue_number):
    """
    Create a single-site mutagenesis (SSM) plot for a specific residue.

    Generates a bar plot showing average fitness values for each amino acid mutation
    at the specified position, with individual data points overlaid.

    Args:
        df: DataFrame containing mutation data.
        smiles_string: SMILES string to filter by.
        residue_number: Residue position number (e.g., 45 for A45S).

    Returns:
        go.Figure: Plotly bar plot with scatter overlay, or None if no data.
    """

    # Use shared filtering function for single-site mutations at specific residue, including parent entries
    filtered_df = filter_single_site_mutations(
        df, smiles_string=smiles_string, residue_number=residue_number, include_parent=True
    )

    if filtered_df.empty:
        return None

    # Extract the mutated amino acid from the mutation string
    # Pattern: original_aa + number + mutated_aa
    def extract_mutated_aa(mutation_str):
        if pd.isna(mutation_str) or mutation_str == "":
            return "unknown"

        # Handle parent entries
        if mutation_str == gs.hashtag_parent:
            return "Parent"

        # Use the same mutation pattern as filtering, but add capture group for mutated amino acid
        # Pattern: original_aa + residue_number + mutated_aa (capture the mutated_aa)
        # original pattern matches A45S, D45F, L45*, etc.
        # The .replace() operation finds: [A-Z*]$ (the character class at the end of the string)
        # Replaces with: ([A-Z*])$ (adds parentheses around it)
        # Without parentheses [A-Z*]$: Matches the amino acid but doesn't capture it
        # With parentheses ([A-Z*])$: Matches AND captures the amino acid in group 1
        base_pattern = get_single_site_mutation_pattern(residue_number)
        mutation_pattern_with_capture = base_pattern.replace("[A-Z*]$", "([A-Z*])$")
        match = re.search(mutation_pattern_with_capture, str(mutation_str))
        if match:
            return match.group(1)
        else:
            # Anything else (including #N.A.#, #LOW#, -, or other formats) is unknown
            return "unknown"

    # Extract mutated amino acids
    filtered_df["mutations"] = filtered_df[gs.c_substitutions].apply(extract_mutated_aa)

    # Filter out rows with missing fitness values only
    # Note: Keeping mutations with fitness value = 0 and parent entries
    # TODO: Consider if zero fitness values should be excluded for better visualization
    # filtered_df_clean = filtered_df#.dropna(subset=[gs.c_fitness_value])

    if filtered_df.empty:
        return None

    # Define amino acid order using AA_LIST plus special cases
    aa_order = ["Parent"] + AA_LIST + ["Unknown"]
    # Create categorical column to preserve amino acid order
    # pd.Categorical function is used to convert a column into a categorical data type,
    # which is useful for ordering and grouping data.
    # ordered=True: Marks the categories as ordered

    filtered_df["mutations_cat"] = pd.Categorical(filtered_df["mutations"], categories=aa_order, ordered=True)

    # Create histogram bars for each amino acid showing average or count
    # First create a summary dataframe for the bars
    bar_data = filtered_df.groupby("mutations_cat").agg({gs.c_fitness_value: ["mean", "count"]}).reset_index()

    # Flatten column names
    bar_data.columns = ["mutations_cat", "avg_fitness", "count"]

    # Create the figure with histogram bars using RdBu_r color scale like other graphs
    fig = px.bar(
        bar_data,
        x="mutations_cat",
        y="avg_fitness",
        color="avg_fitness",  # Color bars by their fitness values
        color_continuous_scale="RdBu_r",  # Use same color scale as heatmaps
        # title=f"Single Site Mutagenesis at Position {residue_number}",
        labels={
            # 'mutations_cat': 'Mutated Amino Acid',
            "avg_fitness": "Avg. Fitness Value"
        },
    )

    # Update hover template for bars to only show avg fitness
    fig.update_traces(selector=dict(type="bar"), hovertemplate="Avg Fitness: %{y:.2f}<extra></extra>")

    # Add scatter points on top of bars to show individual data points
    fig.add_trace(
        go.Scatter(
            x=filtered_df["mutations_cat"],
            y=filtered_df[gs.c_fitness_value],
            mode="markers",
            marker=dict(
                color="rgba(128,128,128,0.8)",  # Neutral gray points
                size=6,
                opacity=0.7,
                line=dict(color="black", width=0.5),  # Thin black outline for better visibility
            ),
            name="Individual Values",
            hovertemplate="Fitness: %{y}<br><extra></extra>",
        )
    )

    # Customize the plot appearance
    fig.update_layout(
        xaxis_title="Amino Acid",
        yaxis_title="Fitness Value",
        showlegend=True,
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=50, r=50, t=50, b=50),
        title=dict(
            x=0.5,  # Center the title
            xanchor="center",
        ),
        # Improve hover label readability with white text on dark background
        hoverlabel=dict(
            bgcolor="rgba(50, 50, 50, 0.9)",  # Dark gray background
            font_color="white",  # White text for better contrast
        ),
    )

    # Fix x-axis labels orientation (horizontal instead of rotated)
    fig.update_xaxes(tickangle=-30)

    # Update bar appearance to match the heatmap theme
    fig.update_traces(
        selector=dict(type="bar"),
        marker_line_color="black",  # Black border for better definition
        marker_line_width=1,
        opacity=0.8,
    )

    # Update colorbar to match heatmap style
    fig.update_coloraxes(
        colorbar=dict(
            thickness=12,
            orientation="v",  # Vertical color bar for bar plot
            title="Avg Fitness",
        )
    )

    return fig
