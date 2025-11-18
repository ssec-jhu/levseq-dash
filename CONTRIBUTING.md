# Contributing to LevSeq-Dash

Thank you for your interest in contributing to LevSeq-Dash! This document provides guidelines and instructions for contributing to the project.


## Code of Conduct

Please note that this project has a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## Quick Reference

### Project Structure

```
levseq-dash/
├── levseq_dash/
│   └── app/
│       ├── main_app.py              # Main Dash application
│       ├── components/              # UI components
│       │   ├── widgets.py           # Reusable widgets
│       │   ├── graphs.py            # Plotting functions
│       │   ├── vis.py               # Visualization utilities
│       │   └── column_definitions.py # Table column configs
│       ├── layouts/                 # Page layouts
│       │   ├── layout_landing.py    # Home page
│       │   ├── layout_upload.py     # Data upload page
│       │   ├── layout_experiment.py # Experiment view
│       │   └── layout_matching_sequences.py # Alignment view
│       ├── data_manager/            # Data management
│       │   ├── base.py              # Abstract base class
│       │   ├── manager.py           # Factory functions
│       │   ├── disk_manager.py      # Local storage
│       │   └── experiment.py        # Experiment data model
│       ├── sequence_aligner/        # Sequence alignment
│       │   └── bio_python_pairwise_aligner.py
│       ├── utils/                   # Utility functions
│       └── config/                  # Configuration
├── tests/                           # Test files
├── docs/                            # Documentation
└── requirements/                    # Dependencies
```

### Key Files

- **main_app.py**: App initialization, page registration
- **global_strings.py**: UI text, labels, and URL paths (most string constants are defined here)
- **components/widgets.py**: Reusable Bootstrap components
- **components/graphs.py**: Plotly figure creation
- **components/vis.py**: DataTable configurations
- **data_manager/disk_manager.py**: Local file operations
- **data_manager/experiment.py**: Experiment data model
- **sequence_aligner/bio_python_pairwise_aligner.py**: Alignment logic

For detailed architecture, see [docs/source/developer.rst](docs/source/developer.rst).

## Development Setup

See [README.md](README.md) for basic installation and setup instructions. For development:

```bash
# Install development dependencies
pip install tox
# or
pip install -r requirements/dev.txt

# Recommended: Enable detailed logging in config/config.yaml
deployment-mode: "local-instance"
logging:
  sequence-alignment-profiling: true
  data-manager: true
  pairwise-aligner: true
```

## Contributing to UI/Frontend Components

**Location**: `levseq_dash/app/components/` and `levseq_dash/app/layouts/`

### Adding New UI Components

1. **Widgets** (`components/widgets.py`): Reusable UI elements
   ```python
   def create_my_widget(element_id: str, **kwargs) -> dbc.Card:
       """
       Create a custom widget.
       
       Args:
           element_id: Unique identifier for the widget.
           **kwargs: Additional properties for customization.
           
       Returns:
           Bootstrap Card component with the widget.
       """
       return dbc.Card([
           dbc.CardHeader("Widget Title"),
           dbc.CardBody([
               # Your widget content
           ])
       ])
   ```

2. **Graphs** (`components/graphs.py`): Plotly visualizations
   ```python
   def create_my_plot(df: pd.DataFrame, **kwargs) -> go.Figure:
       """
       Create a custom plot.
       
       Args:
           df: DataFrame with required columns.
           **kwargs: Plotly figure parameters.
           
       Returns:
           Plotly Figure object.
       """
       fig = go.Figure()
       # Add traces
       fig.update_layout(template="plotly_white")
       return fig
   ```

3. **Visualizations** (`components/vis.py`): DataTable configurations
   ```python
   def create_my_table(df: pd.DataFrame, table_id: str) -> dash_table.DataTable:
       """Create a configured DataTable."""
       return dash_table.DataTable(
           id=table_id,
           columns=[{"name": col, "id": col} for col in df.columns],
           data=df.to_dict('records'),
           # Style configurations
       )
   ```

### Adding New Pages

