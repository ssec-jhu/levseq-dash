import ast
import re

from dash_molstar.utils import molstar_helper
from dash_molstar.utils.representations import Representation

from levseq_dash.app import global_strings as gs

substitution_indices_pattern = r"(\d+)"


def get_geometry_for_viewer(exp):
    if exp.geometry_file_path:
        pdb_cif = molstar_helper.parse_molecule(exp.geometry_file_path, fmt="cif")
    else:
        pdb_cif = molstar_helper.parse_molecule(exp.geometry_base64_bytes, fmt="cif")
    return pdb_cif


def get_selection_focus(residues, analyse=True):
    """ "
    https://dash-molstar.readthedocs.io/en/latest/
    """
    target = molstar_helper.get_targets(
        chain="A",
        residue=residues,
        auth=True,
        # if it's a CIF file to select the authentic chain names and residue
        # numbers
    )
    sel = molstar_helper.get_selection(
        target,
        # select by default, it will put a green highlight on the atoms
        # default select mode (true) or hover mode (false)
        # select=False,
        add=False,
    )  # TODO: do we want to add to the list?

    # Focus the camera on the specified targets.
    # If analyse is set to True, non-covalent interactions within 5 angstroms will be analysed.
    # https://dash-molstar.readthedocs.io/en/latest/callbacks.html#parameter-focus
    foc = molstar_helper.get_focus(target, analyse=analyse)

    return sel, foc


def reset_selection():
    target = {"chain_name": None, "auth": False, "residue_numbers": []}
    sel = molstar_helper.get_selection(
        target,
        # select by default, it will put a green highlight on the atoms
        # default select mode (true) or hover mode (false)
        select=True,
        add=False,
    )
    return sel


def get_molstar_rendered_components_seq_alignment(
    hot_residue_indices_list, cold_residue_indices_list, substitution_residue_list
):
    """
    Generate Dash Molstar components for each of the  list of indices
    """

    mismatch_residues = list(map(int, ast.literal_eval(substitution_residue_list)))
    hot_residues = list(map(int, ast.literal_eval(hot_residue_indices_list)))
    cold_residues = list(map(int, ast.literal_eval(cold_residue_indices_list)))

    # extract the residues that are both in hot and cold groups and isolate the others out
    both_hs_and_cs = list(set(hot_residues).intersection(set(cold_residues)))
    hs_only = [item for item in hot_residues if item not in both_hs_and_cs]
    cs_only = [item for item in cold_residues if item not in both_hs_and_cs]

    # make the representations
    # main chain
    rep_cartoon_gray = Representation(type="cartoon", color="uniform")
    rep_cartoon_gray.set_type_params({"alpha": 0.5})

    # hot spots
    rep_hot = Representation(type="cartoon", color="uniform", size="uniform")
    rep_hot.set_color_params({"value": 0xC41E3A})
    rep_hot.set_size_params({"value": 1.15})

    # cold spots
    rep_cold = Representation(type="cartoon", color="uniform", size="uniform")
    rep_cold.set_color_params({"value": 0x0047AB})
    rep_cold.set_size_params({"value": 1.5})

    # both hot and cold
    rep_hot_cold = Representation(type="cartoon", color="uniform", size="uniform")
    rep_hot_cold.set_color_params({"value": 0xB57EDC})
    rep_hot_cold.set_size_params({"value": 1.5})

    # mismatches
    rep_mismatches = Representation(type="ball-and-stick")

    main_chain = molstar_helper.get_targets(chain="A")
    hot_residue = molstar_helper.get_targets(chain="A", residue=hs_only)
    # analyse = molstar_helper.get_focus(hot_residue, analyse=True)
    analyse = molstar_helper.get_focus(main_chain, analyse=False)
    cold_residue = molstar_helper.get_targets(chain="A", residue=cs_only)
    both_hot_and_cold_residue = molstar_helper.get_targets(chain="A", residue=both_hs_and_cs)
    mismatch_residue = molstar_helper.get_targets(chain="A", residue=mismatch_residues)

    component_main_chain = molstar_helper.create_component(
        label="main", targets=main_chain, representation=rep_cartoon_gray
    )
    component_hot_residue = molstar_helper.create_component(
        label=gs.cc_hot_indices_per_smiles, targets=hot_residue, representation=rep_hot
    )
    component_cold_residue = molstar_helper.create_component(
        label=gs.cc_cold_indices_per_smiles, targets=cold_residue, representation=rep_cold
    )
    component_both_residue = molstar_helper.create_component(
        label=gs.cc_hot_and_cold_indices_per_smiles, targets=both_hot_and_cold_residue, representation=rep_hot_cold
    )
    component_mismatch_residue = molstar_helper.create_component(
        label=gs.c_substitutions, targets=mismatch_residue, representation=rep_mismatches
    )
    return [
        component_main_chain,
        component_hot_residue,
        component_cold_residue,
        component_both_residue,
        component_mismatch_residue,
    ]


def get_molstar_rendered_components_related_variants(substitution_residue_list):
    """ """

    sub_residues_list = list(map(int, substitution_residue_list))

    # make the representations
    # main chain
    rep_by_seq_id = Representation(type="cartoon", color="sequence-id")
    rep_by_seq_id.set_type_params({"alpha": 0.3})

    rep_uniform_red = Representation(type="cartoon", color="uniform", size="uniform")
    rep_uniform_red.set_color_params({"value": 0xC41E3A})
    rep_uniform_red.set_size_params({"value": 1.15})

    rep_ball_stick = Representation(type="ball-and-stick")

    main_chain = molstar_helper.get_targets(chain="A")
    analyse = molstar_helper.get_focus(main_chain, analyse=False)
    sub_residue = molstar_helper.get_targets(chain="A", residue=sub_residues_list)

    component_main_chain = molstar_helper.create_component(
        label="main", targets=main_chain, representation=rep_by_seq_id
    )

    component_sub_residue = molstar_helper.create_component(
        label=gs.c_substitutions, targets=sub_residue, representation=rep_uniform_red
    )
    component_sub_residue_2 = molstar_helper.create_component(
        label=f"{gs.c_substitutions}_2", targets=sub_residue, representation=rep_ball_stick
    )
    return [component_main_chain, component_sub_residue, component_sub_residue_2]
