import hashlib
import io
import os
import threading
from unittest import mock

import pytest

from levseq_dash.app import global_strings as gs
from levseq_dash.app.utils import utils


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
