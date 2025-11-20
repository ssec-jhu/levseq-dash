Developer Guide
===============

This guide provides detailed information for developers contributing to or extending LevSeq-Dash.

.. contents:: Table of Contents
   :local:
   :depth: 2

Getting Started
---------------

For initial setup and contribution guidelines, please see the `CONTRIBUTING.md <https://github.com/ssec-jhu/levseq-dash/blob/main/CONTRIBUTING.md>`_ file in the repository root.

Architecture Overview
---------------------

LevSeq-Dash is built using the Dash framework (Plotly) for creating interactive web applications in Python. The application follows a modular architecture with clear separation of concerns.

High-Level Architecture
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ┌─────────────────────────────────────────────────────────┐
    │                     Dash Application                    │
    │                     (main_app.py)                       │
    └─────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ┌────────┐  ┌─────────┐  ┌──────────┐
    │ Layouts│  │Callbacks│  │Components│
    └────┬───┘  └────┬────┘  └─────┬────┘
         │           │              │
         └───────────┴──────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────────┐      ┌──────────────┐
    │Data Manager │      │Seq Aligner   │
    └──────┬──────┘      └──────┬───────┘
           │                    │
           ▼                    ▼
    ┌─────────────┐      ┌──────────────┐
    │ Experiment  │      │  BioPython   │
    │   Model     │      │   Aligner    │
    └─────────────┘      └──────────────┘

Core Modules
~~~~~~~~~~~~

1. **Main Application** (``main_app.py``)
   
   - Entry point for the Dash application
   - Registers all callbacks
   - Initializes data manager and configuration
   - Sets up routing and navigation

2. **Global Strings** (``global_strings.py``)
   
   - Centralized location for UI text, labels, and messages
   - URL path constants for page routing
   - Navigation labels and menu items
   - **Note**: Most string constants in the application are defined here for consistency and easy localization

3. **Data Manager** (``data_manager/``)
   
   - **Abstract Base Class** (``base.py``): Defines interface for data operations
   - **Factory** (``manager.py``): Creates appropriate data manager based on configuration
   - **Disk Manager** (``disk_manager.py``): Local file storage implementation
   - **Experiment Model** (``experiment.py``): Data model for experiment objects
   
   The data manager handles:
   - Experiment CRUD operations
   - Metadata management
   - File I/O operations
   - Caching with LRU cache

4. **Sequence Aligner** (``sequence_aligner/``)
   
   - Wraps BioPython's pairwise alignment functionality
   - Provides BLASTP-style alignment for protein sequences
   - Calculates alignment scores and statistics
   - Formats alignment strings for visualization

5. **Layouts** (``layouts/``)
   
   Each layout module defines a page in the application:
   
   - ``layout_landing.py``: Home page with navigation
   - ``layout_upload.py``: Data upload and validation
   - ``layout_experiment.py``: Single experiment view with variants
   - ``layout_bars.py``: All experiments table
   - ``layout_matching_sequences.py``: Sequence alignment results
   - ``layout_explore.py``: Sequence exploration and filtering
   - ``layout_about.py``: About page and documentation

6. **Components** (``components/``)
   
   Reusable UI components:
   
   - ``widgets.py``: Tables, viewers, form elements, alerts
   - ``graphs.py``: Plotting functions (heatmaps, rank plots, Single-Site Mutagenesis plots)
   - ``vis.py``: Styling constants and cell coloring utilities
   - ``column_definitions.py``: AG Grid column configurations

7. **Utils** (``utils/``)
   
   Helper functions for:
   
   - Protein structure visualization
   - Chemical reaction rendering
   - Sequence alignment formatting
   - General utilities (logging, data processing)

Data Flow
---------

Upload Workflow
~~~~~~~~~~~~~~~

.. code-block:: text

    User Upload
        │
        ├─> Validate CSV format
        │   └─> Check required columns
        │       └─> Validate well format
        │           └─> Verify SMILES strings
        │               └─> Check for duplicates
        │
        ├─> Process Data
        │   └─> Calculate checksums
        │       └─> Extract parent sequence
        │           └─> Generate UUID
        │
        └─> Store Files
            ├─> Save metadata (JSON)
            ├─> Save experiment data (CSV)
            └─> Save geometry (CIF)

Experiment View Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    Select Experiment
        │
        ├─> Load from Cache (if available)
        │   └─> Return cached Experiment object
        │
        └─> Load from Disk
            ├─> Read CSV (core columns only)
            ├─> Read CIF geometry
            ├─> Calculate unique SMILES
            ├─> Extract plates
            └─> Cache Experiment object

