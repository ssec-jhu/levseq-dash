from enum import Enum
from pathlib import Path

import yaml

package_root = Path(__file__).resolve().parent.parent.parent
package_app_path = package_root / "app"
config_path = package_app_path / "config" / "config.yaml"

# do not change this if you don't know what you're doing
assay_directory = package_app_path / "tests" / "test_data" / "assay"
assay_file_name = "assay_measure_list.csv"
assay_file_path = assay_directory / assay_file_name


class StorageMode(Enum):
    db = "db"  # not implemeted
    disk = "disk"


class DeploymentMode(Enum):
    public_playground = "public-playground"
    local_instance = "local-instance"


def load_config():
    with open(config_path, "r") as file:
        config_file = yaml.safe_load(file)
    return config_file


def get_storage_mode():
    config = load_config()
    return config.get("storage-mode", "disk")


def is_disk_mode():
    return get_storage_mode() == StorageMode.disk.value


def is_db_mode():
    return get_storage_mode() == StorageMode.db.value


def get_deployment_mode():
    config = load_config()
    # default to "public-playground" if not set
    return config.get("deployment-mode", "public-playground")


def is_public_playground_mode():
    return get_deployment_mode() == DeploymentMode.public_playground.value


def is_local_instance_mode():
    return get_deployment_mode() == DeploymentMode.local_instance.value


def get_local_instance_mode_data_path():
    """
    Get the local development path for local-instance mode from disk settings.
    Returns None if not set or empty string.
    """
    disk_settings = get_disk_settings()
    data_path = disk_settings.get("local-data-path", "")
    return data_path


def get_disk_settings():
    config = load_config()
    return config.get("disk", {})


def get_db_settings():
    config = load_config()
    return config.get("db", {})


def get_logging_settings():
    config = load_config()
    return config.get("logging", {})


def is_data_modification_enabled():
    disk_settings = get_disk_settings()
    modification_enabled = disk_settings.get("enable-data-modification", False)

    return modification_enabled


def is_sequence_alignment_profiling_enabled():
    log_settings = get_logging_settings()
    return log_settings.get("sequence-alignment-profiling", False)


def is_data_manager_logging_enabled():
    log_settings = get_logging_settings()
    return log_settings.get("data-manager", False)


def is_pairwise_aligner_logging_enabled():
    log_settings = get_logging_settings()
    return log_settings.get("pairwise-aligner", False)
