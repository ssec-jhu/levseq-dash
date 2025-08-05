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


class AppMode(Enum):
    db = "db"
    disk = "disk"


def load_config():
    with open(config_path, "r") as file:
        config_file = yaml.safe_load(file)
    return config_file


def get_app_mode():
    config = load_config()
    return config.get("app-mode", "disk")


def is_disk_mode():
    return get_app_mode() == AppMode.disk.value


def is_db_mode():
    return get_app_mode() == AppMode.db.value


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
    return disk_settings.get("enable_data_modification", False)


def is_sequence_alignment_profiling_enabled():
    log_settings = get_logging_settings()
    return log_settings.get("sequence_alignment_profiling", False)


def is_data_manager_logging_enabled():
    log_settings = get_logging_settings()
    return log_settings.get("data_manager", False)


def is_pairwise_aligner_logging_enabled():
    log_settings = get_logging_settings()
    return log_settings.get("pairwise_aligner", False)


def is_parallel_sequence_alignment_enabled():
    """
    Returns whether parallel sequence alignment is enabled based on the config.
    """
    config = load_config()
    return config.get("parallel_sequence_alignment", False)