Sequence Alignment Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    Input Sequence
        │
        ├─> Get All Lab Sequences
        │   └─> Extract parent from each experiment
        │
        ├─> Setup BLASTP Aligner
        │   └─> Configure scoring matrix
        │       └─> Set gap penalties
        │
        ├─> Perform Alignments
        │   └─> For each target sequence:
        │       ├─> Run pairwise alignment
        │       ├─> Calculate score & statistics
        │       └─> Format alignment string
        │
        └─> Filter & Sort Results
            └─> Return top matches

Configuration System
--------------------

The application uses a YAML-based configuration system located in ``levseq_dash/app/config/``.

Configuration Structure
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    # Deployment mode
    deployment-mode: "local-instance"  # or "public-playground"

    disk:
      enable-data-modification: true
      local-data-path: "/path/to/data"
      five-letter-id-prefix: "MYLAB"

    logging:
      sequence-alignment-profiling: false
      data-manager: false
      pairwise-aligner: false

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Configuration can be overridden using environment variables:

- ``DATA_PATH``: Override data storage path
- ``FIVE_LETTER_ID_PREFIX``: Override experiment ID prefix

Priority (highest to lowest):

1. Environment variables
2. config.yaml settings
3. Default values

Adding New Features
-------------------

Adding a New Page
~~~~~~~~~~~~~~~~~

1. **Create layout** in ``layouts/layout_my_page.py``:

   .. code-block:: python

       import dash_bootstrap_components as dbc
       from dash import html
       
       def get_layout() -> dbc.Container:
           """Create the page layout."""
           return dbc.Container([
               dbc.Row([
                   dbc.Col([
                       html.H1("Page Title"),
                       # Your page content
                   ])
               ])
           ])

2. **Define the path** in ``global_strings.py``:

   .. code-block:: python

       # Add navigation label
       nav_my_page = "My Page"
       
       # Add URL path (at the end of the file with other paths)
       nav_my_page_path = "/my-page"

3. **Register page route** in ``main_app.py``:

   .. code-block:: python

       # Import the layout module at the top
       from levseq_dash.app.layouts import layout_my_page
       
       # Add route in the route_page callback (around line 109)
       @app.callback(Output("id-page-content", "children"), Input("url", "pathname"))
       def route_page(pathname):
           if pathname == "/":
               return layout_landing.get_layout()
           # ... existing routes ...
           elif pathname == gs.nav_my_page_path:
               return layout_my_page.get_layout()
           else:
               return html.Div([html.H2("Page not found!")])

4. **Add navigation link** in ``layouts/layout_bars.py`` sidebar or navbar

5. **Add callbacks** in ``main_app.py`` (not in the layout file):

   .. code-block:: python

       @app.callback(
           Output("my-output", "children"),
           Input("my-button", "n_clicks"),
           State("my-input", "value"),
           prevent_initial_call=True,
       )
       def handle_my_page_interaction(n_clicks, input_value):
           """Handle user interaction on my page."""
           if not n_clicks:
               return dash.no_update
           # Process and return result
           return f"Processed: {input_value}"

**Important Notes:**

- Layout files only define the UI structure via ``get_layout()`` function
- All callbacks must be registered in ``main_app.py`` (not in layout files)
- Page routing is handled by the ``route_page`` callback in ``main_app.py``
- Path constants are defined in ``global_strings.py`` for consistency

Adding a New Callback
~~~~~~~~~~~~~~~~~~~~~

Callbacks should be added in the relevant layout module:

.. code-block:: python

    from dash import callback, Input, Output
    
    @callback(
        Output("output-id", "property"),
        Input("input-id", "property"),
        prevent_initial_call=True,
    )
    def my_callback(input_value):
        """
        Callback description.
        
        Args:
            input_value: Description.
            
        Returns:
            Output value description.
        """
        # Process input
        result = process_data(input_value)
        return result

Best Practices:

- Use descriptive callback names
- Add docstrings
- Use ``prevent_initial_call=True`` when appropriate
- Handle errors gracefully
- Log important operations

Adding a New Widget
~~~~~~~~~~~~~~~~~~~

Add reusable components to ``components/widgets.py``:

.. code-block:: python

    def get_my_widget(widget_id, **kwargs):
        """
        Create a custom widget.
        
        Args:
            widget_id: Unique ID for the widget.
            **kwargs: Additional properties.
            
        Returns:
            Component with configured properties.
        """
        return dbc.Component(
            id=widget_id,
            # Add properties
        )

