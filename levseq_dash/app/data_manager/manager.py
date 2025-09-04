import base64
import datetime
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from cachetools import LRUCache

from levseq_dash.app import global_strings as gs
from levseq_dash.app.config import settings
from levseq_dash.app.data_manager.experiment import Experiment, MutagenesisMethod
from levseq_dash.app.utils import utils


class DataManager:
    def __init__(self):
        """Initialize the database"""
        self.use_db_web_service = settings.get_storage_mode()
        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")

        elif self.use_db_web_service == "disk":
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
        experiment_content_base64_string,
        geometry_content_base64_string,
    ) -> str:
        """
        Returns
        -------
        A UUID string is generated and returned for future reference.
        """
        experiment_uuid = None
        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")

        elif self.use_db_web_service == "disk":
            if experiment_content_base64_string:
                # Duplicate data check has already passed in upload by check_for_duplicate_experiment
                # Sanity check has already passed in upload by run_sanity_checks_on_experiment_file

                # Generate a UUID for the experiment
                experiment_uuid = self.generate_experiment_id(id_prefix=self.five_letter_id_prefix)

                # assign a timestamp for the upload
                upload_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # convert to dataframe for processing
                df, experiment_bytes = utils.decode_csv_file_base64_string_to_dataframe(
                    experiment_content_base64_string
                )

                # calculate a checksum for the CSV file
                csv_checksum = utils.calculate_file_checksum(experiment_bytes)

                # calculate the number of plates in the experiment
                plates_count = len(Experiment.extract_plates_list(df))

                # extract parent sequence from the CSV - sanity check already checks that such a row exists
                parent_sequence = Experiment.extract_parent_sequence(df)

                metadata = {
                    "experiment_id": experiment_uuid,
                    "experiment_name": experiment_name,
                    "experiment_date": experiment_date,
                    "substrate": substrate,
                    "product": product,
                    "assay": assay,
                    "mutagenesis_method": mutagenesis_method,
                    "parent_sequence": parent_sequence,
                    "plates_count": plates_count,
                    "csv_checksum": csv_checksum,
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
                    # decode to text (assuming it's ASCII)
                    decoded_text = base64.b64decode(geometry_content_base64_string).decode("utf-8")
                    with open(cif_file_path, "w", encoding="utf-8") as f:
                        f.write(decoded_text)

                # add the newly added experiment to the metadata list
                self._experiments_metadata[experiment_uuid] = metadata

        else:
            raise Exception(gs.error_data_mode)

        return experiment_uuid

    def check_for_duplicate_experiment(self, new_csv_checksum: str):
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
            Delete the experiment associated with this UUID

        Returns
        -------
            bool True if deleted successfully

        """
        success = False
        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")
        elif self.use_db_web_service == "disk":
            if experiment_uuid in self._experiments_metadata:
                # Delete files from disk
                json_file, csv_file_path, cif_file_path = self._generate_file_paths_for_experiment(experiment_uuid)

                for file_path in [json_file, csv_file_path, cif_file_path]:
                    if file_path.exists():
                        file_path.unlink()

                # Remove from memory
                del self._experiments_metadata[experiment_uuid]

                # Remove from cache if it exists
                if experiment_uuid in self._experiments_core_data_cache:
                    del self._experiments_core_data_cache[experiment_uuid]

                success = True
        else:
            raise Exception(gs.error_data_mode)

        return success

    # ---------------------------
    #    DATA RETRIEVAL: ALL
    # ---------------------------
    def get_all_lab_experiments_with_meta_data(self):
        """
        Returns
        -------
        | experiment_uuid | experiment_name | upload_time_stamp | experiment_date |
        substrate | product | assay | mutagenesis_method | sequence | csv_checksum
        """
        data_list_of_dict = []
        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")
        elif self.use_db_web_service == "disk":
            # get the metadata for all the experiments
            data_list_of_dict = list(self._experiments_metadata.values())
        else:
            raise Exception(gs.error_data_mode)
        return data_list_of_dict

    def get_all_lab_sequences(self):
        """
        Returns
        -------
        | experiment_uuid | parent_sequence
        """
        seq_data = {}
        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")
        elif self.use_db_web_service == "disk":
            # dictionary of "experiment UUID" and "experiment sequence" pairs
            # the key of the dictionary is the experiment UUID
            for experiment_uuid, metadata in self._experiments_metadata.items():
                seq_data.update({experiment_uuid: metadata.get("parent_sequence", "")})
        else:
            raise Exception(gs.error_data_mode)
        return seq_data

    # ---------------------------
    #    DATA RETRIEVAL: PER EXPERIMENT
    # ---------------------------
    def get_experiment_metadata(self, experiment_uuid: str) -> dict | None:
        """
        Returns metadata for the given experiment UUID.
        """
        return self._experiments_metadata.get(experiment_uuid, None)

    def get_experiment(self, experiment_uuid: str) -> Experiment | None:
        """
        returns Experiment object for the given experiment UUID
        which contains the structure and the experiment data.
        """
        exp = None
        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")
        elif self.use_db_web_service == "disk":
            try:
                # Check cache first
                if experiment_uuid in self._experiments_core_data_cache:
                    return self._experiments_core_data_cache[experiment_uuid]

                # Load from disk
                _, csv_file_path, cif_file_path = self._generate_file_paths_for_experiment(experiment_uuid)
                exp = Experiment(experiment_data_file_path=csv_file_path, geometry_file_path=cif_file_path)
                # Cache the loaded experiment
                if exp:
                    self._experiments_core_data_cache[experiment_uuid] = exp

            except Exception as e:
                raise Exception(f"[LOG] Error loading experiment {experiment_uuid} from disk: {e}")
        else:
            raise Exception(gs.error_data_mode)
        return exp

    # ---------------------------
    #    DATA RETRIEVAL: MISC
    # ---------------------------
    def get_assays(self):
        """
        Returns list of assays
        -------
        | assay |
        """
        assay_list = []
        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")

        elif self.use_db_web_service == "disk":
            assay_list = self.assay_list
        else:
            raise Exception(gs.error_data_mode)
        return assay_list

    # ----------------------------
    #    PRIVATE METHODS
    # ---------------------------
    def _setup_data_path(self):
        """ """

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

        /self.data_path/
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

        if self.use_db_web_service == "db":
            raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")

        utils.log_with_context(
            f"[LOG] Loading UUID-based experiment metadata from: {self.data_path}...",
            log_flag=settings.is_data_manager_logging_enabled(),
        )

        # Find all JSON metadata files recursively in the data directory and subdirectories
        json_files = list(self.data_path.rglob("*.json"))

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
        Create a directory for the experiment based on its UUID.
        This is used to store experiment files like JSON, CSV, and CIF.
        """
        experiment_dir = self.data_path / experiment_uuid
        experiment_dir.mkdir(parents=True, exist_ok=True)
        return experiment_dir

    def _generate_file_paths_for_experiment(self, experiment_uuid: str):
        """
        Generate file paths for experiments based on UUIDs.
        Function does not check if the paths exist or not, it just generates the paths.
        """
        # This function can be used to generate file paths for experiments
        # based on UUIDs, if needed in the future.

        metadata_file_path = self.data_path / experiment_uuid / f"{experiment_uuid}.json"
        csv_file_path = self.data_path / experiment_uuid / f"{experiment_uuid}.csv"
        cif_file_path = self.data_path / experiment_uuid / f"{experiment_uuid}.cif"

        return metadata_file_path, csv_file_path, cif_file_path

    @staticmethod
    def generate_experiment_id(id_prefix: str) -> str:
        # Generate a UUID for the experiment
        generated_uuid = str(uuid.uuid4())
        # Return a string with the prefix and UUID
        return f"{id_prefix}-{generated_uuid}"


# Python will only run module-level code once per process, no matter how often Dash reloads pages or triggers callbacks
# this will ensure Dash doesn't recreate the instance every time the page reloads or a callback is triggered
singleton_data_mgr_instance = DataManager()
