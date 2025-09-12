from levseq_dash.app.data_manager.base import BaseDataManager


class DatabaseDataManager(BaseDataManager):
    """
    Database-based implementation of the data manager.

    This implementation stores experiment data in a database.
    Currently not implemented - placeholder for future database integration.
    """

    def __init__(self):
        """Initialize the database-based data manager"""
        super().__init__()
        raise NotImplementedError("Database mode is not yet implemented. Please use disk mode.")
