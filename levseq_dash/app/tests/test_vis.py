import pytest

from levseq_dash.app import vis


def test_get_molstar_rendered_components(list_of_residues):
    result = vis.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )

    # Validate structure
    assert isinstance(result, list)
    assert len(result) == 5


def test_get_molstar_rendered_components_hot(list_of_residues):
    result = vis.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )
    targets = [comp["targets"] for comp in result]
    assert targets[1][0]["residue_numbers"] == [10, 20]


def test_get_molstar_rendered_components_cold(list_of_residues):
    result = vis.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )
    targets = [comp["targets"] for comp in result]
    assert targets[2][0]["residue_numbers"] == [40, 50]


def test_get_molstar_rendered_components_both(list_of_residues):
    result = vis.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )
    targets = [comp["targets"] for comp in result]
    assert targets[3][0]["residue_numbers"] == [30]


def test_get_molstar_rendered_components_mismatches(list_of_residues):
    result = vis.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )
    targets = [comp["targets"] for comp in result]
    assert targets[4][0]["residue_numbers"] == [25, 60]


@pytest.mark.parametrize(
    "substitution_residue_list",
    [
        (["53", "34"]),
        (["43", "59"]),
        (["106", "118", "203", "322", "552"]),
        # ([], 0), #TODO: need to fix the function
    ],
)
def test_get_molstar_rendered_components_related_variants_number_of_comp(substitution_residue_list):
    assert len(vis.get_molstar_rendered_components_related_variants(substitution_residue_list)) == 3


@pytest.mark.parametrize(
    "index, label,rep,color",
    [
        (0, "main", "cartoon", "sequence-id"),
        (1, "amino_acid_substitutions", "cartoon", "uniform"),
        (2, "amino_acid_substitutions_2", "ball-and-stick", None),
    ],
)
def test_get_molstar_rendered_components_related_variants(index, label, rep, color):
    output = vis.get_molstar_rendered_components_related_variants(["106", "118", "203", "322", "552"])
    assert output[index]["label"] == label
    assert output[index]["representation"][0]["type"] == rep
    if color:
        assert output[index]["representation"][0]["color"] == color

    # assert output[0]["representation"][0]["typeParams"] == {'alpha': 0.5}