Adding a New Graph Type
~~~~~~~~~~~~~~~~~~~~~~~

Add plotting functions to ``components/graphs.py``:

.. code-block:: python

    def create_my_plot(df, x_col, y_col):
        """
        Create a custom plot visualization.
        
        Args:
            df: DataFrame containing data.
            x_col: Column name for X-axis.
            y_col: Column name for Y-axis.
            
        Returns:
            go.Figure: Plotly figure object.
        """
        fig = px.scatter(df, x=x_col, y=y_col)
        fig.update_layout(
            # Customize appearance
        )
        return fig

Extending Data Manager
~~~~~~~~~~~~~~~~~~~~~~

The data manager uses an abstract base class pattern with a factory for creating instances:

.. code-block:: text

    ┌─────────────────────────────────────────────────────┐
    │              main_app.py                            │
    │                                                     │
    │  singleton_data_mgr_instance = create_data_manager()│
    └──────────────────┬──────────────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────────┐
    │           manager.py (Factory)                          │
    │                                                         │
    │  def create_data_manager():                             │
    │      if is_disk_mode():                                 │
    │          return DiskDataManager()                       │
    │      elif is_database_mode():                           │
    │          return DatabaseDataManager() ← Extend backends │
    │      elif is_s3_mode():                                 │
    │          return S3DataManager()       ← Extend backends │
    └──────────────────┬──────────────────────────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────────────────────┐
    │         BaseDataManager (Abstract)                   │
    │  - get_experiment()                                  │
    │  - add_experiment_from_ui()                          │
    │  - get_all_lab_experiments_with_meta_data()          │
    │  - delete_experiment()                               │
    │  - ... other abstract methods                        │
    └──────────────────┬───────────────────────────────────┘
                       │
           ┌───────────┴───────────┬────────────┐
           │                       │            │
           ▼                       ▼            ▼
    ┌────────────────┐    ┌──────────────┐  ┌──────────────┐
    │DiskDataManager │    │DatabaseData  │  │S3DataManager │
    │                │    │Manager       │  │              │
    │(Current Model) │    │(New)         │  │(New)         │
    └────────────────┘    └──────────────┘  └──────────────┘

To add new functionality to all backends:

1. **Add method to base class** (``data_manager/base.py``):

   .. code-block:: python

       class DataManager(ABC):
           @abstractmethod
           def my_new_method(self, param: str) -> dict[str, Any]:
               """
               New data operation.
               
               Args:
                   param: Description.
                   
               Returns:
                   Result dictionary.
               """
               pass

2. **Implement in disk manager** (``data_manager/disk_manager.py``):

   .. code-block:: python

       class DiskDataManager(DataManager):
           def my_new_method(self, param: str) -> dict[str, Any]:
               """Implement the new method."""
               # Access self._data_path for file operations
               file_path = self._data_path / f"{param}.json"
               # Read/write operations
               return result

3. **Implement in other backends** as needed (e.g., database, S3)

To add a new storage backend (e.g., S3 or database):

1. Create a new manager class inheriting from ``BaseDataManager``
2. Implement all abstract methods for your backend
3. Update the factory in ``manager.py`` to return your new manager
4. Add configuration options to ``config.yaml``

Adding New CSV Data Columns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Location**: CSV files uploaded via the UI, loaded by ``Experiment`` class in ``levseq_dash/app/data_manager/experiment.py``

When you add new columns to your experimental CSV data, the ``Experiment`` class reads the entire CSV using ``pd.read_csv()``, so new columns are **automatically included** in ``self.data_df`` without code changes.

**Do you need to modify upload/download?**

- **Upload**: No changes needed. The data manager saves the entire CSV as-is.
- **Download**: No changes needed. The data manager exports the entire ``data_df`` DataFrame.

**When you DO need to make changes:**

1. **If new columns need special validation** during upload:
   
   - Add validation in ``data_manager/disk_manager.py`` → ``add_experiment_from_ui()``
   - Example: Check for required columns, validate data types

2. **If new columns should appear in the UI** (tables, graphs):
   
   - Update column definitions in ``column_definitions.py``
   - Add to visualizations in ``graphs.py`` or layout files

3. **If new columns need transformation** during load/save:
   
   - Modify ``Experiment.__init__()`` to process the new columns
   - Update serialization methods if storing derived data

Testing
-------

Test Organization
~~~~~~~~~~~~~~~~~

Tests are organized by functionality:

