from pathlib import Path
from unittest import mock

import pytest
import yaml

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
    assert settings.AppMode.db.value == "db"
    assert settings.AppMode.disk.value == "disk"


def test_get_app_mode(mocker):
    """Test get_app_mode with different configurations"""
    # Test default value
    mock_load_config = mocker.patch("levseq_dash.app.config.settings.load_config")

    mock_load_config.return_value = {}
    assert settings.get_app_mode() == "disk"

    # Test explicit mode
    mock_load_config.return_value = {"app-mode": "db"}
    assert settings.get_app_mode() == "db"


@mock.patch("levseq_dash.app.config.settings.get_app_mode")
def test_is_disk_mode(mock_get_app_mode):
    """Test is_disk_mode function"""
    mock_get_app_mode.return_value = "disk"
    assert settings.is_disk_mode() is True

    mock_get_app_mode.return_value = "db"
    assert settings.is_disk_mode() is False


@mock.patch("levseq_dash.app.config.settings.get_app_mode")
def test_is_db_mode(mock_get_app_mode):
    """Test is_db_mode function"""
    mock_get_app_mode.return_value = "db"
    assert settings.is_db_mode() is True

    mock_get_app_mode.return_value = "disk"
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
    mock_get_disk_settings.return_value = {"enable_data_modification": True}
    assert settings.is_data_modification_enabled() is True

    mock_get_disk_settings.return_value = {"enable_data_modification": False}
    assert settings.is_data_modification_enabled() is False

    mock_get_disk_settings.return_value = {}
    assert settings.is_data_modification_enabled() is False


def test_load_config():
    """Test load_config function with actual config file"""
    config = settings.load_config()
    assert isinstance(config, dict)
    assert "app-mode" in config
