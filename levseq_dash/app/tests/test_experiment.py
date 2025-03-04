from pathlib import Path

import pandas as pd
import pytest


def test_experiment_empty_upload_timestamp(experiment_empty):
    assert experiment_empty.upload_time_stamp != ""


def test_experiment_empty_substrate_cas(experiment_empty):
    assert len(experiment_empty.substrate_cas_number) == 0


def test_experiment_empty_product_cas(experiment_empty):
    assert len(experiment_empty.product_cas_number) == 0


def test_experiment_empty_mutagenesis_method(experiment_empty):
    assert experiment_empty.mutagenesis_method == ""


def test_experiment_empty_plates(experiment_empty):
    assert len(experiment_empty.plates) == 0


def test_experiment_empty_plates_count(experiment_empty):
    assert experiment_empty.plates_count == 0


def test_experiment_empty_parent_sequence(experiment_empty):
    assert experiment_empty.parent_sequence == ""


def test_experiment_empty_geometry_file_path(experiment_empty):
    assert experiment_empty.geometry_file_path is None


def test_experiment_empty_geometry_base64_bytes(experiment_empty):
    assert experiment_empty.geometry_base64_bytes == bytes()


def test_experiment_empty_geometry_base64_string(experiment_empty):
    assert experiment_empty.geometry_base64_string == ""


@pytest.mark.parametrize(
    "index, cas_number",
    [(0, "345905-97-7"), (1, "395683-37-1")],
)
def test_experiment_ep_pcr_cas(experiment_ep_pcr, index, cas_number):
    assert experiment_ep_pcr.unique_cas_in_data[index] == cas_number


@pytest.mark.parametrize(
    "index, plate",
    [
        (0, "20240422-ParLQ-ep1-300-1"),
        (2, "20240422-ParLQ-ep1-500-1"),
        (4, "20240502-ParLQ-ep2-300-1"),
        (6, "20240502-ParLQ-ep2-300-3"),
        (8, "20240502-ParLQ-ep2-500-2"),
    ],
)
def test_experiment_ep_pcr_plated(experiment_ep_pcr, index, plate):
    assert experiment_ep_pcr.plates[index] == plate


def test_experiment_ep_pcr_data_shape(experiment_ep_pcr):
    assert experiment_ep_pcr.data_df.shape[0] == 1920
    assert experiment_ep_pcr.data_df.shape[1] == 8


def test_experiment_ep_pcr_assay(experiment_ep_pcr, assay_list):
    assert experiment_ep_pcr.assay == assay_list[2]


def test_experiment_ep_pcr_unique_cas(experiment_ep_pcr):
    assert len(experiment_ep_pcr.unique_cas_in_data) == 2


def test_experiment_ep_pcr_name(experiment_ep_pcr):
    assert experiment_ep_pcr.experiment_name == "ep_file"


def test_experiment_ep_pcr_date(experiment_ep_pcr):
    assert experiment_ep_pcr.experiment_date == "TBD"


def test_experiment_ep_pcr_upload_timestamp(experiment_ep_pcr):
    assert experiment_ep_pcr.upload_time_stamp != ""


def test_experiment_ep_pcr_substrate_cas(experiment_ep_pcr):
    assert len(experiment_ep_pcr.substrate_cas_number) == 0


def test_experiment_ep_pcr_product_cas(experiment_ep_pcr):
    assert len(experiment_ep_pcr.product_cas_number) == 0


def test_experiment_ep_pcr_mutagenesis_method(experiment_ep_pcr):
    from levseq_dash.app import global_strings as gs

    assert experiment_ep_pcr.mutagenesis_method == gs.eppcr


def test_experiment_ep_pcr_plates(experiment_ep_pcr):
    assert len(experiment_ep_pcr.plates) == 10


def test_experiment_ep_pcr_plates_count(experiment_ep_pcr):
    assert experiment_ep_pcr.plates_count == 10


