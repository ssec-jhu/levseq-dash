from pathlib import Path
from unittest import mock

import pytest

from levseq_dash.app.config import settings


def test_package_paths():
    """Test package path configurations"""
    assert isinstance(settings.package_root, Path)
    assert isinstance(settings.package_app_path, Path)
    assert isinstance(settings.config_path, Path)
    assert settings.config_path.name == "config.yaml"


def test_assay_paths():
    """Test assay path configurations"""
    assert isinstance(settings.assay_directory, Path)
    assert isinstance(settings.assay_file_path, Path)
    assert settings.assay_file_name == "assay_measure_list.csv"


def test_app_mode_enum():
    """Test AppMode enum values"""
    assert settings.StorageMode.db.value == "db"
    assert settings.StorageMode.disk.value == "disk"


def test_get_storage_mode(mocker):
    """Test get_storage_mode with different configurations"""
    # Test default value
    mock_load_config = mocker.patch("levseq_dash.app.config.settings.load_config")

    # default value should be disk
    mock_load_config.return_value = {}
    assert settings.get_storage_mode() == "disk"

    # Test explicit mode
    mock_load_config.return_value = {"storage-mode": "db"}
    assert settings.get_storage_mode() == "db"


@mock.patch("levseq_dash.app.config.settings.get_storage_mode")
def test_is_disk_mode(mock_get_storage_mode):
    """Test is_disk_mode function"""
    mock_get_storage_mode.return_value = "disk"
    assert settings.is_disk_mode() is True

    mock_get_storage_mode.return_value = "db"
    assert settings.is_disk_mode() is False


@mock.patch("levseq_dash.app.config.settings.get_storage_mode")
def test_is_db_mode(mock_get_storage_mode):
    """Test is_db_mode function"""
    mock_get_storage_mode.return_value = "db"
    assert settings.is_db_mode() is True

    mock_get_storage_mode.return_value = "disk"
    assert settings.is_db_mode() is False


@mock.patch("levseq_dash.app.config.settings.load_config")
def test_get_disk_settings(mock_load_config):
    """Test get_disk_settings function"""
    mock_config = {"disk": {"setting1": "value1"}}
    mock_load_config.return_value = mock_config
    assert settings.get_disk_settings() == {"setting1": "value1"}

    mock_load_config.return_value = {}
    assert settings.get_disk_settings() == {}


@mock.patch("levseq_dash.app.config.settings.load_config")
def test_get_db_settings(mock_load_config):
    """Test get_db_settings function"""
    mock_config = {"db": {"host": "localhost"}}
    mock_load_config.return_value = mock_config
    assert settings.get_db_settings() == {"host": "localhost"}

    mock_load_config.return_value = {}
    assert settings.get_db_settings() == {}


@mock.patch("levseq_dash.app.config.settings.get_disk_settings")
def test_is_data_modification_enabled(mock_get_disk_settings):
    """Test is_data_modification_enabled function"""
    mock_get_disk_settings.return_value = {"enable-data-modification": True}
    assert settings.is_data_modification_enabled() is True

    mock_get_disk_settings.return_value = {"enable-data-modification": False}
    assert settings.is_data_modification_enabled() is False

    mock_get_disk_settings.return_value = {}
    assert settings.is_data_modification_enabled() is False


def test_load_config():
    """Test load_config function with actual config file"""
    config = settings.load_config()
    assert isinstance(config, dict)
    assert "storage-mode" in config
    assert "deployment-mode" in config


def test_returns_empty_string_when_data_modification_disabled(mock_load_config, mock_is_data_modification_enabled):
    """Test that function returns empty string when data modification is disabled"""
    mock_is_data_modification_enabled.return_value = False
    mock_load_config.return_value = {"five-letter-id-prefix": ""}

    result = settings.get_five_letter_id_prefix()
    assert result == ""


def test_returns_empty_string_when_no_prefix_configured_and_modification_disabled(
    mock_load_config, mock_is_data_modification_enabled
):
    """Test that function returns empty string when no prefix is configured and modification is disabled"""
    mock_is_data_modification_enabled.return_value = False
    mock_load_config.return_value = {}  # No five-letter-id-prefix key

    result = settings.get_five_letter_id_prefix()
    assert result == ""


def test_valid_prefix_when_data_modification_enabled(mock_load_config, mock_is_data_modification_enabled):
    """Test that function returns uppercase prefix when data modification is enabled and prefix is valid"""
    mock_is_data_modification_enabled.return_value = True
    mock_load_config.return_value = {"five-letter-id-prefix": "hello"}

    result = settings.get_five_letter_id_prefix()
    assert result == "HELLO"


def test_valid_prefix_mixed_case_conversion(mock_load_config, mock_is_data_modification_enabled):
    """Test that function converts mixed case prefix to uppercase"""
    mock_is_data_modification_enabled.return_value = True
    mock_load_config.return_value = {"five-letter-id-prefix": "TeSt1"}

    with pytest.raises(ValueError):
        settings.get_five_letter_id_prefix()


