import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import graphs


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("N56T_T45R_D32R", "N56T<br>T45R<br>D32R"),
        ("F67R_A5N", "F67R<br>A5N"),
        ("N56T_T45R_D32R_Y78T", "4Mut*"),  # More than 3 mutations
        ("X_Y_Z_W_V", "5Mut*"),  # More than 3 mutations
        ("single", "single"),  # Only one mutation
        (3, ""),
        (float("nan"), ""),  # dataframe procedures may result in a nan column
    ],
)
def test_format_mutation_annotation(input_text, expected_output):
    assert graphs.format_mutation_annotation(input_text) == expected_output


@pytest.mark.parametrize(
    "smiles, plate, property",
    [
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", gs.c_fitness_value),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", gs.c_fitness_value),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_probability),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_probability),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_count),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", gs.c_alignment_count),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", gs.c_alignment_count),
    ],
)
def test_creat_heatmap_figure_general(experiment_ep_pcr, smiles, plate, property):
    df = experiment_ep_pcr.data_df
    fig = graphs.creat_heatmap(df, plate_number=plate, property=property, smiles=smiles)

    # must have annotations
    annotations = fig["data"][0]["text"]
    assert annotations.shape == (8, 12)
    # check hover date
    hover = fig["data"][0]["hovertemplate"]
    assert "Mut:" in hover
    assert "Well:" in hover

    custom_data = fig["data"][0]["customdata"]
    assert custom_data.shape == (8, 12)

    # Check if the colorbar is placed at the top
    assert fig.layout.coloraxis.colorbar.orientation == "h"  # Horizontal colorbar

    # Check margin removal
    assert fig.layout.margin.l == 0
    assert fig.layout.margin.r == 0
    assert fig.layout.margin.b == 0


@pytest.mark.parametrize(
    "smiles, plate, mutation,i,j",
    [
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", "A14G", 4, 3),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", "Y185N", 2, 5),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", "L59Q", 4, 10),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", "K87E", 2, 0),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", "G189S", 0, 4),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", "K39E", 1, 4),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", "L173S", -1, -1),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", "V127A", 3, 3),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", "K120R", 4, 5),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", "F89L", 3, 5),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", "V28E", 4, 3),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", "F70L", 2, 5),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", "I67N", 4, 0),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", "K155E", 2, 0),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", "L97S", 0, 4),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", "E164D", 2, 7),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", "D128N", -1, -1),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", "L82P", 3, 3),
        # ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", "L59P", 3, 1),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", "L82Q", 3, 5),
    ],
)
def test_creat_heatmap_figure_data(experiment_ep_pcr, smiles, plate, mutation, i, j):
    df = experiment_ep_pcr.data_df
    fig = graphs.creat_heatmap(df, plate_number=plate, property=gs.c_fitness_value, smiles=smiles)

    # mutations should appear in custom data
    assert mutation in fig["data"][0]["customdata"]

    # must have annotations
    annotations = fig["data"][0]["text"]
    assert any(mutation in text for text in annotations)

    # Ensure 4Mut* appears where necessary
    if i == -1 and j == -1:
        assert not any("4Mut*" in text for text in annotations)
    else:
        assert annotations[i][j] == "4Mut*"


@pytest.mark.parametrize(
    "smiles, plate",
    [
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2"),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1"),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1"),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3"),
    ],
)
def test_create_rank_plot_figure_data(experiment_ep_pcr, smiles, plate):
    fig = graphs.creat_rank_plot(df=experiment_ep_pcr.data_df, plate_number=plate, smiles=smiles)
    count = 0
    for index in range(0, len(fig["data"])):
        count += len(fig["data"][index]["customdata"])
    assert count == 96


@pytest.mark.parametrize(
    "smiles, residue_number",
    [
        ("C1=CC=C(C=C1)C=O", 120),
        ("C1=CC=C(C=C1)C=O", 93),
        ("C1=CC=C(C=C1)C=O", 149),
        ("C1=CC=C(C=C1)C=O", 89),
        ("C1=CC=C(C=C1)C=O", 59),  # Most common residue in test data
    ],
)
def test_create_ssm_plot_basic(experiment_ssm, smiles, residue_number):
    """Test basic structure and layout of SSM plots"""
    fig = graphs.create_ssm_plot(experiment_ssm.data_df, smiles, residue_number)

    # Basic structure tests
    assert fig is not None, "Figure should not be None"
    assert len(fig["data"]) == 2, "Should have 2 traces: bars and scatter points"


@pytest.mark.parametrize(
    "smiles, residue_number, expected_mutations",
    [
        ("C1=CC=C(C=C1)C=O", 59, ["Parent", "V", "S", "N", "G", "L", "M"]),  # A59 mutations
        ("C1=CC=C(C=C1)C=O", 89, ["Parent"]),  # Should have at least Parent
        ("C1=CC=C(C=C1)C=O", 93, ["Parent"]),  # Should have at least Parent
        ("C1=CC=C(C=C1)C=O", 120, ["Parent"]),  # Should have at least Parent
        ("C1=CC=C(C=C1)C=O", 149, ["Parent"]),  # Should have at least Parent
    ],
)
def test_create_ssm_plot_mutations(experiment_ssm, smiles, residue_number, expected_mutations):
    """Test that expected mutations appear in the plot"""
    fig = graphs.create_ssm_plot(experiment_ssm.data_df, smiles, residue_number)

    # Check bar data (averaged mutations)
    bar_x_values = fig["data"][0]["x"]
    assert "Parent" in bar_x_values, "Should always include Parent category"

    # Check that expected mutations are present in the data
    for mutation in expected_mutations:
        assert mutation in bar_x_values, f"Expected mutation '{mutation}' should be in bar chart"

    # Check scatter data (individual points)
    scatter_x_values = fig["data"][1]["x"]
    scatter_y_values = fig["data"][1]["y"]

    # Should have same number of x and y values for scatter plot
    assert len(scatter_x_values) == len(scatter_y_values), "Scatter plot should have matching x and y data"

    # All fitness values should be numeric
    for fitness_val in scatter_y_values:
        assert isinstance(fitness_val, (int, float)), f"Fitness value {fitness_val} should be numeric"


def test_create_ssm_plot_amino_acid_ordering(experiment_ssm):
    """Test that amino acids are properly ordered using AA_LIST"""
    smiles = "C1=CC=C(C=C1)C=O"
    residue_number = 59  # Residue with multiple mutations

    fig = graphs.create_ssm_plot(experiment_ssm.data_df, smiles, residue_number)

    # Get the amino acid categories from the bar chart
    bar_x_values = list(fig["data"][0]["x"])

    # Parent should always come first
    if "Parent" in bar_x_values:
        assert bar_x_values[0] == "Parent"

    # Remove Parent to check amino acid ordering
    aa_values = [x for x in bar_x_values if x != "Parent"]

    # Check that amino acids follow the expected order from AA_LIST
    from levseq_dash.app.components.graphs import AA_LIST

    # The amino acids that appear should be in the correct order
    aa_indices = [AA_LIST.index(aa) if aa in AA_LIST else float("inf") for aa in aa_values]
    assert aa_indices == sorted(aa_indices), f"Amino acids should be ordered according to AA_LIST: {aa_values}"