def test_experiment_ep_pcr_parent_sequence(experiment_ep_pcr):
    assert experiment_ep_pcr.parent_sequence == (
        "MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVE"
        "DILDLWYGLQGSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTLCKPL"
        "DRQWLNYMYEIGLRHHRTKKGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPI"
        "LEKSGHPPEAVERMWAAWVKLVVLQVAIWSYPYAKTGEWLE"
    )


def test_experiment_ep_pcr_geometry_base64_bytes(experiment_ep_pcr):
    assert experiment_ep_pcr.geometry_base64_bytes == bytes()


def test_experiment_ep_pcr_geometry_base64_string(experiment_ep_pcr):
    assert experiment_ep_pcr.geometry_base64_string == ""


def test_experiment_ep_pcr_substrate(experiment_ep_pcr_with_user_cas):
    assert experiment_ep_pcr_with_user_cas.substrate_cas_number == "918704-25-2, 98053-92-1"


def test_experiment_ep_pcr_product(experiment_ep_pcr_with_user_cas):
    assert experiment_ep_pcr_with_user_cas.product_cas_number == "597635-11-3, 605026-90-8, 650843-51-7"


def test_exp_to_dict_data_shape(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_to_dict()
    df = pd.DataFrame(d["data_df"])
    assert df.shape[0] == 1920
    assert df.shape[1] == 8


def test_exp_to_dict_plates_count(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_to_dict()
    assert d["plates_count"] == 10


def test_exp_to_dict_substrate_cas(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_to_dict()
    assert d["substrate_cas_number"] == "918704-25-2, 98053-92-1"


def test_exp_to_dict_assay(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_to_dict()
    assert d["assay"] == "UV-Vis Spectroscopy"


def test_exp_meta_data_plates_count(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_meta_data_to_dict()
    assert d["plates_count"] == 10


def test_exp_meta_data_substrate_cas(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_meta_data_to_dict()
    assert d["substrate_cas_number"] == "918704-25-2, 98053-92-1"


def test_exp_meta_data_assay(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_meta_data_to_dict()
    assert d["assay"] == "UV-Vis Spectroscopy"


def test_exp_meta_data_length(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_meta_data_to_dict()
    assert len(d) == 12


def test_exp_core_data_to_dict(experiment_ep_pcr_with_user_cas):
    d = experiment_ep_pcr_with_user_cas.exp_core_data_to_dict()
    df = pd.DataFrame.from_dict(d)
    assert df.shape[0] == 1920
    assert df.shape[1] == 8


@pytest.mark.parametrize(
    "index, key, value",
    [
        (0, "aa_sequence", "#N.A.#"),
        (0, "alignment_count", 0),
        (0, "alignment_probability", 0.0),
        (0, "amino_acid_substitutions", "#N.A.#"),
        (0, "cas_number", "345905-97-7"),
        (94, "fitness_value", 1917633.707),
        (0, "plate", "20240422-ParLQ-ep1-300-1"),
        (0, "well", "A1"),
        (
            36,
            "aa_sequence",
            "MAVPGYDFGKVPDAPISDADFESLKKTVMWGEEDEKYRKMACEALKGQVEDILDLWYGLQGSNQHLIYYFGDKSGRPIPQYLEAVRKRFGLWIIDTLCKPLDRQWL"
            "NYMYEIGLRHHRTKKGKTDGVDTVEHIPLRYMIAFIAPIGLTIKPILEKSGHPPEAVERMWAAWVKLVVLQVAIWSYPYAKTGEWLE",
        ),
        (51, "alignment_count", 29),
        (61, "alignment_probability", 0.0),
        (69, "amino_acid_substitutions", "#PARENT#"),
        (99, "cas_number", "395683-37-1"),
        (99, "fitness_value", 1244116.159),
        (42, "plate", "20240422-ParLQ-ep1-300-1"),
        (0, "well", "A1"),
    ],
)
def test_exp_core_data_to_dict_2(experiment_ep_pcr_with_user_cas, index, key, value):
    d = experiment_ep_pcr_with_user_cas.exp_core_data_to_dict()
    assert d[index][key] == value