def test_valid_prefix_with_whitespace_trimming(mock_load_config, mock_is_data_modification_enabled):
    """Test that function trims whitespace from prefix"""
    mock_is_data_modification_enabled.return_value = True
    mock_load_config.return_value = {"five-letter-id-prefix": "  hello  "}

    with pytest.raises(ValueError):
        settings.get_five_letter_id_prefix()


def test_raises_error_when_prefix_missing_and_modification_enabled(mock_load_config, mock_is_data_modification_enabled):
    """Test that function raises ValueError when prefix key is missing and data modification is enabled"""
    mock_is_data_modification_enabled.return_value = True
    mock_load_config.return_value = {}  # No five-letter-id-prefix key

    with pytest.raises(ValueError):
        settings.get_five_letter_id_prefix()


@pytest.mark.parametrize("prefix", ["", "     ", "abc", "abcdefg", "abc12", "abc@#", "ab cd"])
def test_raises_error_when_prefix_empty_and_modification_enabled(
    mock_load_config, mock_is_data_modification_enabled, prefix
):
    """Test that function raises ValueError when prefix is empty and data modification is enabled"""
    mock_is_data_modification_enabled.return_value = True
    mock_load_config.return_value = {"five-letter-id-prefix": prefix}

    with pytest.raises(ValueError):
        settings.get_five_letter_id_prefix()


# Tests for deployment mode functions
def test_get_deployment_mode(mock_load_config):
    """Test get_deployment_mode with different configurations"""
    # Test default value
    mock_load_config.return_value = {}
    assert settings.get_deployment_mode() == ""

    # Test explicit mode
    mock_load_config.return_value = {"deployment-mode": "local-instance"}
    assert settings.get_deployment_mode() == "local-instance"


def test_is_public_playground_mode(mock_get_deployment_mode):
    """Test is_public_playground_mode function"""
    mock_get_deployment_mode.return_value = "public-playground"
    assert settings.is_public_playground_mode() is True

    mock_get_deployment_mode.return_value = "local-instance"
    assert settings.is_public_playground_mode() is False


def test_is_local_instance_mode(mock_get_deployment_mode):
    """Test is_local_instance_mode function"""
    mock_get_deployment_mode.return_value = "local-instance"
    assert settings.is_local_instance_mode() is True

    mock_get_deployment_mode.return_value = "public-playground"
    assert settings.is_local_instance_mode() is False


@mock.patch("levseq_dash.app.config.settings.get_disk_settings")
def test_get_local_instance_mode_data_path(mock_get_disk_settings):
    """Test get_local_instance_mode_data_path function"""
    mock_get_disk_settings.return_value = {"local-data-path": "/path/to/data"}
    assert settings.get_local_instance_mode_data_path() == "/path/to/data"

    mock_get_disk_settings.return_value = {"local-data-path": ""}
    assert settings.get_local_instance_mode_data_path() == ""

    mock_get_disk_settings.return_value = {}
    assert settings.get_local_instance_mode_data_path() == ""


def test_get_logging_settings(mock_load_config):
    """Test get_logging_settings function"""
    mock_load_config.return_value = {"logging": {"data-manager": True}}
    assert settings.get_logging_settings() == {"data-manager": True}

    mock_load_config.return_value = {}
    assert settings.get_logging_settings() == {}


def test_is_sequence_alignment_profiling_enabled(mock_get_logging_settings):
    """Test is_sequence_alignment_profiling_enabled function"""
    mock_get_logging_settings.return_value = {"sequence-alignment-profiling": True}
    assert settings.is_sequence_alignment_profiling_enabled() is True

    mock_get_logging_settings.return_value = {"sequence-alignment-profiling": False}
    assert settings.is_sequence_alignment_profiling_enabled() is False

    mock_get_logging_settings.return_value = {}
    assert settings.is_sequence_alignment_profiling_enabled() is False


def test_is_data_manager_logging_enabled(mock_get_logging_settings):
    """Test is_data_manager_logging_enabled function"""
    mock_get_logging_settings.return_value = {"data-manager": True}
    assert settings.is_data_manager_logging_enabled() is True

    mock_get_logging_settings.return_value = {"data-manager": False}
    assert settings.is_data_manager_logging_enabled() is False

    mock_get_logging_settings.return_value = {}
    assert settings.is_data_manager_logging_enabled() is False


def test_is_pairwise_aligner_logging_enabled(mock_get_logging_settings):
    """Test is_pairwise_aligner_logging_enabled function"""
    mock_get_logging_settings.return_value = {"pairwise-aligner": True}
    assert settings.is_pairwise_aligner_logging_enabled() is True

    mock_get_logging_settings.return_value = {"pairwise-aligner": False}
    assert settings.is_pairwise_aligner_logging_enabled() is False

    mock_get_logging_settings.return_value = {}
    assert settings.is_pairwise_aligner_logging_enabled() is False


@mock.patch.dict("os.environ", {"FIVE_LETTER_ID_PREFIX": "MYLAB"})
def test_environment_variable_takes_precedence_over_config(mock_load_config, mock_is_data_modification_enabled):
    """Test that environment variable takes precedence over config file"""
    mock_is_data_modification_enabled.return_value = True
    mock_load_config.return_value = {"five-letter-id-prefix": "ABCD"}

    result = settings.get_five_letter_id_prefix()
    assert result == "MYLAB"


