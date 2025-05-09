import base64

import pandas as pd
import pytest

from levseq_dash.app import components, settings, utils
from levseq_dash.app import global_strings as gs


def test_geometry_viewer_type(experiment_ep_pcr_with_user_smiles):
    pdb = utils.get_geometry_for_viewer(experiment_ep_pcr_with_user_smiles)
    assert pdb["type"] == "mol"


def test_geometry_viewer_format(experiment_ep_pcr_with_user_smiles):
    pdb = utils.get_geometry_for_viewer(experiment_ep_pcr_with_user_smiles)
    assert pdb["format"] == "mmcif"


def test_geometry_viewer_length(experiment_ep_pcr_with_user_smiles):
    pdb = utils.get_geometry_for_viewer(experiment_ep_pcr_with_user_smiles)
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
    "input_str,target_index,expected",
    [
        ("abc123def456", 123, True),  # found
        ("abc123def456", 456, True),  # found
        ("abc123def456", 789, False),  # not found
        ("justtext", 123, False),  # no digits
        ("12 34 56", 34, True),  # spaced digits
        ("x99y88z77", 77, True),  # digits scattered
        ("", 1, False),  # empty string
        ("multiple12and12", 12, True),  # duplicates
        ("edge0case1", 0, True),  # check for 0
        ("A53K_T34R", 53, True),
        ("A53K_T34R", 34, True),
        ("#PARENT#", 34, False),
        ("T106C_G118T_T203C_C322T_T552G", 118, True),
        ("T106C_G118T_T203C_C322T_T552G", 22, False),
    ],
)
def test_is_target_index_in_string(input_str, target_index, expected):
    assert utils.is_target_index_in_string(input_str, target_index) == expected


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
    sel, foc = utils.get_selection_focus(residues)
    assert sel["mode"] == "select"
    assert sel["targets"][0]["residue_numbers"] == numbers
    assert foc["analyse"]


@pytest.mark.parametrize(
    "smiles, plate, mean",
    [
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-1", 1823393.4415588235),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-300-2", 599238.9788096774),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-1", 737378.5054485715),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240422-ParLQ-ep1-500-2", 740058.0916967741),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-1", 555981.8641939394),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-2", 363747.4904807692),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-300-3", 472821.28098),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-1", 385903.38386190473),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-2", 273690.4014826087),
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "20240502-ParLQ-ep2-500-3", 578947.396785),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-1", 1340097.0553558823),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-300-2", 574284.2879645161),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-1", 748629.7012771429),
        ("C1=CC=C(C=C1)C=O", "20240422-ParLQ-ep1-500-2", 695933.5473419355),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-1", 416383.57166363636),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-2", 330711.85486538464),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-300-3", 380189.44049999997),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-1", 325416.7923809524),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-2", 216320.55895652174),
        ("C1=CC=C(C=C1)C=O", "20240502-ParLQ-ep2-500-3", 530547.46612),
    ],
)
def test_calculate_group_mean(experiment_ep_pcr, smiles, plate, mean):
    df = utils.calculate_group_mean_ratios_per_smiles_and_plate(experiment_ep_pcr.data_df)
    # if the main core data that is kept in the user session changes column count we need to update this number
    col_count = 14

    assert df.shape[0] == 1920
    assert df.shape[1] == col_count  # added columns
    plate_per_smiles_data_per = df[(df[gs.c_smiles] == smiles) & (df[gs.c_plate] == plate)]  # Filter the row
    assert plate_per_smiles_data_per.shape[0] == 96  # plate count expectation
    assert plate_per_smiles_data_per.shape[1] == col_count
    assert plate_per_smiles_data_per.iloc[0]["mean"] == mean
    assert (plate_per_smiles_data_per["mean"].dropna() == mean).all()

    # ratio must be increasing. this ensures the ranking was done within group
    plate_per_smiles_data_per.fillna(0)
    plate_per_smiles_data_per = plate_per_smiles_data_per.sort_values(by="ratio", ascending=True)
    assert plate_per_smiles_data_per["ratio"].dropna().is_monotonic_increasing


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


def test_decode_dash_upload_data_to_base64_encoded_string_empty():
    """Test a simple csv file with header names and numbers for each column"""

    upload_str = "data:text/csv;base64,QSxCLEMsRCxFLEYKMSwyLDMsNCw1LDYKNyw4LDksMTAsMTEsMTIK"
    result = utils.decode_dash_upload_data_to_base64_encoded_string(upload_str)
    df = utils.decode_csv_file_base64_string_to_dataframe(result)
    assert not df.empty
    assert df.shape[0] == 2
    assert df.shape[1] == 6


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
    sel, foc = utils.get_selection_focus(residue_list, analyse=False)
    assert sel["targets"][0]["residue_numbers"] == target
    assert foc["targets"][0]["residue_numbers"] == target


def test_reset_selection():
    sel = utils.reset_selection()
    assert sel["targets"][0]["residue_numbers"] == []


@pytest.mark.parametrize(
    "max, slider_marks",
    [(2, {"0": "0", "1": "1"}), (1, {"0": "0"}), (0, {})],
)
def test_generate_slider_marks_dict(max, slider_marks):
    result = utils.generate_slider_marks_dict(max)
    assert result == slider_marks


@pytest.mark.parametrize(
    "option, sub_string",
    [
        (components.DownloadType.FILTERED.value, "filteredAndSorted"),
        (components.DownloadType.ORIGINAL.value, "all"),
        (components.DownloadType.FILTERED.value, "filteredAndSorted"),
        (components.DownloadType.ORIGINAL.value, "all"),
    ],
)
def test_export_data_as_csv(option, sub_string):
    _, output = utils.export_data_as_csv(option, "test_file")
    assert sub_string in output["fileName"]
