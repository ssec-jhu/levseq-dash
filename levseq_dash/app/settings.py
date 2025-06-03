from pathlib import Path

import yaml

package_root = Path(__file__).resolve().parent.parent
package_app_path = package_root / "app"

config_path = package_app_path / "config" / "config.yaml"

# do not change this if you don't know what you're doing
assay_directory = package_app_path / "tests" / "test_data" / "assay"
assay_file_name = "assay_measure_list.csv"
assay_file_path = assay_directory / assay_file_name


def load_config():
    with open(config_path, "r") as file:
        config_file = yaml.safe_load(file)
        return config_file