@mock.patch.dict("os.environ", {}, clear=True)  # Clear environment variables
def test_falls_back_to_config_when_no_env_var(mock_load_config, mock_is_data_modification_enabled):
    """Test that config file is used when no environment variable is set"""
    mock_is_data_modification_enabled.return_value = True
    mock_load_config.return_value = {"five-letter-id-prefix": "CFGID"}

    result = settings.get_five_letter_id_prefix()
    assert result == "CFGID"


@mock.patch.dict("os.environ", {"FIVE_LETTER_ID_PREFIX": "ENVID"})
def test_environment_variable_when_data_modification_disabled(mock_is_data_modification_enabled):
    """Test that environment variable is not used even when data modification is disabled"""
    mock_is_data_modification_enabled.return_value = False

    result = settings.get_five_letter_id_prefix()
    assert result == ""


@mock.patch.dict("os.environ", {"FIVE_LETTER_ID_PREFIX": "  envid  "})
def test_environment_variable_whitespace_trimming(mock_is_data_modification_enabled):
    """Test that whitespace is trimmed from environment variable"""
    mock_is_data_modification_enabled.return_value = True

    with pytest.raises(ValueError):
        settings.get_five_letter_id_prefix()


@mock.patch.dict("os.environ", {"FIVE_LETTER_ID_PREFIX": "abc"})
def test_environment_variable_validation_error(mock_is_data_modification_enabled):
    """Test that environment variable is validated when data modification is enabled"""
    mock_is_data_modification_enabled.return_value = True

    with pytest.raises(ValueError):
        settings.get_five_letter_id_prefix()


# Tests for get_data_path function
@mock.patch.dict("os.environ", {"DATA_PATH": "/custom/data/path"})
def test_get_data_path_with_env_variable():
    """Test that DATA_PATH environment variable takes precedence"""
    result = settings.get_data_path()
    expected_path = Path("/custom/data/path").resolve()
    assert result == expected_path


@mock.patch.dict("os.environ", {}, clear=True)  # Clear environment variables
def test_get_data_path_playground_mode_default(mock_is_local_instance_mode):
    """Test that playground mode uses app/data/DEDB as default"""
    mock_is_local_instance_mode.return_value = False

    result = settings.get_data_path()
    expected_path = (settings.package_app_path / "data" / "DEDB").resolve()
    assert result == expected_path


@mock.patch.dict("os.environ", {}, clear=True)
def test_get_data_path_local_instance_absolute_path(get_local_instance_mode_data_path, mock_is_local_instance_mode):
    """Test local instance mode with absolute path"""
    mock_is_local_instance_mode.return_value = True
    get_local_instance_mode_data_path.return_value = "/absolute/path/to/data"

    result = settings.get_data_path()
    expected_path = Path("/absolute/path/to/data").resolve()
    assert result == expected_path


@mock.patch.dict("os.environ", {}, clear=True)
def test_get_data_path_local_instance_relative_path(get_local_instance_mode_data_path, mock_is_local_instance_mode):
    """Test local instance mode with relative path"""
    mock_is_local_instance_mode.return_value = True
    get_local_instance_mode_data_path.return_value = "data/custom"

    result = settings.get_data_path()
    expected_path = (settings.package_app_path / "data/custom").resolve()
    assert result == expected_path


@mock.patch.dict("os.environ", {}, clear=True)
def test_get_data_path_local_instance_no_path_configured(
    get_local_instance_mode_data_path, mock_is_local_instance_mode
):
    """Test local instance mode with no path configured raises error"""
    mock_is_local_instance_mode.return_value = True
    get_local_instance_mode_data_path.return_value = ""

    with pytest.raises(ValueError):
        settings.get_data_path()


@mock.patch.dict("os.environ", {}, clear=True)
def test_get_data_path_local_instance_none_path_configured(
    get_local_instance_mode_data_path, mock_is_local_instance_mode
):
    """Test local instance mode with None path configured raises error"""
    mock_is_local_instance_mode.return_value = True
    get_local_instance_mode_data_path.return_value = None

    with pytest.raises(ValueError, match="local-instance MODE ERROR"):
        settings.get_data_path()


@mock.patch.dict("os.environ", {"DATA_PATH": "/env/override"})
def test_get_data_path_env_overrides_local_instance(get_local_instance_mode_data_path, mock_is_local_instance_mode):
    """Test that DATA_PATH environment variable overrides local instance config"""
    mock_is_local_instance_mode.return_value = True
    get_local_instance_mode_data_path.return_value = "/config/path"

    result = settings.get_data_path()
    expected_path = Path("/env/override").resolve()
    assert result == expected_path


@mock.patch.dict("os.environ", {"DATA_PATH": "/env/override"})
def test_get_data_path_env_overrides_playground(mock_is_local_instance_mode):
    """Test that DATA_PATH environment variable overrides playground mode default"""
    mock_is_local_instance_mode.return_value = False

    result = settings.get_data_path()
    expected_path = Path("/env/override").resolve()
    assert result == expected_path
