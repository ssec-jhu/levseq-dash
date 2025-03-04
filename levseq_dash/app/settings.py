from pathlib import Path

import yaml

package_root = Path(__file__).resolve().parent.parent
config_path = package_root / "app" / "config" / "config.yaml"


def load_config():
    with open(config_path, "r") as file:
        config_file = yaml.safe_load(file)
        return config_file
