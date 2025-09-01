import base64
import hashlib
from unittest import mock
from unittest.mock import patch

import pandas as pd
import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import column_definitions as cd
from levseq_dash.app.components.widgets import DownloadType
from levseq_dash.app.utils import utils


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
    plate_per_smiles_data_per = plate_per_smiles_data_per.sort_values(by=gs.cc_ratio, ascending=True)
    assert plate_per_smiles_data_per[gs.cc_ratio].dropna().is_monotonic_increasing


def test_get_top_variant_column_defs(experiment_ep_pcr):
    df_filtered_with_ratio = utils.calculate_group_mean_ratios_per_smiles_and_plate(experiment_ep_pcr.data_df)
    d = cd.get_top_variant_column_defs(df_filtered_with_ratio)
    assert len(d) == 6


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


# @pytest.mark.parametrize(
#     "max, slider_marks",
#     [(2, {"0": "0", "1": "1"}), (1, {"0": "0"}), (0, {})],
# )
# def test_generate_slider_marks_dict(max, slider_marks):
#     result = utils.generate_slider_marks_dict(max)
#     assert result == slider_marks


@pytest.mark.parametrize(
    "option, sub_string",
    [
        (DownloadType.FILTERED.value, "filteredAndSorted"),
        (DownloadType.ORIGINAL.value, "all"),
        (DownloadType.FILTERED.value, "filteredAndSorted"),
        (DownloadType.ORIGINAL.value, "all"),
    ],
)
def test_export_data_as_csv(option, sub_string):
    _, output = utils.export_data_as_csv(option, "test_file")
    assert sub_string in output["fileName"]


def test_validate_smiles_string_valid_smiles():
    valid_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # aspirin
    with patch("levseq_dash.app.utils.utils.u_reaction.is_valid_smiles", return_value=True):
        valid, invalid = utils.validate_smiles_string(valid_smiles)
        assert valid is True
        assert invalid is False


def test_validate_smiles_string_invalid_smiles():
    invalid_smiles = "C1CC1C(=O)(O"  # broken ring
    with patch("levseq_dash.app.utils.utils.u_reaction.is_valid_smiles", return_value=False):
        valid, invalid = utils.validate_smiles_string(invalid_smiles)
        assert valid is False
        assert invalid is True


def test_validate_smiles_string_smiles_raises_exception():
    # You can simulate errors in the function you're mocking
    # with patch("your_module.u_reaction.is_valid_smiles", side_effect=Exception("something went wrong")):
    with patch("levseq_dash.app.utils.utils.u_reaction.is_valid_smiles", side_effect=Exception("Error")):
        valid, invalid = utils.validate_smiles_string("bad_input")
        assert valid is False
        assert invalid is True


def test_returns_first_row_when_data_is_present():
    data = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = utils.select_first_row_of_data(data)
    assert result == [{"id": 1}]


def test_returns_none_when_data_is_empty():
    data = []
    result = utils.select_first_row_of_data(data)
    assert result is None


def test_returns_none_when_data_is_none():
    result = utils.select_first_row_of_data(None)
    assert result is None


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("A123B456C", ["123", "456"]),
        ("X1Y2Z3", ["1", "2", "3"]),
        ("A53K_T34R", ["53", "34"]),
        ("T106C_G118T_T203C_C322T_T552G", ["106", "118", "203", "322", "552"]),
        ("nodigits", []),
        ("", []),
        ("123456", ["123456"]),
        ("#PARENT#", []),
        ("A14G", ["14"]),
        ("V127A_K120R_F89L", ["127", "120", "89"]),
    ],
)
def test_extract_all_indices(input_str, expected):
    """Test the extract_all_indices function"""

    result = utils.extract_all_indices(input_str)
    assert result == expected


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


def test_extract_smiles_empty_list():
    """Test with empty list"""
    result = utils.extract_all_substrate_product_smiles_from_lab_data([])
    assert result == ("", "")


def test_extract_smiles_single_experiment():
    """Test with single experiment"""
    experiments = [{gs.cc_substrate: "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", gs.cc_product: "C1=CC=C(C=C1)C=O"}]
    substrate, product = utils.extract_all_substrate_product_smiles_from_lab_data(experiments)
    assert substrate == "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
    assert product == "C1=CC=C(C=C1)C=O"


