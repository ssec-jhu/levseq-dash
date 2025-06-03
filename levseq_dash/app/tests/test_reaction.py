import base64

import pytest
from rdkit import Chem

from levseq_dash.app.utils import u_reaction

expected_svg_prefix = "data:image/svg+xml;base64,"


@pytest.mark.parametrize(
    "valid_smiles",
    [
        # three different reps of ethanol
        "CCO",  # ethanol
        "OCC",  # ethanol
        "C(O)C",  # ethanol
        "O=C=O",  # carbon dioxide
        "C1=CC=CC=C1",  # benzene
        "C(C(=O)O)N",  # glycine
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # aspirin,
    ],
)
def test_valid_smiles(valid_smiles):
    assert u_reaction.is_valid_smiles(valid_smiles) is not None


@pytest.mark.parametrize(
    "invalid_smiles",
    [
        "C1CC1C1",  # invalid ring closure
        "N[N@@",  # malformed chiral center
        "C(C(C",  # incomplete branches
        "*&^%$#",  # nonsense
        "12345",  # numeric string
        "random",  # empty string
        " ",  # empty spaces
        "   ",
        "\t",
        "abc",
        "(",
    ],
)
def test_invalid_smiles(invalid_smiles):
    assert u_reaction.is_valid_smiles(invalid_smiles) is None


def test_none_input():
    with pytest.raises(Exception):
        u_reaction.is_valid_smiles(None)


@pytest.mark.parametrize(
    "valid_smiles",
    [
        # three different reps of ethanol
        "CCO",  # ethanol
        "OCC",  # ethanol
        "C(O)C",  # ethanol
        "C-C-O",  # ethanol
        "CC-O",  # ethanol
        "C-CO",
    ],
)
def test_canonical_smiles_1(valid_smiles):
    """
    Chem.MolToSmiles sanitizes and converts the string into a standard canonical form
    This test is checking different forms of one molecule.
    """
    sm = Chem.MolToSmiles(Chem.MolFromSmiles(valid_smiles))
    assert sm == "CCO"


@pytest.mark.parametrize(
    "smiles",
    [
        "C1CCCCC1C2CCCCC2"  # bicyclohexyl ,
        "C0CCCCC0C0CCCCC0"
    ],
)
def test_canonical_smiles_2(smiles):
    """
    Chem.MolToSmiles sanitizes and converts the string into a standard canonical form
    This test is checking different forms of one molecule.
    """
    sm = Chem.MolToSmiles(Chem.MolFromSmiles(smiles))
    assert sm == "C1CCC(C2CCCCC2C2CCCCC2C2CCCCC2)CC1"


def test_basic_svg_encoding():
    svg_input = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="5"/></svg>'

    result = u_reaction.convert_svg_img_to_src(svg_input)

    assert result.startswith(expected_svg_prefix)

    # get the base part
    base64_part = result.split(",")[1]
    # decode it back
    decoded_svg = base64.b64decode(base64_part).decode("utf-8")
    assert decoded_svg == svg_input


def test_empty_svg_string():
    result = u_reaction.convert_svg_img_to_src("")
    assert result.startswith(expected_svg_prefix)
    assert result == "data:image/svg+xml;base64,"


def test_none_svg_string():
    with pytest.raises(Exception):
        u_reaction.convert_svg_img_to_src(None)


def test_unicode_characters_in_svg():
    svg_input = "<svg><text>Δδλπ</text></svg>"  # Greek characters
    result = u_reaction.convert_svg_img_to_src(svg_input)
    base64_part = result.split(",")[1]
    decoded = base64.b64decode(base64_part).decode("utf-8")
    assert decoded == svg_input


def test_invalid_input_type():
    with pytest.raises(Exception):
        # a non string input
        u_reaction.convert_svg_img_to_src(123)


def test_valid_reaction_smiles():
    substrate = "CCO"  # ethanol
    product = "CC=O"  # acetaldehyde

    svg = u_reaction.create_reaction_image(substrate, product)

    assert svg.startswith(expected_svg_prefix)


@pytest.mark.parametrize(
    "invalid_substrate, invalid_product",
    [
        ("", "CCO"),  # Empty substrate
        ("CCO", ""),  # Empty product
        ("   ", "CCO"),  # Space-only substrate
        ("CCO", "   "),  # Space-only product
        ("random", "CCO"),  # this will give an internal warning from rdkit but test passes as expected
        ("CCO", "anything"),  # this will give an internal warning from rdkit but test passes as expected
        ("C1CC1C1", "CCO"),  # invalid ring closure on substrate
        (None, "CCO"),
        ("CCO", None),
        (None, None),
    ],
)
def test_invalid_smiles_raises_exception(invalid_substrate, invalid_product):
    with pytest.raises(Exception):
        u_reaction.create_reaction_image(invalid_substrate, invalid_product)


@pytest.mark.parametrize(
    "smiles",
    [
        "CCO;C1=CC=CC=C1;CC(=O)O",
        "CCO;    C1=CC=CC=C1;    CC(=O)O",  # added spaces
        "CCO;notasmiles;C1=CC=CC=C1;123bad",  # this should skip over the invalid ones, but still have an image
    ],
)
def test_valid_smiles_grid(smiles):
    svg = u_reaction.create_mols_grid(smiles)

    assert svg is not None
    assert svg.startswith(expected_svg_prefix)


def test_valid_smiles_grid_long():
    smiles = ";".join(["CCO"] * 100)
    svg = u_reaction.create_mols_grid(smiles)

    assert svg is not None
    assert svg.startswith(expected_svg_prefix)


@pytest.mark.parametrize(
    "smiles",
    [
        None,
        "",
        ";  ;",
        ";notasmiles;invalid;bad",  # this should skip over the invalid ones, but still have an image
    ],
)
def test_invalid_smiles_grid(smiles):
    svg = u_reaction.create_mols_grid(smiles)

    assert svg is None
