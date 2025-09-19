"""
Base Data Manager Module

This module defines the abstract base class for all data manager implementations
in the levseq-dash application. It provides a consistent interface for managing
experiment data across different storage backends (disk, database, etc.).

Classes:
    BaseDataManager: Abstract base class defining the data manager interface

Usage:
    from levseq_dash.app.data_manager.base import BaseDataManager

    class MyDataManager(BaseDataManager):
        # Implement all abstract methods
        def add_experiment_from_ui(self, ...): ...
        def get_experiment(self, ...): ...
        # ... etc
"""

import hashlib
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from levseq_dash.app.data_manager.experiment import Experiment, MutagenesisMethod


class BaseDataManager(ABC):
    """
    Abstract base class for data managers.

    This class defines the interface that all data manager implementations must follow.
    It provides a consistent API for storing, retrieving, and managing experiment data
    regardless of the underlying storage mechanism (file system, database, etc.).

    The data manager is responsible for:
    - Adding new experiments from UI uploads
    - Checking for duplicate experiments
    - Retrieving experiment data and metadata
    - Managing experiment sequences and assay information
    - Deleting experiments when needed

    All concrete implementations must inherit from this class and implement
    all abstract methods.

    Example:
        class DiskDataManager(BaseDataManager):
            def __init__(self):
                super().__init__()
                # Initialize disk-specific components

            def add_experiment_from_ui(self, ...):
                # Implement disk-based storage
                pass
    """

    def __init__(self):
        """
        Initialize the data manager.

        Subclasses should call super().__init__() and then initialize
        their specific storage mechanisms and configurations.
        """
        pass

    # =============================================================================
    #                           ABSTRACT METHODS - DATA CREATION
    # =============================================================================

    @abstractmethod
    def add_experiment_from_ui(
        self,
        experiment_name: str,
        experiment_date: str,
        substrate: str,
        product: str,
        assay: str,
        mutagenesis_method: MutagenesisMethod,
        geometry_content_base64_encoded_string: str,
        experiment_content_base64_encoded_string: str,
    ) -> str:
        """
        Add a new experiment from UI input.

        This method processes experiment data uploaded through the web interface,
        validates the input, and stores the experiment in the underlying storage system.

        The method should:
        1. Generate a unique experiment UUID
        2. Decode and validate the uploaded CSV and structure files
        3. Calculate checksums for duplicate detection
        4. Store all experiment files and metadata
        5. Update any internal caches or indexes

        Args:
            experiment_name (str): Human-readable name for the experiment
            experiment_date (str): Date when the experiment was conducted (ISO format)
            substrate (str): Chemical substrate used in the experiment
            product (str): Expected chemical product
            assay (str): Type of assay performed (must be from available assays)
            mutagenesis_method (MutagenesisMethod): Method used for mutagenesis
            geometry_content_base64_encoded_string (str): Base64-encoded CIF/structure file
            experiment_content_base64_encoded_string (str): Base64-encoded CSV data file

        Returns:
            str: Success message containing experiment name and generated ID,
                 or error message if upload failed

        Raises:
            ValueError: If required parameters are missing or invalid
            IOError: If file operations fail
            DuplicateExperimentError: If experiment with same checksum exists
        """
        pass

    @abstractmethod
    def check_for_duplicate_experiment(self, new_csv_checksum: str) -> bool:
        """
        Check if an experiment with the given CSV checksum already exists.

        Args:
            new_csv_checksum (str): Checksum of the CSV data to check for duplicates

        Returns:
            bool: True if an experiment with this checksum already exists,
                  False if the experiment is unique

        Note:
            The checksum comparison should be case-insensitive and use the same
            hashing algorithm across all implementations.
        """
        pass

    @abstractmethod
    def delete_experiment(self, experiment_uuid: str) -> bool:
        """
        Delete an experiment by UUID.

        This method permanently removes an experiment and all associated data
        from the storage system. This includes:
        - Experiment metadata
        - CSV data files
        - Structure/geometry files
        - Any cached data
        - Index entries

        Args:
            experiment_uuid (str): The unique identifier of the experiment to delete

        Returns:
            bool: True if deletion was successful, False if the experiment
                  was not found or deletion failed

        Warning:
            This operation is irreversible. Ensure proper confirmation
            before calling this method.

        Note:
            Implementations should handle partial deletion failures gracefully
            and log appropriate error messages.
        """
        pass

    # =============================================================================
    #                           ABSTRACT METHODS - DATA RETRIEVAL
    # =============================================================================

    @abstractmethod
    def get_all_lab_experiments_with_meta_data(self) -> List[Dict[str, Any]]:
        """
        Get all lab experiments with their metadata.

        Retrieves a comprehensive list of all experiments stored in the system,
        including their metadata but not the full experimental data. This method
        is typically used for displaying experiment lists in the UI.

        The returned metadata should include:
        - experiment_id: Human-readable experiment identifier
        - experiment_uuid: Unique system identifier
        - experiment_name: User-provided name
        - experiment_date: Date of experiment
        - substrate: Chemical substrate
        - product: Chemical product
        - assay: Assay type
        - mutagenesis_method: Method used
        - upload_timestamp: When experiment was added to system

        Returns:
            List[Dict[str, Any]]: List of experiment metadata dictionaries.
                                 Empty list if no experiments exist.
        """
        pass

    @abstractmethod
    def get_all_lab_sequences(self) -> Dict[str, str]:
        """
        Get all lab sequences as a dictionary.

        Retrieves the primary sequence data for all experiments. This is used
        for sequence alignment and comparison operations across experiments.

        Returns:
            Dict[str, str]: Dictionary mapping experiment UUIDs to their
                           primary sequence strings. Empty dict if no sequences.

        Note:
            Only experiments with valid sequence data should be included.
            Invalid or corrupted sequences should be logged and skipped.
        """
        pass

    @abstractmethod
    def get_experiment_metadata(self, experiment_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific experiment.

        Retrieves the metadata for a single experiment without loading the
        full experimental data. This is useful for quick lookups and validations.

        Args:
            experiment_uuid (str): The unique identifier of the experiment

        Returns:
            Optional[Dict[str, Any]]: Experiment metadata dictionary if found,
                                     None if experiment doesn't exist

        Example:
            metadata = manager.get_experiment_metadata("123e4567-e89b-12d3...")
            if metadata:
                print(f"Experiment: {metadata['experiment_name']}")
        """
        pass

    @abstractmethod
    def get_experiment(self, experiment_uuid: str) -> Optional[Experiment]:
        """
        Get a complete experiment object by UUID.

        Retrieves the full experiment data including metadata, CSV data,
        structure files, and any derived data. This method may be expensive
        as it loads all experiment data into memory.

        Args:
            experiment_uuid (str): The unique identifier of the experiment

        Returns:
            Optional[Experiment]: Complete experiment object if found,
                                 None if experiment doesn't exist or can't be loaded

        Note:
            Implementations should consider caching frequently accessed
            experiments to improve performance. Handle file I/O errors
            gracefully and return None if data is corrupted.

        Example:
            exp = manager.get_experiment("123e4567-e89b-12d3...")
            if exp:
                df = exp.data_df  # Access the pandas DataFrame
                sequence = exp.sequence  # Access the sequence
        """
        pass

    @abstractmethod
    def get_experiment_file_content(self, experiment_uuid: str) -> Dict[str, bytes]:
        """
        Get experiment files content as bytes for a specific experiment.

        Args:
            experiment_uuid (str): The unique identifier of the experiment

        Returns:
            Dict[str, bytes]: A dictionary with file types ('json', 'csv', 'cif') as keys
                              and file content as bytes as values. Returns an empty dictionary if files are not found.
        """
        pass

    @abstractmethod
    def get_assays(self) -> List[str]:
        """
        Get list of available assays.

        Returns the list of assay types that can be used when creating new
        experiments. This list defines the valid assay options for the UI.

        Returns:
            List[str]: List of available assay names. Empty list if none configured.

        Example:
            assays = manager.get_assays()
            # Returns: ["FACS", "Growth", "Spectrophotometry", ...]
        """
        pass

    @abstractmethod
    def get_experiments_zipped(self, experiments_to_zip: List[Dict[str, Any]]) -> Optional[bytes]:
        """
        Create a ZIP archive containing experiment data and metadata.

        Takes a list of experiment metadata dictionaries and creates a ZIP file
        containing all experiment files (JSON metadata, CSV data, CIF structure files)
        organized in a structured format along with a summary CSV file.

        Args:
            experiments_to_zip (List[Dict[str, Any]]): List of experiment metadata
                                                           dictionaries to include in the ZIP

        Returns:
            Optional[bytes]: ZIP file data as bytes if successful, None if no experiments
                           provided or if creation fails

        Note:
            The ZIP structure should be:
            - EnzEngDB_Experiments_{timestamp}.csv (summary metadata file)
            - experiments/{experiment_id}/{experiment_id}.json
            - experiments/{experiment_id}/{experiment_id}.csv
            - experiments/{experiment_id}/{experiment_id}.cif
        """
        pass

    # =============================================================================
    #                              UTILITY METHODS
    # =============================================================================
    # These methods provide common functionality that can be shared across
    # all data manager implementations. They can be overridden if needed.

    @staticmethod
    def generate_experiment_id(id_prefix: str) -> str:
        """
        Generate a unique experiment ID.

        Creates a human-readable experiment identifier by combining a prefix
        with a UUID. This ID is used for display purposes and should be unique
        across the entire system.

        Args:
            id_prefix (str): Prefix for the experiment ID (e.g., "ARNLD", "EXPT")
                           Should be short (5 characters) and alphanumeric

        Returns:
            str: Generated experiment ID in format "{prefix}-{uuid}"

        Example:
            exp_id = BaseDataManager.generate_experiment_id("ARNLD")
            # Returns: "ARNLD-123e4567-e89b-12d3-a456-426614174000"

        Note:
            This method uses UUID4 for randomness. The generated ID is
            guaranteed to be unique but may be long for display purposes.
        """
        generated_uuid = str(uuid.uuid4())
        # Return a string with the prefix and UUID
        return f"{id_prefix}-{generated_uuid}"

    @staticmethod
    def calculate_file_checksum(file_bytes) -> str:
        """Calculate SHA256 checksum of a file."""

        if file_bytes is None:
            raise ValueError("file_bytes cannot be None")

        if not isinstance(file_bytes, bytes):
            raise TypeError("file_bytes must be of type bytes")

        if len(file_bytes) == 0:
            raise ValueError("file_bytes cannot be empty")

        sha256 = hashlib.sha256()
        sha256.update(file_bytes)

        return sha256.hexdigest()
