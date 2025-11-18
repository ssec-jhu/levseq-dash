# SSEC-JHU LevSeq-Dash

[![CI](https://github.com/ssec-jhu/levseq-dash/actions/workflows/ci.yml/badge.svg)](https://github.com/ssec-jhu/levseq-dash/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ssec-jhu/levseq-dash/branch/main/graph/badge.svg?token=K04NJeMj2Y)](https://codecov.io/gh/ssec-jhu/levseq-dash)
[![Security](https://github.com/ssec-jhu/levseq-dash/actions/workflows/security.yml/badge.svg)](https://github.com/ssec-jhu/levseq-dash/actions/workflows/security.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15880411.svg)](https://doi.org/10.5281/zenodo.17310822)

> **🌐 Live Demo**: This application is publicly available at [https://enzengdb.org/](https://enzengdb.org/)



![SSEC-JHU Logo](docs/_static/SSEC_logo_horiz_blue_1152x263.png)

# About

Levseq dash is a user-friendly web application that provides a rich and interactive visualization dashboard to a comprehensive sequence-function database tailored to directed evolution experiments designed for individual labs at this phase.
The app allows users to explore parent protein structures in 3D, view ligand docking interactions, and analyze 
variants to determine which mutations lead to enhanced activity. These features streamline the decision-making process, 
offering a significant improvement over traditional spreadsheet-based approaches. Check it out live at https://enzengdb.org/


![app_snapshot_1](docs/_static/app_1.png)
![app_snapshot_2](docs/_static/app_2.png)


## Setup
  * Download & install Docker - see [Docker install docs](https://docs.docker.com/get-docker/).
  * Get the code: `git clone https://github.com/ssec-jhu/levseq-dash.git`
  * cd into repo directory: `cd levseq-dash`

This application supports two deployment modes: 
  * Public-Playground mode
  * Local-Instance mode

## Public-Playground Mode [Quick Start - recommended]:
This mode is the **fastest way** to run the app and is ideal for demos, testing, and exploration 
of the curated sample dataset publicly available online at https://enzengdb.org/

**Usage**:
```bash
# Build the docker image
docker build . -t levseq-dash:playground --no-cache

# Run the image
docker run -p 8050:8050 levseq-dash:playground

# App will be running at: http://0.0.0.0:8050
```

## Local-Instance Mode [For use locally in your lab with your own dataset]
Use this mode for setting up an instance in your lab with with persistent, user-controlled data storage. 

### Setup:
* First you'll need to open `levseq_dash/app/config/config.yaml` and configure it for local instance mode. 
* 💡 Hint: you can just copy/paste the below into `config.yaml` and modify the values as described in the next steps. 
* Configure `five-letter-id-prefix`. 
    * This should be a unique identifier for your lab or project (e.g. "MYLAB"). 
    * It must be exactly 5 letters long and can only contain alphabetic characters (A-Z, a-z). 
    * This will be prefixed to all your experiment IDs. 
* Configure a `local-data-path`:
    * This is where your experiment data will be stored on your local machine.
    * Make sure the directory exists and that you have write permissions to it.

```yaml
# Set deployment mode to local-instance
deployment-mode: "local-instance"

disk:
  # Enable data modification to allow adding/deleting data
  enable-data-modification: true
  
  # Set a unique 5-letter prefix for your lab or project 
  # OR set using environment variable
  five-letter-id-prefix: "MYLAB"
  
  # Example: absolute of data on your desktop
  local-data-path: "/Users/<username>/Desktop/MyLabData"
```

* Using Docker? You can override these settings at runtime using environment variables as well to setup multiple instances:
  * Configure `five-letter-id-prefix` using `FIVE_LETTER_ID_PREFIX` environment variable
  * Configure `local-data-path` using `DATA_PATH` environment variable
* 💡 Hint: Above environment variables **will override** values in config.yaml at runtime.

### Run:
```yaml
# Build the docker image
docker build . -t levseq-dash:local --no-cache

# Run in local instance mode using settings in config.yaml
docker run -p 8050:8050 levseq-dash:local

OR

# Run in local instance mode with environment variables to override config.yaml settings 
docker run -p 8050:8050 \
    -v /your/host/data/path:/data \
    -e DATA_PATH=/data \
    -e FIVE_LETTER_ID_PREFIX=MYLAB \
    levseq-dash:local

# App will be running at: http://0.0.0.0:8050
```
*   `-v /your/host/data/path:/data`: Mounts a directory from your host machine to the `/data` directory inside the container.
*   `-e DATA_PATH=/data`: Tells the application to use the `/data` directory for storage.
*   `-e FIVE_LETTER_ID_PREFIX=MYLAB`: Sets your unique 5-letter lab/project identifier (must be exactly 5 letters, only alphabetic characters).

## Building and Development [locally]
You can run the app for development, testing, and debugging without docker as well. Set up the config.yaml file setup for local instance mode as shown above. 
Feel free to enable additional logging and profiling options for debugging and performance testing as needed. This example has all logging options enabled.
```yaml
deployment-mode: "local-instance"

disk:
  # Enable data modification to allow uploads
  enable-data-modification: true
  
  # Path for local development (relative to app directory or absolute path)
  local-data-path: "data"  # or "/absolute/path/to/data"
  
  # 5-letter prefix of your choosing for clear distinction of experiment IDs
  five-letter-id-prefix: "DEBUG"

# Logging and profiling settings for development and debugging
logging:
  # Enable profiling for sequence alignment performance testing
  # Logs timing information for alignment operations (default: false)
  sequence-alignment-profiling: true
  
  # Enable detailed logging for data manager operations
  # Logs data loading, experiment management operations (default: false)
  data-manager: true
  
  # Enable logging for pairwise aligner detailed operations
  # Logs alignment algorithm details and performance (default: false)
  pairwise-aligner: true
```

**Logging Parameters Explained:**
- `sequence-alignment-profiling`: Enables timing logs for sequence alignment operations, useful for performance optimization
- `data-manager`: Enables detailed logging of data loading, experiment metadata operations, and file I/O
- `pairwise-aligner`: Enables verbose logging of the BioPython pairwise alignment algorithm details

**Note:** These logging settings are primarily for development and debugging. Set all to `false` in production deployments to reduce log verbosity.

**Run the app**:
With the configuration set, you can run the app directly.
```bash
python -m levseq_dash.app.main_app
```

### with Tox
```bash
# Install tox if you don't have it already (requires Python)
pip install tox

# Make sure you are in the repo directory
cd levseq-dash

# Install dependencies, run tests, and then run the app
tox -e test exec -- python -m levseq_dash.app.main_dash_app

# This will have Dash running locally on http://127.0.0.1:8050/
# Press Ctrl+c to quit
``` 
### with Conda:

For additional cmds see the [Conda cheat-sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf).

```bash
# Download and install either miniconda or anaconda first
# See: https://docs.conda.io/en/latest/miniconda.html#installing
# Or: https://docs.anaconda.com/free/anaconda/install/index.html

# Create new environment
conda create -n <environment_name>

# Activate/switch to new environment
conda activate <environment_name>

# Make sure you are in the repo directory
cd levseq-dash

# Install all required dependencies
pip install -r requirements/all.txt

# Run the app
python -m levseq_dash.app.main_app.py

# App will be running at: http://127.0.0.1:8050/
# Press Ctrl+c to quit

# Deactivate conda when done
conda deactivate
```


## Testing with tox
Typically, the CI tests run in github actions will use tox to run below. No need to manually run these.

* ``cd levseq-dash``
* Run tox ``tox``. This will run all of linting, security, test, docs and package building within tox virtual environments.
* To run an individual step, use ``tox -e {step}`` for example:
  * ``tox -e test``
  * ``tox -e format``
  * ``tox -e py311``

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:

## Documentation

- **User Documentation**: See [docs/source/usage.rst](docs/source/usage.rst) for detailed usage instructions
- **Developer Documentation**: See [docs/source/developer.rst](docs/source/developer.rst) for architecture and development guide
- **API Documentation**: Auto-generated from code docstrings - build with `tox -e build-docs`

To build documentation locally:
```bash
tox -e build-docs
open docs/_build/html/index.html
```

**Note**: Documentation is automatically built when you run `tox` (without arguments).

## License

See [LICENSE](LICENSE) file for details.


