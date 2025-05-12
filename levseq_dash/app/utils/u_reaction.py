import base64

from rdkit import Chem
from rdkit.Chem import Draw, rdChemReactions


def is_valid_smiles(smiles):
    """
    Args:
        smiles: the smiles string we would like to validate

    Returns:
        MolFromSmiles will sanitize and validat the string. It will return None upon failure

    """
    mol = Chem.MolFromSmiles(smiles)
    return mol is not None


def convert_svg_img_to_src(svg_img):
    svg_base64 = base64.b64encode(svg_img.encode("utf-8")).decode("utf-8")
    svg_src = f"data:image/svg+xml;base64,{svg_base64}"
    return svg_src


def create_reaction_image(substrate_smiles: str, product_smiles: str):
    """
    Args:
        substrate_smiles: reaction substrate in smiles strings
        product_smiles: reaction product in smiles strings

    Returns:
        image

    """
    # verify the smiles string
    if not is_valid_smiles(substrate_smiles) or not is_valid_smiles(product_smiles):
        raise Exception("Smiles String is not valid for creating an image.")

    rxn_smarts = f"{substrate_smiles}>>{product_smiles}"
    rxn = rdChemReactions.ReactionFromSmarts(rxn_smarts, useSmiles=True)

    # this function will return a raster image, and you can use
    # this in dash with an html.Img(src=img)
    # img = Draw.ReactionToImage(rxn)
    # return img

    # this option produces a svg image
    svg_img = Draw.ReactionToImage(rxn, subImgSize=(150, 150), useSVG=True)
    svg_src = convert_svg_img_to_src(svg_img)

    return svg_src


def create_mols_grid(all_smiles_strings: str):
    # Clean and split SMILES
    smiles_list = [s.strip() for s in all_smiles_strings.split(";") if s.strip()]
    mols = []
    captions = []

    for smi in smiles_list:
        try:
            mol = Chem.MolFromSmiles(smi)
            if mol:
                mols.append(mol)
                captions.append(smi)
        except Exception as e:
            print(f"Error parsing {smi}: {e}")

    if not mols:
        return None, None

    # make an svg image for better resolution
    # MolsToGridImage is a bit more limited in terms of the layout and the padding that it has
    # but it is better than loads of code trying to draw on the draw pad
    svg_img = Draw.MolsToGridImage(mols, molsPerRow=8, subImgSize=(200, 200), legends=captions, useSVG=True)
    svg_src = convert_svg_img_to_src(svg_img)

    return svg_src
