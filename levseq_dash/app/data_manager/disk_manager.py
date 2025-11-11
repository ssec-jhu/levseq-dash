import base64
import datetime
import io
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
from cachetools import LRUCache

from levseq_dash.app.config import settings
from levseq_dash.app.data_manager.base import BaseDataManager
from levseq_dash.app.data_manager.experiment import Experiment, MutagenesisMethod
from levseq_dash.app.utils import utils


class DiskDataManager(BaseDataManager):
    """
    Disk-based data manager for storing experiment data locally.
    """

    def __init__(self):
        """
        Initialize the disk-based data manager.
        """
        super().__init__()

        # Set up the data path
        self._setup_data_path()

        # Store experiment metadata index (UUID -> metadata dict)
        self._experiments_metadata = {}

        # Cache for loaded experiment objects (UUID -> Experiment object)
        # self.experiments_cache = {}
        self._experiments_core_data_cache = LRUCache(maxsize=20)

        self.five_letter_id_prefix = settings.get_five_letter_id_prefix()

        # read the assay file and set up the assay list
        self._load_assay_list()

        self._load_all_experiments_metadata_into_memory()

    # -----------------------
    #       ADD DATA
    # -----------------------

    def add_experiment_from_ui(
        self,
        experiment_name,
        experiment_date,
        substrate,
        product,
        assay,
        mutagenesis_method: MutagenesisMethod,  # epPCR or SSM
        experiment_doi: str,
        experiment_additional_info: str,
        experiment_content_base64_string,
        geometry_content_base64_string,
    ) -> str:
        """
        Add a new experiment and return its UUID.
        """
        # Duplicate data check has already passed in upload by check_for_duplicate_experiment
        # Sanity check has already passed in upload by run_sanity_checks_on_experiment_file

        # Generate a UUID for the experiment
        experiment_uuid = self.generate_experiment_id(id_prefix=self.five_letter_id_prefix)

        # assign a timestamp for the upload
        upload_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # convert to dataframe for processing
        df, experiment_bytes = utils.decode_csv_file_base64_string_to_dataframe(experiment_content_base64_string)

        # calculate a checksum for the CSV file
        csv_checksum = self.calculate_file_checksum(experiment_bytes)

        # calculate the number of plates in the experiment
        plates_count = len(Experiment.extract_plates_list(df))

        # extract parent sequence from the CSV - sanity check already checks that such a row exists
        # note at this point the aa_sequence column exists. We don't read this column anymore because it uses up memory
        parent_sequence = Experiment.extract_parent_sequence(df)

        metadata = {
            "experiment_id": experiment_uuid,
            "experiment_name": experiment_name,
            "doi": experiment_doi,
            "experiment_date": experiment_date,
            "substrate": substrate,
            "product": product,
            "assay": assay,
            "mutagenesis_method": mutagenesis_method,
            "parent_sequence": parent_sequence,
            "plates_count": plates_count,
            "csv_checksum": csv_checksum,
            "additional_information": experiment_additional_info,
            "upload_time_stamp": upload_time_stamp,
        }

        # Save metadata as a JSON file
        self._create_experiment_directory(experiment_uuid)
        json_file_path, csv_file_path, cif_file_path = self._generate_file_paths_for_experiment(experiment_uuid)

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(metadata, json_file, indent=4)

        # save experiment data as CSV
        df.to_csv(csv_file_path, index=False)

        # Save geometry content if provided
        if geometry_content_base64_string:
            # decode to text (assuming it's UTF-8 encoded)
            decoded_text = base64.b64decode(geometry_content_base64_string).decode("utf-8")
            with open(cif_file_path, "w", encoding="utf-8") as f:
                f.write(decoded_text)

        # add the newly added experiment to the metadata list
        self._experiments_metadata[experiment_uuid] = metadata

        return experiment_uuid

    def check_for_duplicate_experiment(self, new_csv_checksum: str):
        """
        Check if an experiment with the same checksum already exists.
        """
        for experiment_uuid, metadata in self._experiments_metadata.items():
            existing_checksum = metadata.get("csv_checksum", "")
            if existing_checksum == new_csv_checksum:
                existing_name = metadata.get("experiment_name", "Unknown")
                raise ValueError(
                    f"DUPLICATE experiment data detected! "
                    f"An experiment with identical CSV data already exists with UUID: {experiment_uuid}"
                    f" and Name: {existing_name}."
                )
        return False

    # ---------------------------
    #    Delete
    # ---------------------------
    def delete_experiment(self, experiment_uuid: str) -> bool:
        """
        Delete an experiment by UUID.

        Returns:
            bool: True if deleted successfully.
        """
        if experiment_uuid not in self._experiments_metadata:
            return False

        try:
            # Get experiment directory
            experiment_dir = self.data_path / experiment_uuid

            # Remove directory and all contents
            if experiment_dir.exists():
                import shutil

                deleted_exp_dir = self.data_path / "DELETED_EXP"
                deleted_exp_dir.mkdir(exist_ok=True)

                # Add timestamp to prevent any naming conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                target_path = deleted_exp_dir / f"{experiment_dir.name}_{timestamp}"

                # Move the experiment directory to DELETED_EXP folder with timestamp
                shutil.move(str(experiment_dir), str(target_path))

            # Remove from in-memory metadata
            del self._experiments_metadata[experiment_uuid]

            # Remove from cache if it exists
            if experiment_uuid in self._experiments_core_data_cache:
                del self._experiments_core_data_cache[experiment_uuid]

            return True

        except Exception as e:
            raise RuntimeError(f"Error deleting experiment {experiment_uuid} from disk: {e}") from e

    # ---------------------------
    #    DATA RETRIEVAL: ALL
    # ---------------------------
    def get_all_lab_experiments_with_meta_data(self):
        """
        Get metadata for all experiments.

        Returns:
            list: List of experiment metadata dictionaries.
        """
        return list(self._experiments_metadata.values())

    def get_all_lab_sequences(self):
        """
        Get parent sequences for all experiments.

        Returns:
            dict: Dictionary mapping experiment UUIDs to parent sequences.
        """
        seq_data = {}
        # dictionary of "experiment UUID" and "experiment sequence" pairs
        # the key of the dictionary is the experiment UUID
        for experiment_uuid, metadata in self._experiments_metadata.items():
            seq_data.update({experiment_uuid: metadata.get("parent_sequence", "")})
        return seq_data

    # ---------------------------
    #    DATA RETRIEVAL: PER EXPERIMENT
    # ---------------------------
    def get_experiment_metadata(self, experiment_uuid: str) -> dict | None:
        """
        Get metadata for a specific experiment.
        """
        return self._experiments_metadata.get(experiment_uuid, None)

    def get_experiment(self, experiment_uuid: str) -> Experiment | None:
        """
        Get the Experiment object for a specific UUID.
        """
        try:
            exp = None
            # Check cache first
            if experiment_uuid in self._experiments_core_data_cache:
                return self._experiments_core_data_cache[experiment_uuid]

            # Load from disk
            _, csv_file_path, cif_file_path = self._generate_file_paths_for_experiment(experiment_uuid)
            exp = Experiment(experiment_data_file_path=csv_file_path, geometry_file_path=cif_file_path)
            # Cache the loaded experiment
            if exp:
                self._experiments_core_data_cache[experiment_uuid] = exp

            return exp
        except Exception as e:
            raise Exception(f"Error loading experiment {experiment_uuid} from disk: {e}")

    def get_experiment_file_content(self, experiment_uuid: str) -> dict[str, bytes]:
        """
        Get experiment files content as bytes for a specific experiment.
        This is the implementation for a local file storage retriever.
        """
        files_content = {}
        if experiment_uuid not in self._experiments_metadata:
            return files_content

        try:
            json_path, csv_path, cif_path = self._generate_file_paths_for_experiment(experiment_uuid)

            if json_path.exists():
                files_content["json"] = json_path.read_bytes()
            if csv_path.exists():
                files_content["csv"] = csv_path.read_bytes()
            if cif_path.exists():
                files_content["cif"] = cif_path.read_bytes()

        except Exception as e:
            raise Exception(f"Error reading files for experiment: {experiment_uuid}: {e}")

        return files_content

    # ---------------------------
    #    DATA RETRIEVAL: MISC
    # ---------------------------
    def get_assays(self):
        """
        Get the list of available assays.

        Returns:
            list: List of assay names.
        """
        return self.assay_list

    def get_experiments_zipped(self, experiments_to_zip: list[dict[str]]) -> bytes | None:
        if not experiments_to_zip or len(experiments_to_zip) == 0:
            return None

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            # Add metadata CSV to root of zip
            # Use pandas to properly handle CSV escaping (commas, quotes, newlines in fields)
            metadata_df = pd.DataFrame(experiments_to_zip)
            csv_content = metadata_df.to_csv(index=False)
            zipf.writestr(f"EnzEngDB_Experiments.csv", csv_content)

            # Add experiment files directly from disk
            for exp_data in experiments_to_zip:
                experiment_id = exp_data.get("experiment_id")
                if experiment_id:
                    try:
                        # get the file contents, bytes,...
                        file_contents = self.get_experiment_file_content(experiment_id)

                        # Add files to ZIP using content-based approach
                        if "json" in file_contents:
                            zipf.writestr(f"experiments/{experiment_id}/{experiment_id}.json", file_contents["json"])
                        if "csv" in file_contents:
                            zipf.writestr(f"experiments/{experiment_id}/{experiment_id}.csv", file_contents["csv"])
                        if "cif" in file_contents:
                            zipf.writestr(f"experiments/{experiment_id}/{experiment_id}.cif", file_contents["cif"])

                    except Exception as e:
                        raise Exception(f"Error adding files for experiment {experiment_id}: {e}")

        # Get the ZIP data from memory buffer
        zip_data = zip_buffer.getvalue()
        zip_buffer.close()

        return zip_data

    # ----------------------------
    #    PRIVATE METHODS
    # ---------------------------

    def _setup_data_path(self):
        """
        Set up the data storage path.
        """

        self.data_path = settings.get_data_path()

        utils.log_with_context(
            f"[LOG] Using path: {self.data_path})",
            log_flag=settings.is_data_manager_logging_enabled(),
        )

        # Sanity checks on the directory
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data directory not found at {self.data_path}\n")

        # Check if the path is writable
        if settings.is_data_modification_enabled() and not os.access(self.data_path, os.W_OK):
            raise PermissionError(f"No write permission to storage: {self.data_path}\n")

    def _load_assay_list(self):
        """
        Load the list of assays from the assay file.
        """
        if settings.assay_file_path.exists():
            assays = pd.read_csv(settings.assay_file_path, encoding="utf-8", usecols=["Technique"])
            self.assay_list = assays["Technique"].tolist()
            utils.log_with_context(
                f"[LOG] Read assay file at: {settings.assay_file_path} with size {len(self.assay_list)}",
                log_flag=settings.is_data_manager_logging_enabled(),
            )

    def _load_all_experiments_metadata_into_memory(self):
        """
        Load experiment metadata from UUID-based files.
        This method scans the data directory for .json metadata files and loads them into memory.
        It assumes the file structure is as follows:

        /{self.data_path}/
        ├── {uuid}/
        │   ├── {uuid}.json           Metadata file for experiment with UUID
        │   ├── {uuid}.csv            Experiment data in CSV format
        │   └── {uuid}.cif            Geometry file for experiment
        ├── {uuid}/
        │   ├── {uuid}.json
        │   ├── {uuid}.csv
        │   └── {uuid}.cif
        └── ...
        """

        utils.log_with_context(
            f"[LOG] Loading UUID-based experiment metadata from: {self.data_path}...",
            log_flag=settings.is_data_manager_logging_enabled(),
        )

        # Find all JSON metadata files recursively in the data directory and subdirectories
        json_files = self.data_path.rglob("*.json")

        for json_file in json_files:
            try:
                # Extract UUID from filename
                experiment_uuid = json_file.stem

                # Verify required files exist
                _, csv_file, cif_file = self._generate_file_paths_for_experiment(experiment_uuid)

                # all files have to be present to load
                if not csv_file.exists() or not cif_file.exists():
                    utils.log_with_context(
                        f"[LOG] Warning: CSV or CIF file missing for UUID {experiment_uuid}",
                        log_flag=settings.is_data_manager_logging_enabled(),
                    )
                    continue

                # load metadata from JSON file
                with open(json_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                # add the metadata to memory
                self._experiments_metadata[experiment_uuid] = metadata

            except Exception as e:
                utils.log_with_context(
                    f"[LOG] Error loading metadata from {json_file}: {e}",
                    log_flag=settings.is_data_manager_logging_enabled(),
                )

        utils.log_with_context(
            f"[LOG] Successfully loaded {len(self._experiments_metadata)} experiments into memory",
            log_flag=settings.is_data_manager_logging_enabled(),
        )

    def _create_experiment_directory(self, experiment_uuid: str) -> Path:
        """
        Create a directory for an experiment.
        """
        experiment_dir = self.data_path / experiment_uuid
        experiment_dir.mkdir(parents=True, exist_ok=True)
        return experiment_dir

    def _generate_file_paths_for_experiment(self, experiment_uuid: str):
        """
        Generate file paths for an experiment.
        Function does not check if the paths exist or not, it just generates the paths.
        """
        # This function can be used to generate file paths for experiments
        # based on UUIDs, if needed in the future.

        metadata_file_path = self.data_path / experiment_uuid / f"{experiment_uuid}.json"
        csv_file_path = self.data_path / experiment_uuid / f"{experiment_uuid}.csv"
        cif_file_path = self.data_path / experiment_uuid / f"{experiment_uuid}.cif"

        return metadata_file_path, csv_file_path, cif_file_path
