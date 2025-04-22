import base64

import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app import settings, utils


def test_geometry_viewer_type(experiment_ep_pcr_with_user_cas):
    pdb = utils.get_geometry_for_viewer(experiment_ep_pcr_with_user_cas)
    assert pdb["type"] == "mol"


def test_geometry_viewer_format(experiment_ep_pcr_with_user_cas):
    pdb = utils.get_geometry_for_viewer(experiment_ep_pcr_with_user_cas)
    assert pdb["format"] == "mmcif"


def test_geometry_viewer_length(experiment_ep_pcr_with_user_cas):
    pdb = utils.get_geometry_for_viewer(experiment_ep_pcr_with_user_cas)
    assert len(pdb) == 4


# def test_gather_residue_count(selected_row_top_variant_table):
#     residues = utils.gather_residues_from_selection(selected_row_top_variant_table)
#     assert len(residues) == 2


# def test_gather_residue(selected_row_top_variant_table):
#     residues = utils.gather_residues_from_selection(selected_row_top_variant_table)
#     assert residues[0] == "99"
#     assert residues[1] == "118"


# @pytest.mark.parametrize(
#     "residue, length",
#     [
#         ("K99R R118C", 1),
#         ("K99", 0),
#         ("99R*", 0),
#     ],
# )
# def test_gather_residue_errors(residue, length):
#     """
#     assumption: residues must be in the format Letter-Number-Letter format
#     """
#     residues = utils.extract_all_indices(list(residue))
#     assert len(residues) == length


# @pytest.mark.parametrize(
#     "residue, numbers",
#     [
#         ("K99R_R118C", [99, 118]),
#         ("A59L", [59]),
#         ("C81T_T86A_A108G", [81, 86, 108]),
#     ],
# )
# def test_gather_residue_errors(residue, numbers):
#     """
#     tests the molstar selection and focus functions
#     """
#     residues = utils.gather_residues_from_selection([{gs.c_substitutions: residue}])
#     sel, foc = utils.get_selection_focus(residues)
#     assert sel["mode"] == "select"
#     assert sel["targets"][0]["residue_numbers"] == numbers
#     assert foc["analyse"]


@pytest.mark.parametrize(
    "cas, plate, mean",
    [
        ("345905-97-7", "20240422-ParLQ-ep1-300-1", 1823393.4415588235),
        ("345905-97-7", "20240422-ParLQ-ep1-300-2", 599238.9788096774),
        ("345905-97-7", "20240422-ParLQ-ep1-500-1", 737378.5054485715),
        ("345905-97-7", "20240422-ParLQ-ep1-500-2", 740058.0916967741),
        ("345905-97-7", "20240502-ParLQ-ep2-300-1", 555981.8641939394),
        ("345905-97-7", "20240502-ParLQ-ep2-300-2", 363747.4904807692),
        ("345905-97-7", "20240502-ParLQ-ep2-300-3", 472821.28098),
        ("345905-97-7", "20240502-ParLQ-ep2-500-1", 385903.38386190473),
        ("345905-97-7", "20240502-ParLQ-ep2-500-2", 273690.4014826087),
        ("345905-97-7", "20240502-ParLQ-ep2-500-3", 578947.396785),
        ("395683-37-1", "20240422-ParLQ-ep1-300-1", 1340097.0553558823),
        ("395683-37-1", "20240422-ParLQ-ep1-300-2", 574284.2879645161),
        ("395683-37-1", "20240422-ParLQ-ep1-500-1", 748629.7012771429),
        ("395683-37-1", "20240422-ParLQ-ep1-500-2", 695933.5473419355),
        ("395683-37-1", "20240502-ParLQ-ep2-300-1", 416383.57166363636),
        ("395683-37-1", "20240502-ParLQ-ep2-300-2", 330711.85486538464),
        ("395683-37-1", "20240502-ParLQ-ep2-300-3", 380189.44049999997),
        ("395683-37-1", "20240502-ParLQ-ep2-500-1", 325416.7923809524),
        ("395683-37-1", "20240502-ParLQ-ep2-500-2", 216320.55895652174),
        ("395683-37-1", "20240502-ParLQ-ep2-500-3", 530547.46612),
    ],
)
def test_calculate_group_mean(experiment_ep_pcr, cas, plate, mean):
    df = utils.calculate_group_mean_ratios_per_cas_and_plate(experiment_ep_pcr.data_df)
    # if the main core data that is kept in the user session changes column count we need to update this number
    col_count = 14

    assert df.shape[0] == 1920
    assert df.shape[1] == col_count  # added columns
    plate_per_cas_data_per = df[(df[gs.c_cas] == cas) & (df[gs.c_plate] == plate)]  # Filter the row
    assert plate_per_cas_data_per.shape[0] == 96  # plate count expectation
    assert plate_per_cas_data_per.shape[1] == col_count
    assert plate_per_cas_data_per.iloc[0]["mean"] == mean
    assert (plate_per_cas_data_per["mean"].dropna() == mean).all()

    # ratio must be increasing. this ensures the ranking was done within group
    plate_per_cas_data_per.fillna(0)
    plate_per_cas_data_per = plate_per_cas_data_per.sort_values(by="ratio", ascending=True)
    assert plate_per_cas_data_per["ratio"].dropna().is_monotonic_increasing


def test_decode_csv_file_base64_string_to_dataframe():
    # make a csv content
    csv_content = "col_A,col_B\nLevseq,2024\nProject,2025"
    csv_bytes = csv_content.encode("utf-8")  # Convert string to bytes
    csv_base64 = base64.b64encode(csv_bytes).decode("utf-8")  # Encode to Base64 string

    df = utils.decode_csv_file_base64_string_to_dataframe(csv_base64)

    assert isinstance(df, pd.DataFrame)  # Ensure result is a DataFrame
    assert df.shape == (2, 2)  # 2 rows, 2 columns
    assert list(df.columns) == ["col_A", "col_B"]  # Correct columns
    assert df.iloc[0]["col_A"] == "Levseq"  # Correct data
    assert df.iloc[1]["col_B"] == 2025  # Correct data


def test_decode_csv_file_base64_string_to_dataframe_empty():
    # empty csv -> empty bytes
    empty_base64 = base64.b64encode(b"").decode("utf-8")

    df = utils.decode_csv_file_base64_string_to_dataframe(empty_base64)

    assert isinstance(df, pd.DataFrame)
    assert df.empty  # Ensure the DataFrame is empty


def test_decode_csv_file_base64_string_to_dataframe_invalid():
    # invalid input
    # https://docs.python.org/3/library/base64.html#base64.b64decode
    with pytest.raises(base64.binascii.Error):  # Expecting binascii.Error
        utils.decode_csv_file_base64_string_to_dataframe("SomeInvalidString")


def test_decode_csv_file_base64_string_to_dataframe_non_utf8():
    """Test decoding non-UTF-8 Base64 string (should raise an error)."""
    non_utf8_bytes = b"\x80\x81\x82"  # Invalid UTF-8 bytes
    non_utf8_base64 = base64.b64encode(non_utf8_bytes).decode("utf-8")

    with pytest.raises(Exception, match="The content is not a valid UTF-8 string."):
        utils.decode_csv_file_base64_string_to_dataframe(non_utf8_base64)


def test_load_config():
    c = settings.load_config()
    # TODO this must be switched on deployment
    assert not c["debug"]["use_db_web_service"]
    assert c["debug"]["load_all_experiments_from_disk"]