1. **Create layout** in `layouts/layout_my_page.py`:
   ```python
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
   ```

2. **Define the path** in `global_strings.py`:
   ```python
   # Add navigation label
   nav_my_page = "My Page"
   
   # Add URL path (at the end of the file with other paths)
   nav_my_page_path = "/my-page"
   ```

3. **Register page route** in `main_app.py`:
   ```python
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
   ```

4. **Add navigation link** in `layouts/layout_bars.py` sidebar or navbar

5. **Add callbacks** in `main_app.py` (not in the layout file):
   ```python
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
   ```

**Important Notes:**
- Layout files only define the UI structure via `get_layout()` function
- All callbacks must be registered in `main_app.py` (not in layout files)
- Page routing is handled by the `route_page` callback in `main_app.py`
- Path constants are defined in `global_strings.py` for consistency


## Extending Data Manager to Support Other Persistent Storage Backends

**Location**: `levseq_dash/app/data_manager/`

### Overview
The data manager uses an abstract base class pattern with a factory for creating instances:

```
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
```

### To add new functionality to all backends:

1. **Add method to base class** (`data_manager/base.py`):
   ```python
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
   ```
2. **Implement in disk manager** (`data_manager/disk_manager.py`):
   ```python
   class DiskDataManager(DataManager):
       def my_new_method(self, param: str) -> dict[str, Any]:
           """Implement the new method."""
           # Access self._data_path for file operations
           file_path = self._data_path / f"{param}.json"
           # Read/write operations
           return result
   ```
3. **Implement in other backends** as needed (e.g., database, S3)

## Adding New CSV Data Columns

**Location**: CSV files uploaded via the UI, loaded by `Experiment` class in `levseq_dash/app/data_manager/experiment.py`

When you add new columns to your experimental CSV data, the `Experiment` class reads the entire CSV using `pd.read_csv()`, so new columns are **automatically included** in `self.data_df` without code changes.

**Do you need to modify upload/download?**

- **Upload**: No changes needed. The data manager saves the entire CSV as-is.
- **Download**: No changes needed. The data manager exports the entire `data_df` DataFrame.

**When you DO need to make changes:**

1. **If new columns need special validation** during upload:
   - Add validation in `data_manager/disk_manager.py` → `add_experiment_from_ui()`
   - Example: Check for required columns, validate data types

2. **If new columns should appear in the UI** (tables, graphs):
   - Update column definitions in `column_definitions.py`
   - Add to visualizations in `graphs.py` or layout files

3. **If new columns need transformation** during load/save:
   - Modify `Experiment.__init__()` to process the new columns
   - Update serialization methods if storing derived data

## To add a new storage backend (Example: S3):

**Step 1: Create new manager class** in `data_manager/s3_manager.py`:
```python
from levseq_dash.app.data_manager.base import BaseDataManager
# ... other imports

class S3DataManager(BaseDataManager):
    def __init__(self, bucket_name: str, prefix: str = "experiments/"):
        super().__init__()
        self.bucket = bucket_name
        # ...and any other specific initialization for this storage mode
    
    def get_experiment(self, experiment_id: str):
        # Download from S3 and return Experiment object
        pass
    
    def add_experiment_from_ui(self, ...):
        # Upload to S3
        pass
    
    # Implement all other abstract methods from BaseDataManager
```

**Step 2: Update factory** in `manager.py`:
```python
def create_data_manager():
    if settings.is_s3_mode():
        from .s3_manager import S3DataManager
        return S3DataManager(
            bucket_name=settings.get_s3_bucket_name(),
            prefix=settings.get_s3_prefix()
        )
    elif settings.is_disk_mode():
        # ... existing code
```

**Step 3: Add configuration** in `config/config.yaml`:
```yaml
storage-mode: "s3"

s3:
  bucket-name: "my-lab-experiments"
  prefix: "enzengdb/"
  # AWS credentials via environment variables:
  # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
```

**Step 4: Update settings** in `config/settings.py`:

