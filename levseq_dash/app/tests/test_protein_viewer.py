import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.utils import u_protein_viewer, utils


def test_get_molstar_rendered_components(list_of_residues):
    result = u_protein_viewer.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )

    # Validate structure
    assert isinstance(result, list)
    assert len(result) == 5


def test_get_molstar_rendered_components_hot(list_of_residues):
    result = u_protein_viewer.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )
    targets = [comp["targets"] for comp in result]
    assert targets[1][0]["residue_numbers"] == [10, 20]


def test_get_molstar_rendered_components_cold(list_of_residues):
    result = u_protein_viewer.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )
    targets = [comp["targets"] for comp in result]
    assert targets[2][0]["residue_numbers"] == [40, 50]


def test_get_molstar_rendered_components_both(list_of_residues):
    result = u_protein_viewer.get_molstar_rendered_components_seq_alignment(
        list_of_residues[0], list_of_residues[1], list_of_residues[2]
    )
    targets = [comp["targets"] for comp in result]
    assert targets[3][0]["residue_numbers"] == [30]


def test_get_molstar_rendered_components_mismatches(list_of_residues):
    result = u_protein_viewer.get_molstar_rendered_components_seq_alignment(
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
    assert len(u_protein_viewer.get_molstar_rendered_components_related_variants(substitution_residue_list)) == 3


@pytest.mark.parametrize(
    "index, label,rep,color",
    [
        (0, "main", "cartoon", "sequence-id"),
        (1, "amino_acid_substitutions", "cartoon", "uniform"),
        (2, "amino_acid_substitutions_2", "ball-and-stick", None),
    ],
)
def test_get_molstar_rendered_components_related_variants(index, label, rep, color):
    output = u_protein_viewer.get_molstar_rendered_components_related_variants(["106", "118", "203", "322", "552"])
    assert output[index]["label"] == label
    assert output[index]["representation"][0]["type"] == rep
    if color:
        assert output[index]["representation"][0]["color"] == color

    # assert output[0]["representation"][0]["typeParams"] == {'alpha': 0.5}


def test_geometry_viewer_type(experiment_ep_pcr_with_user_smiles):
    pdb = u_protein_viewer.get_geometry_for_viewer(experiment_ep_pcr_with_user_smiles)
    assert pdb["type"] == "mol"


def test_geometry_viewer_format(experiment_ep_pcr_with_user_smiles):
    pdb = u_protein_viewer.get_geometry_for_viewer(experiment_ep_pcr_with_user_smiles)
    assert pdb["format"] == "mmcif"


def test_geometry_viewer_length(experiment_ep_pcr_with_user_smiles):
    pdb = u_protein_viewer.get_geometry_for_viewer(experiment_ep_pcr_with_user_smiles)
    assert len(pdb) == 4


def test_extract_all_indices(selected_row_top_variant_table):
    residues = utils.extract_all_indices(selected_row_top_variant_table[0][gs.c_substitutions])
    assert len(residues) == 2


@pytest.mark.parametrize(
    "residue, extracted_list, length",
    [
        ("A53K_T34R", ["53", "34"], 2),
        ("K43*_A59R", ["43", "59"], 2),
        ("T106C_G118T_T203C_C322T_T552G", ["106", "118", "203", "322", "552"], 5),
        ("#PARENT#", [], 0),
        ("#anything#", [], 0),
        ("N.A", [], 0),
        ("K99R_R118C", ["99", "118"], 2),
        ("K99", ["99"], 1),
        ("99R*", ["99"], 1),
    ],
)
def test_test_extract_all_indices_2(residue, extracted_list, length):
    indices = utils.extract_all_indices(residue)
    assert len(indices) == length
    assert indices == extracted_list


@pytest.mark.parametrize(
    "residue, numbers",
    [
        ("K99R_R118C", [99, 118]),
        ("A59L", [59]),
        ("C81T_T86A_A108G", [81, 86, 108]),
    ],
)
def test_gather_residue_errors(residue, numbers):
    """
    tests the molstar selection and focus functions
    """
    residues = utils.extract_all_indices(residue)
    sel, foc = u_protein_viewer.get_selection_focus(residues)
    assert sel["mode"] == "select"
    assert sel["targets"][0]["residue_numbers"] == numbers
    assert foc["analyse"]


@pytest.mark.parametrize(
    "residue_list, target",
    [
        (["53", "34"], [53, 34]),
        (["43", "59"], [43, 59]),
        (["106", "118", "203", "322", "552"], [106, 118, 203, 322, 552]),
        ([], []),
    ],
)
def test_get_selection_focus(residue_list, target):
    sel, foc = u_protein_viewer.get_selection_focus(residue_list, analyse=False)
    assert sel["targets"][0]["residue_numbers"] == target
    assert foc["targets"][0]["residue_numbers"] == target


def test_reset_selection():
    sel = u_protein_viewer.reset_selection()
    assert sel["targets"][0]["residue_numbers"] == []