.. code-block:: text

    levseq_dash/app/tests/                     # Application tests
    ├── conftest.py                            # Shared fixtures and configuration
    ├── test_callbacks.py                      # Dash callback tests (routing, interactions)
    ├── test_dbmanager.py                      # Data manager operations (CRUD)
    ├── test_experiment.py                     # Experiment model and validation
    ├── test_components.py                     # UI widgets and tables
    ├── test_graphs.py                         # Plotting (heatmaps, rank plots, Single-Site Mutagenesis)
    ├── test_settings.py                       # Configuration and settings
    ├── test_alignment.py                      # Sequence alignment integration
    ├── test_utils.py                          # Utility functions
    └── test_data/                             # Test fixtures and sample data

    levseq_dash/app/sequence_aligner/tests/    # Sequence alignment tests
    ├── test_pairwise_aligner.py               # Alignment algorithm logic
    └── test_alignment_time.py                 # Performance benchmarks

Shared Test Fixtures (conftest.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``conftest.py`` file provides reusable fixtures for all tests:

**Path Fixtures**:

- ``test_data_path``, ``app_data_path``: Common directory paths for test and app data
- ``path_exp_ep_data``, ``path_exp_ssm_data``: Paths to sample experiment files (CSV, CIF, JSON)

**Data Fixtures**:

- ``experiment_ep_pcr_metadata``, ``experiment_ssm_metadata``: Pre-loaded experiment metadata from JSON

**Mock Configuration Fixtures**:

- ``mock_load_config_from_test_data_path``: Mock config pointing to test data directory
- ``mock_get_deployment_mode``, ``mock_is_data_modification_enabled``: Mock settings functions

**Data Manager Fixtures**:

- ``disk_manager_from_app_data``: DiskDataManager using app data (for read-only tests)
- ``disk_manager_from_temp_data``: DiskDataManager using temporary directory (for write tests)

These fixtures avoid code duplication and ensure consistent test environments.

Writing Tests
~~~~~~~~~~~~~

Unit Tests
^^^^^^^^^^

Test individual functions in isolation:

.. code-block:: python

    import pytest
    from levseq_dash.app.utils import utils
    
    def test_my_function():
        """Test my_function with valid input."""
        # Arrange
        input_data = {"key": "value"}
        
        # Act
        result = utils.my_function(input_data)
        
        # Assert
        assert result["key"] == "processed_value"

Integration Tests
^^^^^^^^^^^^^^^^^

Test interactions between components:

.. code-block:: python

    def test_data_manager_experiment_lifecycle():
        """Test complete experiment lifecycle."""
        manager = create_data_manager()
        
        # Add experiment
        uuid = manager.add_experiment_from_ui(...)
        
        # Retrieve experiment
        exp = manager.get_experiment(uuid)
        assert exp is not None
        
        # Delete experiment
        deleted = manager.delete_experiment(uuid)
        assert deleted is True

Fixtures
^^^^^^^^

Use pytest fixtures for reusable test data. Prefer using shared fixtures from ``conftest.py`` when available:

.. code-block:: python

    def test_with_shared_fixture(disk_manager_from_temp_data):
        """Test using shared fixture from conftest.py."""
        # disk_manager_from_temp_data is provided by conftest.py
        manager = disk_manager_from_temp_data
        
        # Add and test experiment
        uuid = manager.add_experiment_from_ui(...)
        exp = manager.get_experiment(uuid)
        assert exp is not None

Create custom fixtures in test files for specific needs:

.. code-block:: python

    @pytest.fixture
    def sample_dataframe():
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            "smiles": ["CCO", "CC(O)C"],
            "fitness_value": [1.5, 2.0],
        })
    
    def test_with_custom_fixture(sample_dataframe):
        """Test using custom fixture data."""
        result = process_data(sample_dataframe)
        assert len(result) == 2

**Best Practices**:

- Use fixtures from ``conftest.py`` for common test data and mocks
- Create custom fixtures in test files for specific test needs
- Use ``tmp_path`` fixture for tests that modify files
- Mock configuration to isolate tests from system settings

Debugging
---------

Logging
~~~~~~~

Enable logging in ``config.yaml`` for debugging:

.. code-block:: yaml

    logging:
      sequence-alignment-profiling: true  # Alignment timing
      data-manager: true                   # Data operations
      pairwise-aligner: true              # Alignment details

Use logging in your code:

.. code-block:: python

    from levseq_dash.app.utils import utils
    from levseq_dash.app.config import settings
    
    utils.log_with_context(
        "Debug message",
        log_flag=settings.is_data_manager_logging_enabled()
    )

Dash DevTools
~~~~~~~~~~~~~

Enable Dash DevTools for debugging callbacks:

