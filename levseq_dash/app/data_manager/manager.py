"""
Data manager factory and singleton instance.

This module provides a factory function to create the appropriate data manager
implementation based on the storage mode configuration.
"""

from levseq_dash.app.config import settings
from levseq_dash.app.data_manager.base import BaseDataManager


def validate_deployment_configuration():
    """
    Validate that the deployment configuration is consistent and secure.
    """
    # Check for invalid deployment mode configuration
    if settings.is_public_playground_mode():
        # In public-playground mode, data modification MUST be disabled
        if settings.is_data_modification_enabled():
            raise ValueError(
                "CONFIGURATION ERROR: public-playground mode cannot have data modification enabled. "
                "Set 'enable-data-modification: false' in config.yaml for public-playground mode OR use "
                "local-instance mode."
            )

        # In public-playground mode, five-letter-id-prefix should be empty
        if settings.get_five_letter_id_prefix():
            raise ValueError(
                "CONFIGURATION ERROR: public-playground mode should not have five-letter-id-prefix set. "
                "Set 'five-letter-id-prefix: \"\"' in config.yaml for public-playground mode."
            )

        # In public-playground mode, local-data-path should be empty
        if settings.get_disk_settings().get("local-data-path", ""):
            raise ValueError(
                "CONFIGURATION ERROR: public-playground mode should not have local-data-path set. "
                "Set 'local-data-path: \"\"' in config.yaml for public-playground mode."
            )

    elif settings.is_local_instance_mode():
        try:
            # call the getters to trigger validation
            settings.get_data_path()
            if settings.is_data_modification_enabled():
                settings.get_five_letter_id_prefix()
        except ValueError as e:
            raise ValueError(f"CONFIGURATION ERROR: {str(e)}")
    else:
        raise ValueError(
            "CONFIGURATION ERROR: deployment-mode must be either 'public-playground' or 'local-instance'. "
            f"Got: '{settings.get_deployment_mode()}'"
        )


def create_data_manager() -> BaseDataManager:
    """
    Factory function to create the appropriate data manager implementation
    based on the storage mode configuration.

    Returns:
        BaseDataManager: An instance of the appropriate data manager implementation

    Raises:
        NotImplementedError: If the storage mode is not supported
        ValueError: If the storage mode is invalid
    """
    validate_deployment_configuration()
    storage_mode = settings.get_storage_mode()

    if storage_mode == "disk":
        from levseq_dash.app.data_manager.disk_manager import DiskDataManager

        return DiskDataManager()
    # Other modes are not yet implemented
    # You can implement the required data manager class in the future and add it here like this
    # as shown in the "db" example below
    # elif storage_mode == "db":
    # from levseq_dash.app.data_manager.db_manager import DatabaseDataManager
    # return DatabaseDataManager()
    else:
        raise ValueError(
            "CONFIGURATION ERROR: deployment-mode must be either 'public-playground' or 'local-instance'. "
            f"Got: '{settings.get_deployment_mode()}'"
        )


# Python will only run module-level code once per process, no matter how often Dash reloads pages or triggers callbacks
# this will ensure Dash doesn't recreate the instance every time the page reloads or a callback is triggered
singleton_data_mgr_instance = create_data_manager()
