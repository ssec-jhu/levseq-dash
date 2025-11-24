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
    │              Dash Application (main_app.py)             │
    │  - Routes pages                                         │
    │  - Registers all callbacks                              │
    │  - Initializes data manager via factory                 │
    └─────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    ┌──────────┐             ┌──────────┐
    │ Layouts  │             │Components│
    │ (UI def) │             │(Widgets) │
    └────┬─────┘             └─────┬────┘
         │                         │
         └─────────┬───────────────┘
                   │
       ┌───────────┴────────────┐
       │                        │
       ▼                        ▼
    ┌─────────────────────┐    ┌──────────────┐
    │ Data Manager        │    │Seq Aligner   │
    │ ┌─────────────────┐ │    └──────┬───────┘
    │ │ Factory         │ │           │
    │ │ (manager.py)    │ │           ▼
    │ └────────┬────────┘ │    ┌──────────────┐
    │          │          │    │  BioPython   │
    │          ▼          │    │   Aligner    │
    │ ┌─────────────────┐ │    └──────────────┘
    │ │ Base (Abstract) │ │
    │ └────────┬────────┘ │
    │          │          │
    │     ┌────┴────┐     │
    │     ▼         ▼     │
    │ ┌──────┐ ┌────────┐ │
    │ │ Disk │ │ S3/DB  │ │
    │ │ Mgr  │ │(Future)│ │ 
    │ └──┬───┘ └────────┘ │
    └────┼────────────────┘
         │
         ▼
    ┌─────────────┐
    │ Experiment  │
    │   Model     │
    └─────────────┘

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

Configuration File and Settings
--------------------------------

The application uses a YAML-based configuration system located in ``levseq_dash/app/config/``. The configuration determines deployment mode, storage backend, data paths, and logging behavior.

Configuration Files
~~~~~~~~~~~~~~~~~~~

**Key Files**:

- ``config.yaml``: Main configuration file with all settings
- ``settings.py``: Python module that loads and validates configuration

**Location**: ``levseq_dash/app/config/``

Configuration Structure
~~~~~~~~~~~~~~~~~~~~~~~

The ``config.yaml`` file is organized into several sections:

.. code-block:: yaml

    # Deployment mode: "public-playground" or "local-instance"
    deployment-mode: "local-instance"
    
    # Storage backend: "disk" or "db" (database not yet implemented)
    storage-mode: "disk"
    
    # Disk storage settings
    disk:
      five-letter-id-prefix: "MYLAB"
      local-data-path: "/path/to/data"
      enable-data-modification: true
    
    # Database settings (not yet implemented)
    db:
      host: ""
      port: ""
    
    # Logging and profiling flags
    logging:
      sequence-alignment-profiling: false
      data-manager: false
      pairwise-aligner: false

Deployment Modes
~~~~~~~~~~~~~~~~

The application supports two deployment modes that determine how data is accessed and whether modifications are allowed.

**public-playground Mode**

- **Purpose**: Read-only demo environment for public websites
- **Data Location**: Bundled inside container at ``levseq_dash/app/data/``
- **Data Modification**: Disabled (cannot upload/delete experiments)
- **Use Case**: Public demos and deployment

.. code-block:: yaml

    deployment-mode: "public-playground"
    # all other settings ignored or set to false

**local-instance Mode**

- **Purpose**: Full-featured installation with persistent storage
- **Data Location**: External mount via Docker volume or local path
- **Data Modification**: User can enable in order to upload/delete experiments
- **ID Prefix**: Required when data modification is enabled - a 5-letter lab identifier prepended to all experiment UUIDs
- **Use Case**: Research labs, production deployments

.. code-block:: yaml

    deployment-mode: "local-instance"
    disk:
      enable-data-modification: true # or false if that is not wanted
      local-data-path: "/path/to/data"
      five-letter-id-prefix: "MYLAB"  # Required when enable-data-modification: true

Storage Modes
~~~~~~~~~~~~~

**Disk Storage** (Current Implementation)

Uses local filesystem for data persistence:

.. code-block:: yaml

    storage-mode: "disk"
    disk:
      five-letter-id-prefix: "MYLAB"
      local-data-path: "/Users/username/data"
      enable-data-modification: true

**Settings**:

- ``five-letter-id-prefix``: 5-letter code prepended to experiment UUIDs
  
  - **Required** when ``enable-data-modification: true``
  - Must be exactly 5 letters (no numbers or special characters)
  - Automatically converted to uppercase
  - Example: "MYLAB" → experiment IDs like "MYLAB-a1b2c3d4"

- ``local-data-path``: Path to data directory
  
  - Can be absolute: ``"/Users/username/Desktop/MyData"``
  - Can be relative to app: ``"data"`` → ``levseq_dash/app/data/``
  - Overridden by ``DATA_PATH`` environment variable

- ``enable-data-modification``: Allow upload/delete operations
  
  - ``true``: Full read-write access (requires valid ID prefix)
  - ``false``: Read-only mode

**Database Storage** (Future)

Planned support for database backends:

.. code-block:: yaml

    storage-mode: "db"
    db:
      host: "localhost"
      port: "5432"

Logging Settings
~~~~~~~~~~~~~~~~

Enable detailed logging for debugging and performance analysis:

.. code-block:: yaml

    logging:
      sequence-alignment-profiling: true   # Log alignment timing
      data-manager: true                    # Log data operations
      pairwise-aligner: true               # Log alignment details

**Logging Flags**:

- ``sequence-alignment-profiling``: Times alignment operations, useful for performance tuning
- ``data-manager``: Logs experiment CRUD operations, file I/O, cache hits/misses
- ``pairwise-aligner``: Logs BioPython alignment parameters and results

**Accessing Logging Flags in Code**:

.. code-block:: python

    from levseq_dash.app.config import settings
    from levseq_dash.app.utils import utils
    
    # Check if logging is enabled
    if settings.is_data_manager_logging_enabled():
        utils.log_with_context("Loading experiment...", log_flag=True)

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Environment variables override ``config.yaml`` settings and are the preferred method for Docker deployments.

**Available Variables**:

- ``DATA_PATH``: Override ``disk.local-data-path``
  
  .. code-block:: bash
  
      docker run -e DATA_PATH=/data -v /host/data:/data levseq-dash

- ``FIVE_LETTER_ID_PREFIX``: Override ``disk.five-letter-id-prefix``
  
  .. code-block:: bash
  
      docker run -e FIVE_LETTER_ID_PREFIX=PROD levseq-dash

**Configuration Priority** (highest to lowest):

1. Environment variables (``DATA_PATH``, ``FIVE_LETTER_ID_PREFIX``)
2. ``config.yaml`` settings
3. Default values (if applicable)



Adding New Configuration Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add new configuration settings:

1. **Add to config.yaml**:

   .. code-block:: yaml

       my-new-section:
         my-setting: "value"

2. **Add getter function to settings.py**:

   .. code-block:: python

       def get_my_new_section():
           config = load_config()
           return config.get("my-new-section", {})
       
       def get_my_setting():
           section = get_my_new_section()
           return section.get("my-setting", "default-value")

3. **Use in application code**:

   .. code-block:: python

       from levseq_dash.app.config import settings
       
       value = settings.get_my_setting()

4. **Add environment variable support** (optional):

   .. code-block:: python

       def get_my_setting():
           # Check environment variable first
           env_value = os.environ.get("MY_SETTING")
           if env_value:
               return env_value
           
           # Fall back to config file
           section = get_my_new_section()
           return section.get("my-setting", "default-value")

**Best Practices**:

- Use descriptive setting names with hyphens (``my-setting``, not ``MySetting``)
- Provide sensible defaults in getter functions
- Document new settings in config.yaml with comments
- Use environment variables for secrets and deployment-specific values
- Validate settings at application startup (raise clear errors for invalid values)

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
----------------------

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

Enable Dash DevTools for debugging callbacks and hot reload:

.. code-block:: python

    if __name__ == "__main__":
        app.run(debug=True)