.. code-block:: python

    app = Dash(__name__, suppress_callback_exceptions=True)
    app.enable_dev_tools(debug=True, dev_tools_hot_reload=True)

Profiling
~~~~~~~~~

Profile performance-critical code:

.. code-block:: python

    import time
    
    start = time.time()
    result = expensive_operation()
    duration = time.time() - start
    print(f"Operation took {duration:.2f} seconds")

Performance Optimization
------------------------

Caching
~~~~~~~

Use LRU cache for expensive operations:

.. code-block:: python

    from cachetools import LRUCache
    
    class MyManager:
        def __init__(self):
            self._cache = LRUCache(maxsize=20)
        
        def get_data(self, key):
            if key in self._cache:
                return self._cache[key]
            
            data = expensive_load(key)
            self._cache[key] = data
            return data

Data Loading
~~~~~~~~~~~~

- Read only necessary columns from CSV files
- Use ``usecols`` parameter in ``pd.read_csv()``
- Cache loaded experiment objects
- Lazy load large data structures

Callback Optimization
~~~~~~~~~~~~~~~~~~~~~

- Use ``prevent_initial_call=True`` when appropriate
- Avoid unnecessary callback chains
- Use ``dash.no_update`` to skip updates
- Batch updates when possible

Deployment
----------

Docker Deployment
~~~~~~~~~~~~~~~~~

Build and run using Docker:

.. code-block:: bash

    # Build image
    docker build -t levseq-dash:latest .
    
    # Run container
    docker run -p 8050:8050 \
        -v /host/data:/data \
        -e DATA_PATH=/data \
        -e FIVE_LETTER_ID_PREFIX=PROD \
        levseq-dash:latest

Production Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Security**:
   
   - Validate all user inputs
   - Sanitize file uploads
   - Use HTTPS in production
   - Keep dependencies updated

2. **Performance**:
   
   - Enable caching
   - Optimize database queries
   - Use production WSGI server (e.g., Gunicorn)
   - Monitor resource usage

3. **Reliability**:
   
   - Implement error handling
   - Add logging and monitoring
   - Regular backups of data
   - Health check endpoints

4. **Scalability**:
   
   - Consider horizontal scaling
   - Use load balancing
   - Optimize data access patterns
   - Profile and optimize bottlenecks

Common Development Tasks
------------------------

Running the Application
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Development mode with auto-reload
    python -m levseq_dash.app.main_app
    
    # With tox
    tox -e dev

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

    # All tests
    tox -e test
    
    # Specific test
    tox -e test -- tests/test_utils/test_utils.py::test_function
    
    # With coverage
    tox -e test -- --cov=levseq_dash --cov-report=html

Code Formatting
~~~~~~~~~~~~~~~

.. code-block:: bash

    # Format code
    tox -e format
    
    # Check linting
    tox -e lint

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Build docs
    tox -e docs
    
    # Open in browser
    open docs/_build/html/index.html

Security Scanning
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Run security checks
    tox -e security

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Errors**
    Ensure all dependencies are installed and virtual environment is activated.

**Callback Errors**
    Check that all Input/Output IDs match component IDs in the layout.

**Data Loading Issues**
    Verify file paths and permissions. Enable data-manager logging.

**Alignment Performance**
    For large datasets, consider implementing pagination or filtering.

**Docker Build Failures**
    Clear Docker cache: ``docker build --no-cache``

Getting Help
~~~~~~~~~~~~

- Check existing documentation
- Search GitHub issues
- Create a new issue with detailed information
- Contact maintainers

Resources
---------

External Documentation
~~~~~~~~~~~~~~~~~~~~~~

- `Dash Documentation <https://dash.plotly.com/>`_
- `Plotly Python Documentation <https://plotly.com/python/>`_
- `Pandas Documentation <https://pandas.pydata.org/docs/>`_
- `BioPython Documentation <https://biopython.org/wiki/Documentation>`_
- `Pytest Documentation <https://docs.pytest.org/>`_

Related Projects
~~~~~~~~~~~~~~~~

- `Dash Bootstrap Components <https://dash-bootstrap-components.opensource.faculty.ai/>`_
- `Dash AG Grid <https://dash.plotly.com/dash-ag-grid>`_
- `Dash Molstar <https://github.com/ssec-jhu/dash-molstar>`_

Contributing
------------

See the `CONTRIBUTING.md <https://github.com/ssec-jhu/levseq-dash/blob/main/CONTRIBUTING.md>`_ file for detailed contribution guidelines.

Thank you for contributing to LevSeq-Dash!
