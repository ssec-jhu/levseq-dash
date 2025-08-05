import base64
import datetime
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

from levseq_dash.app import global_strings as gs
from levseq_dash.app.config import settings
from levseq_dash.app.config.settings import AppMode
from levseq_dash.app.data_manager.experiment import Experiment, MutagenesisMethod
from levseq_dash.app.utils import utils
from levseq_dash.app.utils.utils import log_with_context


# from levseq_dash.app.wsexec import Query


class DataManager:
    def __init__(self):
        """Initialize the database"""
        if settings.is_db_mode():
            self.use_db_web_service = AppMode.db.value
            # TODO: database connection happens on instance load
            # ideally defined in the config file
            # connect_to_db( host, port, username, password)
        elif settings.is_disk_mode():
            self.use_db_web_service = AppMode.disk.value
            log_with_context(f"---------DISK MODE ---------------", log_flag=settings.is_data_manager_logging_enabled())

            # Store experiment metadata index (UUID -> metadata dict)
            self.experiments_metadata = {}
            # Cache for loaded experiment objects (UUID -> Experiment object)
            # self.experiments_cache = {}

            # look for DATA_PATH in case data is mounted from elsewhere
            env_data_path = os.getenv("DATA_PATH")
            log_with_context(f"[LOG] os.getenv: {env_data_path}", log_flag=settings.is_data_manager_logging_enabled())

            if env_data_path is None:
                # if no path is provided, read from the path in config file
                disk_settings = settings.get_disk_settings()
                raw_path = disk_settings.get("data_path")
                self.data_path = (settings.package_root / raw_path).resolve() if raw_path else None
                log_with_context(
                    f"[LOG] Using config file data_path: {self.data_path}",
                    log_flag=settings.is_data_manager_logging_enabled(),
                )
            else:
                self.data_path = Path(env_data_path).resolve()
                log_with_context(
                    f"[LOG] Using env DATA_PATH for data path: {self.data_path}",
                    log_flag=settings.is_data_manager_logging_enabled(),
                )

            if not self.data_path or not self.data_path.exists():
                log_with_context(
                    f"[LOG] Data path not found: {self.data_path}", log_flag=settings.is_data_manager_logging_enabled()
                )
                raise FileNotFoundError()

            # read the assay file and set up the assay list
            if settings.assay_file_path.exists():
                assays = pd.read_csv(settings.assay_file_path, encoding="utf-8", usecols=["Technique"])
                self.assay_list = assays["Technique"].tolist()
                log_with_context(
                    f"[LOG] Read assay file at: {settings.assay_file_path} with size {len(self.assay_list)}",
                    log_flag=settings.is_data_manager_logging_enabled(),
                )

            # Load experiment metadata index from UUID-based files
            self._load_all_experiments_metadata_into_memory()
            # self._export_experiment_data_with_uuid(data_directory=self.data_path, output_directory=self.data_path)

        else:
            raise Exception(gs.error_app_mode)

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
        if self.use_db_web_service == AppMode.db.value:
            pass

        elif self.use_db_web_service == AppMode.disk.value:
            # Generate UUID for the experiment
            experiment_uuid = str(uuid.uuid4())

            if experiment_content_base64_string:
                # calculate a checksum for the CSV file
                experiment_bytes = base64.b64decode(experiment_content_base64_string)
                csv_checksum = utils.calculate_file_checksum(experiment_bytes)
                upload_time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # convert to dataframe for processing
                df = utils.decode_csv_file_base64_string_to_dataframe(experiment_content_base64_string)

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
                self.experiments_metadata[experiment_uuid] = metadata

        else:
            raise Exception(gs.error_app_mode)

        return experiment_uuid

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
        if self.use_db_web_service == AppMode.db.value:
            pass
        elif self.use_db_web_service == AppMode.disk.value:
            if experiment_uuid in self.experiments_metadata:
                # Delete files from disk
                json_file, csv_file_path, cif_file_path = self._generate_file_paths_for_experiment(experiment_uuid)

                for file_path in [json_file, csv_file_path, cif_file_path]:
                    if file_path.exists():
                        file_path.unlink()

                # Remove from memory
                del self.experiments_metadata[experiment_uuid]

                # # Remove from cache if it exists
                # if experiment_uuid in self.experiments_cache:
                #     del self.experiments_cache[experiment_uuid]

                success = True
        else:
            raise Exception(gs.error_app_mode)

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
        if self.use_db_web_service == AppMode.db.value:
            # TODO:
            #  get all lab experiments ids + get metadata from each experiment
            #  OR: this can be bundled into 1 function
            #  put data together
            pass
        elif self.use_db_web_service == AppMode.disk.value:
            # get the metadata for all the experiments
            data_list_of_dict = list(self.experiments_metadata.values())
        else:
            raise Exception(gs.error_app_mode)
        return data_list_of_dict

    def get_all_lab_sequences(self):
        """
        Returns
        -------
        | experiment_uuid | parent_sequence
        """
        seq_data = {}
        if self.use_db_web_service == AppMode.db.value:
            # TODO:
            # get all lab sequences
            pass
        elif self.use_db_web_service == AppMode.disk.value:
            # dictionary of "experiment UUID" and "experiment sequence" pairs
            # the key of the dictionary is the experiment UUID
            for experiment_uuid, metadata in self.experiments_metadata.items():
                seq_data.update({experiment_uuid: metadata.get("parent_sequence", "")})
        else:
            raise Exception(gs.error_app_mode)
        return seq_data

    # ---------------------------
    #    DATA RETRIEVAL: PER EXPERIMENT
    # ---------------------------
    def get_experiment(self, experiment_uuid: str) -> Experiment | None:
        """
        Lazy load experiment from disk if not in cache
        """
        exp = None
        if self.use_db_web_service == AppMode.db.value:
            # TODO:
            #  get_experiment_meta_data
            #  get_experiment_core_data
            #  get_experiment_parent_sequence
            #  get_experiment_geometry_file
            #  return Experiment
            pass
        elif self.use_db_web_service == AppMode.disk.value:
            try:
                # Check cache first
                # if experiment_uuid in self.experiments_cache:
                #     return self.experiments_cache[experiment_uuid]

                # Load from disk
                # exp = self._load_experiment_from_disk(experiment_uuid)
                _, csv_file_path, cif_file_path = self._generate_file_paths_for_experiment(experiment_uuid)
                exp = Experiment(experiment_data_file_path=csv_file_path, geometry_file_path=cif_file_path)

                # if exp:
                #     # Cache the loaded experiment
                #     self.experiments_cache[experiment_uuid] = exp

            except Exception as e:
                raise Exception(f"[LOG] Error loading experiment {experiment_uuid} from disk: {e}")
        else:
            raise Exception(gs.error_app_mode)
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
        if self.use_db_web_service == AppMode.db.value:
            # this works
            # cols, rows = Query("get_assays", [])
            # assay_list = [sublist[1] for sublist in rows]
            pass

            # df = pd.DataFrame(rows)
            # # cols, rows = Query("get_test_queries", [eid, uid, gid])  # type:ignore
            # cols, rows = Query("get_usernames", [])  # type:ignore
            # df_user = pd.DataFrame(data=rows, columns=cols)  # type:ignore
            # cols, rows = Query("get_mutagenesis_methods", [])  # type:ignore
            # cols_1, rows_1 = Query("get_experiments_u", [4])  # type:ignore
            # df = pd.DataFrame(rows_1)
            # eid = 102
            # gid = 2
            # cols, rows = Query("get_test_queries", [eid, 4, gid])  # type:ignore
            # # cols, rows = Query("get_user_info", [uid])  # type:ignore
            #
            # cols, rows = Query("get_variant_sequences", [1, gid])  # type:ignore
        elif self.use_db_web_service == AppMode.disk.value:
            assay_list = self.assay_list
        else:
            raise Exception(gs.error_app_mode)
        return assay_list

    def _load_all_experiments_metadata_into_memory(self):
        """
        Load experiment metadata from UUID-based files.
        This method scans the data directory for .json metadata files and loads them into memory.
        It assumes the file structure is as follows:

        /self.data_path/
        ├── {uuid}.json           Metadata file for experiment with UUID
        ├── {uuid}.csv            Experiment data in CSV format
        └── {uuid}.cif            Geometry file for experiment
        """

        if self.use_db_web_service == AppMode.db.value:
            raise Exception(gs.error_wrong_mode)

        log_with_context(
            f"[LOG] Loading UUID-based experiment metadata from: {self.data_path}...",
            log_flag=settings.is_data_manager_logging_enabled(),
        )

        # Find all JSON metadata files in the data directory
        json_files = list(self.data_path.glob("*.json"))

        for json_file in json_files:
            try:
                # Extract UUID from filename
                experiment_uuid = json_file.stem

                # Verify required files exist
                _, csv_file, cif_file = self._generate_file_paths_for_experiment(experiment_uuid)

                # all files have to be present to load
                if not csv_file.exists() or not cif_file.exists():
                    log_with_context(
                        f"[LOG] Warning: CSV or CIF file missing for UUID {experiment_uuid}",
                        log_flag=settings.is_data_manager_logging_enabled(),
                    )
                    continue

                # load metadata from JSON file
                with open(json_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                # add the metadata to memory
                self.experiments_metadata[experiment_uuid] = metadata

            except Exception as e:
                log_with_context(
                    f"[LOG] Error loading metadata from {json_file}: {e}",
                    log_flag=settings.is_data_manager_logging_enabled(),
                )

    def _generate_file_paths_for_experiment(self, experiment_uuid):
        """
        Generate file paths for experiments based on UUIDs.
        This function is a placeholder for future implementations.
        """
        # This function can be used to generate file paths for experiments
        # based on UUIDs, if needed in the future.

        metadata_file_path = self.data_path / f"{experiment_uuid}.json"
        csv_file_path = self.data_path / f"{experiment_uuid}.csv"
        cif_file_path = self.data_path / f"{experiment_uuid}.cif"

        return metadata_file_path, csv_file_path, cif_file_path


# Python will only run module-level code once per process, no matter how often Dash reloads pages or triggers callbacks
# this will ensure Dash doesn't recreate the instance every time the page reloads or a callback is triggered
singleton_data_mgr_instance = DataManager()