def test_extract_smiles_multiple_experiments():
    """Test with multiple experiments"""
    experiments = [
        {gs.cc_substrate: "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", gs.cc_product: "C1=CC=C(C=C1)C=O"},
        {gs.cc_substrate: "CC(=O)O", gs.cc_product: "CCO"},
        {
            gs.cc_substrate: "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Duplicate
            gs.cc_product: "C1=CC=C(C=C1)C=O",  # Duplicate
        },
    ]
    substrate, product = utils.extract_all_substrate_product_smiles_from_lab_data(experiments)

    # Results should be sorted and deduplicated
    expected_substrates = ["CC(=O)O", "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"]
    expected_products = ["C1=CC=C(C=C1)C=O", "CCO"]

    assert substrate == ";  ".join(expected_substrates)
    assert product == ";  ".join(expected_products)


def test_extract_smiles_multiple_unique_experiments():
    """Test with multiple unique experiments"""
    experiments = [
        {gs.cc_substrate: "CCC", gs.cc_product: "CCO"},
        {gs.cc_substrate: "AAA", gs.cc_product: "BBB"},
        {gs.cc_substrate: "ZZZ", gs.cc_product: "XXX"},
    ]
    substrate, product = utils.extract_all_substrate_product_smiles_from_lab_data(experiments)

    # Should be sorted
    assert substrate == "AAA;  CCC;  ZZZ"
    assert product == "BBB;  CCO;  XXX"


@pytest.fixture
def mock_print():
    """Fixture for mocking print"""
    with mock.patch("builtins.print") as mock_print:
        yield mock_print


def test_log_disabled(mock_print):
    """Test that nothing is logged when flag is False"""
    utils.log_with_context("Test message", False)
    mock_print.assert_not_called()


def test_log_enabled(mock_print):
    """Test that message is logged when flag is True"""
    utils.log_with_context("Test message", True)
    mock_print.assert_called_once()

    # Check that the log message contains expected components
    call_args = mock_print.call_args[0][0]
    assert "Test message" in call_args
    assert "[PID:" in call_args
    assert "[TID:" in call_args
    assert "[FUNC:" in call_args


@mock.patch("os.getpid", return_value=12345)
@mock.patch("threading.get_ident", return_value=67890)
@mock.patch("threading.current_thread")
def test_log_format(mock_thread, mock_tid, mock_pid, mock_print):
    """Test the exact format of the log message"""
    mock_thread.return_value.name = "MainThread"

    utils.log_with_context("Test message", True)

    call_args = mock_print.call_args[0][0]
    assert "[PID:12345]" in call_args
    assert "[TID:67890]" in call_args
    assert "[MainThread]" in call_args
    assert "[FUNC:test_log_format]" in call_args
    assert "Test message" in call_args


def test_valid_checksum():
    """Test checksum calculation with valid bytes"""
    test_bytes = b"Hello, World!"
    result = utils.calculate_file_checksum(test_bytes)

    # Calculate expected checksum manually
    expected = hashlib.sha256(test_bytes).hexdigest()
    assert result == expected
    assert isinstance(result, str)
    assert len(result) == 64  # SHA256 hex string length


def test_empty_bytes_raises_error():
    """Test that empty bytes raises ValueError"""
    with pytest.raises(ValueError):
        utils.calculate_file_checksum(b"")


def test_none_bytes_raises_error():
    """Test that None bytes raises ValueError"""
    with pytest.raises(ValueError):
        utils.calculate_file_checksum(None)


def test_wrong_type_raises_error():
    """Test that non-bytes input raises TypeError"""
    with pytest.raises(TypeError):
        utils.calculate_file_checksum("not bytes")

    with pytest.raises(TypeError):
        utils.calculate_file_checksum(123)

    with pytest.raises(TypeError):
        utils.calculate_file_checksum(["not", "bytes"])


def test_different_inputs_different_checksums():
    """Test that different inputs produce different checksums"""
    bytes1 = b"content1"
    bytes2 = b"content2"

    checksum1 = utils.calculate_file_checksum(bytes1)
    checksum2 = utils.calculate_file_checksum(bytes2)

    assert checksum1 != checksum2


def test_same_input_same_checksum():
    """Test that same input always produces same checksum"""
    test_bytes = b"consistent content"

    checksum1 = utils.calculate_file_checksum(test_bytes)
    checksum2 = utils.calculate_file_checksum(test_bytes)

    assert checksum1 == checksum2


@pytest.mark.parametrize(
    "test_input, expected_length",
    [
        (b"short", 64),
        (b"a" * 1000, 64),  # longer input
        (b"\x00\x01\x02\x03", 64),  # binary data
    ],
)
def test_checksum_length_consistency(test_input, expected_length):
    """Test that checksum always has consistent length regardless of input"""
    result = utils.calculate_file_checksum(test_input)
    assert len(result) == expected_length


def test_known_checksum_value():
    """Test against a known SHA256 value"""
    # "hello" in SHA256 is a well-known value
    test_bytes = b"hello"
    result = utils.calculate_file_checksum(test_bytes)
    expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert result == expected
