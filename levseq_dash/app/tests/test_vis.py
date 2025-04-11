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
