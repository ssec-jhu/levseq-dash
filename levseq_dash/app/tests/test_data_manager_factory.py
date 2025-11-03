import pytest

from levseq_dash.app.data_manager.manager import validate_deployment_configuration


def test_validate_deployment_configuration_public_playground_valid(mocker, load_config_mock_string):
    """Test valid public-playground mode configuration."""

    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "public-playground",
    }

    # Should not raise any exception
    validate_deployment_configuration()


def test_validate_deployment_configuration_public_playground_data_modification_enabled(mocker, load_config_mock_string):
    """Test public-playground mode with data modification enabled (invalid)."""

    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "public-playground",
        "storage-mode": "disk",
        "disk": {
            "enable-data-modification": True,
        },
    }

    with pytest.raises(ValueError):
        validate_deployment_configuration()


def test_validate_deployment_configuration_public_playground_with_local_data_path(mocker, load_config_mock_string):
    """Test public-playground mode with local-data-path set (invalid)."""

    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "public-playground",  # public-playground mode should not have local-data-path set
        "storage-mode": "disk",
        "disk": {
            "local-data-path": "/some/valid/path",
            "enable-data-modification": False,
            "five-letter-id-prefix": "",
        },
    }

    with pytest.raises(ValueError):
        validate_deployment_configuration()


def test_validate_deployment_configuration_local_instance_valid(mocker, load_config_mock_string):
    """Test valid local-instance mode configuration."""
    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {"local-data-path": "/some/valid/path"},
    }

    # Should not raise any exception
    validate_deployment_configuration()


def test_validate_deployment_configuration_local_instance_data_path_error(mocker, load_config_mock_string):
    """Test local-instance mode with invalid data path configuration."""

    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {},  # missing path
    }

    with pytest.raises(ValueError):
        validate_deployment_configuration()


def test_validate_deployment_configuration_local_instance_with_modification_no_prefix(mocker, load_config_mock_string):
    """Test local-instance mode with data modification but no ID prefix."""

    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {
        "deployment-mode": "local-instance",
        "storage-mode": "disk",
        "disk": {
            "local-data-path": "/some/valid/path",
            "enable-data-modification": True,
            "five-letter-id-prefix": "",  # missing prefix
        },
    }

    with pytest.raises(ValueError):
        validate_deployment_configuration()


def test_validate_deployment_configuration_invalid_deployment_mode(mocker, load_config_mock_string):
    """Test invalid deployment mode."""

    mock = mocker.patch(load_config_mock_string)
    mock.return_value = {"deployment-mode": "some-other-mode", "storage-mode": "disk"}

    with pytest.raises(ValueError):
        validate_deployment_configuration()