Follow existing patterns in `settings.py` (see `get_disk_settings()`, `is_disk_mode()`, etc.)
```python
class StorageMode(Enum):
    disk = "disk"
    db = "db"
    s3 = "s3"  # Add new mode

# add any settings functions for S3 that need to be used in the code
def is_s3_mode():
    return get_storage_mode() == StorageMode.s3.value

def get_s3_settings():
    config = load_config()
    return config.get("s3", {})

def get_s3_bucket_name():
    s3_settings = get_s3_settings()
    return s3_settings.get("bucket-name", "")

def get_s3_prefix():
    s3_settings = get_s3_settings()
    return s3_settings.get("prefix", "experiments/")
```


## Testing

**Location**: `tests/` and `levseq_dash/app/tests/`

### Test Organization

Tests are organized by functionality:

```
levseq_dash/app/tests/                     # Application tests
├── conftest.py                            # Shared fixtures and configuration
├── test_callbacks.py                      # Dash callback tests (routing, interactions)
├── test_dbmanager.py                      # Data manager operations (CRUD)
├── test_experiment.py                     # Experiment model and validation
├── test_components.py                     # UI widgets and tables
├── test_graphs.py                         # Plotting (heatmaps, rank plots, SSM)
├── test_settings.py                       # Configuration and settings
├── test_alignment.py                      # Sequence alignment integration
├── test_utils.py                          # Utility functions
└── test_data/                             # Test fixtures and sample data

levseq_dash/app/sequence_aligner/tests/    # Sequence alignment tests
├── test_pairwise_aligner.py               # Alignment algorithm logic
└── test_alignment_time.py                 # Performance benchmarks
```

### Shared Test Fixtures (`conftest.py`)

The `conftest.py` file provides reusable fixtures for all tests:

**Path Fixtures**:
- `test_data_path`, `app_data_path`: Common directory paths for test and app data
- `path_exp_ep_data`, `path_exp_ssm_data`: Paths to sample experiment files (CSV, CIF, JSON)

**Data Fixtures**:
- `experiment_ep_pcr_metadata`, `experiment_ssm_metadata`: Pre-loaded experiment metadata from JSON

**Mock Configuration Fixtures**:
- `mock_load_config_from_test_data_path`: Mock config pointing to test data directory
- `mock_get_deployment_mode`, `mock_is_data_modification_enabled`: Mock settings functions

**Data Manager Fixtures**:
- `disk_manager_from_app_data`: DiskDataManager using app data (for read-only tests)
- `disk_manager_from_temp_data`: DiskDataManager using temporary directory (for write tests)

These fixtures avoid code duplication and ensure consistent test environments.

### Writing Tests
- Follow the same pattern and use shared fixtures from `conftest.py`:
- Use fixtures from `conftest.py` for common test data and mocks
- Create custom fixtures in test files for specific test needs
- Use `tmp_path` fixture for tests that modify files
- Mock configuration to isolate tests from system settings


### Running Tests

```bash
# Run all tests
tox

# Run tests
tox -e test

# Run specific tests
tox -e test -- tests/test_specific.py::test_function
```

## Documentation

**Location**: `docs/source/`
* Add docstrings to all public functions (auto-extracted by Sphinx):
* Update `docs/source/*.rst` as needed
* Documentation is automatically built when you run `tox` without arguments.
* Building Documentation:
    ```bash
    # Build docs
    tox -e build-docs
    
  # open doc/build/html/index.html in browser
    ```

## Code Style Guidelines

### Python Code Style

We follow PEP 8 with some modifications. The project uses:

- **Black** for code formatting
- **Ruff** for linting
- **isort** for import sorting

#### Formatting

```bash
# Format code with Black
tox -e format
```

#### Linting

```bash
# Run linting
tox -e lint
```

## Pull Request Process

### Before Submitting

Run the full test suite to ensure quality:

```bash
# Run all checks (includes tests, linting, formatting, security, and docs)
tox

# Or individually
tox -e test         # Run tests
tox -e check-style  # Check code style
tox -e format       # Format code
tox -e build-docs   # Build documentation
```

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to LevSeq-Dash! 🎉
