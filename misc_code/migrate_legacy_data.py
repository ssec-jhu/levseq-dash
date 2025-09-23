import datetime
import json
import shutil
from pathlib import Path

import pandas as pd

from levseq_dash.app.data_manager.experiment import Experiment
from levseq_dash.app.data_manager.manager import BaseDataManager
from levseq_dash.app.utils import u_reaction


def migrate_legacy_data_to_uuid_structure(input_data_path: Path, output_data_path, meta_data_file_name) -> None:
    meta_data_file = input_data_path / meta_data_file_name
    experiments_dir = input_data_path / "experiments"
    structures_dir = input_data_path / "structures"

    if not meta_data_file.exists():
        raise FileNotFoundError(f"meta_data.csv not found at {meta_data_file}")
    if not experiments_dir.exists():
        raise FileNotFoundError(f"experiments directory not found at {experiments_dir}")
    if not structures_dir.exists():
        raise FileNotFoundError(f"structures directory not found at {structures_dir}")

    # Read metadata CSV
    # df_metadata = pd.read_csv(meta_data_file)
    df_metadata = pd.read_excel(meta_data_file)

    total_experiments = len(df_metadata)
    successful_migrations = 0
    failed_migrations = 0

    print(f"Starting migration of {total_experiments} experiments...")

    # Process each experiment
    for index, row in df_metadata.iterrows():
        experiment_id = None
        try:
            experiment_id = row["experiment_id"]
            id_prefix = row["prefix"]
            # experiment name
            experiment_name = row["experiment_name"]
            experiment_name = experiment_name.replace(".csv", "").strip()

            # experiment date
            experiment_date = pd.to_datetime(row["experiment_date"]).strftime("%Y-%m-%d")

            # smiles strings
            substrate_smiles = str(row["substrate_smiles"]).strip()
            product_smiles = str(row["product_smiles"]).strip()

            # Handle common invalid values for substrate (substrate can be empty)
            if substrate_smiles.lower() in ["nan", "none", "null", ""]:
                substrate_smiles = ""

            # Handle common invalid values for product (product must not be empty)
            if product_smiles.lower() in ["nan", "none", "null", ""]:
                raise ValueError(f"Product SMILES cannot be empty or invalid: {row['product_smiles']}")

            # validate smiles (skip validation for empty substrate, but product must be valid)
            if substrate_smiles and not u_reaction.is_valid_smiles(substrate_smiles):
                raise ValueError(f"Invalid substrate SMILES: {substrate_smiles}")
            if not product_smiles:
                raise ValueError("Product SMILES is required and cannot be empty")
            if not u_reaction.is_valid_smiles(product_smiles):
                raise ValueError(f"Invalid product SMILES: {product_smiles}")

            assay_technique = row["assay_technique"]

            additional_info = row["additional_information"]

            # Find CIF structure file
            cif_filename = row["cif_filename"]
            exp_cif_file = structures_dir / cif_filename
            if not exp_cif_file.exists():
                raise ValueError(f"CIF structure file for not found: {exp_cif_file}")

            # Find experiment CSV file

            exp_csv_file = experiments_dir / f"{experiment_id}.csv"
            if not exp_csv_file.exists():
                raise ValueError(f"Experiment CSV file not found: {exp_csv_file}")

            # run sanity check on the experiment CSV file
            df = pd.read_csv(exp_csv_file)
            passed_sanity_check = Experiment.run_sanity_checks_on_experiment_file(df)
            if not passed_sanity_check:
                raise ValueError(f"Experiment CSV file failed sanity check: {exp_csv_file}")

            # checksum calculation
            with open(exp_csv_file, "rb") as f:
                csv_bytes = f.read()
                csv_checksum = BaseDataManager.calculate_file_checksum(csv_bytes)

            # Calculate plates count and get CSV checksum
            plates_count = len(Experiment.extract_plates_list(df))
            parent_sequence = Experiment.extract_parent_sequence(df)

            # Create metadata dictionary
            upload_time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Generate new UUID
            experiment_uuid = BaseDataManager.generate_experiment_id(id_prefix)

            metadata = {
                "experiment_id": experiment_uuid,
                "experiment_name": experiment_name,
                "experiment_date": experiment_date,
                "substrate": substrate_smiles,
                "product": product_smiles,
                "assay": assay_technique,
                "mutagenesis_method": "Across Sequence",  # Default for legacy data
                "parent_sequence": parent_sequence,
                "plates_count": plates_count,
                "csv_checksum": csv_checksum,
                "additional_information": additional_info,
                "upload_time_stamp": upload_time_stamp,
            }

            # Create UUID-based directory structure
            experiment_dir = output_data_path / experiment_uuid
            experiment_dir.mkdir(parents=True, exist_ok=True)

            # Generate file paths
            json_file_path = experiment_dir / f"{experiment_uuid}.json"
            csv_file_path = experiment_dir / f"{experiment_uuid}.csv"
            cif_file_path = experiment_dir / f"{experiment_uuid}.cif"

            # Save metadata as JSON
            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(metadata, json_file, indent=4)

            # Copy experiment CSV data (mimicking file upload process)
            shutil.copy(exp_csv_file, csv_file_path)
            shutil.copy(exp_cif_file, cif_file_path)

            # Verify files were copied successfully
            if not csv_file_path.exists() or csv_file_path.stat().st_size == 0:
                raise ValueError(f"Failed to copy CSV file to {csv_file_path}")
            if not cif_file_path.exists() or cif_file_path.stat().st_size == 0:
                raise ValueError(f"Failed to copy CIF file to {cif_file_path}")

            # print(f"Successfully migrated experiment {experiment_id} -> {experiment_uuid}")
            successful_migrations += 1

        except Exception as e:
            exp_ref = experiment_id if experiment_id else f"row {index}"
            print(f"Experiment {exp_ref}: {e}")
            failed_migrations += 1
            continue

    # Print migration summary
    print(f"\nMigration Summary:")
    print(f"Total experiments: {total_experiments}")
    print(f"Successful migrations: {successful_migrations}")
    print(f"Failed migrations: {failed_migrations}")
    print(f"Success rate: {(successful_migrations / total_experiments) * 100:.1f}%")


# Example usage for migration:
# To migrate legacy data structure to UUID-based structure, use:
#


migrate_legacy_data_to_uuid_structure(
    input_data_path=Path("/Users/Fatemeh/Desktop/DEDB"),
    output_data_path=Path("/Users/Fatemeh/Desktop/DEDB_converted"),
    meta_data_file_name="meta_data.xlsx",
)

print(f"Migration completed.")
