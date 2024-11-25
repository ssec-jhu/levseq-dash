# SSEC-JHU LevSeq-Dash

[![CI](https://github.com/ssec-jhu/levseq-dash/actions/workflows/ci.yml/badge.svg)](https://github.com/ssec-jhu/levseq-dash/actions/workflows/ci.yml)
<!---[![Documentation Status](https://readthedocs.org/projects/ssec-jhu-levseq-dash/badge/?version=latest)](https://ssec-jhu-levseq-dash.readthedocs.io/en/latest/?badge=latest) --->
<!---[![codecov](https://codecov.io/gh/ssec-jhu/levseq-dash/branch/main/graph/badge.svg?token=0KPNKHRC2V)](https://codecov.io/gh/ssec-jhu/levseq-dash) --->
[![Security](https://github.com/ssec-jhu/levseq-dash/actions/workflows/security.yml/badge.svg)](https://github.com/ssec-jhu/levseq-dash/actions/workflows/security.yml)
<!---[![DOI](https://zenodo.org/badge/<insert_ID_number>.svg)](https://zenodo.org/badge/latestdoi/<insert_ID_number>) --->


![SSEC-JHU Logo](docs/_static/SSEC_logo_horiz_blue_1152x263.png)

Base repo template to be used by all others.

Things to do when using this template:

 * Run ```python project_setup.py```
 * Uncomment above DOI in README.md and correct ``<insert_ID_number>``.
 * Correct "description" field in .zenodo.json to reflect description of child repo.
 * Correct the ``CI Status`` badge with the correct token in the URL.
 * Import package into https://readthedocs.org/.

What's included in this template:

 * Licence file
 * Code of Conduct
 * Build & Setup, inc. ``pip`` dependency requirements.
 * Dependabot GitHub action
 * CI for GitHub actions: lint, pytest, build & publish docker image to GitHub Packages.
 * Dockerfile.
 * Pytest example(s).
 * Githooks.

# Installation, Build, & Run instructions

### Conda:

For additional cmds see the [Conda cheat-sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf).

 * Download and install either [miniconda](https://docs.conda.io/en/latest/miniconda.html#installing) or [anaconda](https://docs.anaconda.com/free/anaconda/install/index.html).
 * Create new environment (env) and install ``conda create -n <environment_name>``
 * Activate/switch to new env ``conda activate <environment_name>``
 * ``cd`` into repo dir.
 * Install ``python`` and ``pip`` ``conda install python=3.11 pip``
 * Install all required dependencies (assuming local dev work), there are two ways to do this
   * If working with tox (recommended) ``pip install -r requirements/dev.txt``.
   * If you would like to setup an environment with all requirements to run outside of tox ``pip install -r requirements/all.txt``.

### Build:

  #### with Docker:
  * Download & install Docker - see [Docker install docs](https://docs.docker.com/get-docker/).
  * ``cd`` into repo dir.
  * Build image: ``docker build -t <image_name> .``

  #### with Python ecosystem:
  * ``cd`` into repo dir.
  * ``conda activate <environment_name>``
  * Build and install package in <environment_name> conda env: ``pip install .``
  * Do the same but in dev/editable mode (changes to repo will be reflected in env installation upon python kernel restart)
    _NOTE: This is the preferred installation method for dev work._
    ``pip install -e .``.
    _NOTE: If you didn't install dependencies from ``requirements/dev.txt``, you can install
    a looser constrained set of deps using: ``pip install -e .[dev]``._

### Run

  #### with Docker:
  * Follow the above [Build with Docker instructions](#with-docker).
  * Run container from image: ``docker run -d -p 8000:8000 <image_name>``. _NOTE: ``-p 8000:8000`` is specific to the example application using port 8000._
  * Alternatively, images can be pulled from ``ghcr.io/ssec-jhu/`` e.g., ``docker pull ghcr.io/ssec-jhu/levseq-dash:pr-1``.

  #### with Python ecosystem:
  * Follow the above [Build with Python ecosystem instructions](#with-python-ecosystem).
  * Run ``uvicorn levseq_dash.app.main:app --host 0.0.0.0 --port", "8000``. _NOTE: This is just an example and is obviously application dependent._

### Usage:
To be completed by child repo.


# Testing
_NOTE: The following steps require ``pip install -r requirements/dev.txt``._

## Using tox

* Run tox ``tox``. This will run all of linting, security, test, docs and package building within tox virtual environments.
* To run an individual step, use ``tox -e {step}`` for example, ``tox -e test``, ``tox -e build-docs``, etc.

Typically, the CI tests run in github actions will use tox to run as above. See also [ci.yml](https://github.com/ssec-jhu/levseq-dash/blob/main/.github/workflows/ci.yml).

## Outside of tox:

The below assume you are running steps without tox, and that all requirements are installed into a conda environment, e.g. with ``pip install -r requirements/all.txt``.

_NOTE: Tox will run these for you, this is specifically if there is a requirement to setup environment and run these outside the purview of tox._

### Linting:
Facilitates in testing typos, syntax, style, and other simple code analysis tests.
  * ``cd`` into repo dir.
  * Switch/activate correct environment: ``conda activate <environment_name>``
  * Run ``ruff .``
  * This can be automatically run (recommended for devs) every time you ``git push`` by installing the provided
    ``pre-push`` git hook available in ``./githooks``.
    Instructions are in that file - just ``cp ./githooks/pre-push .git/hooks/;chmod +x .git/hooks/pre-push``.

### Security Checks:
Facilitates in checking for security concerns using [Bandit](https://bandit.readthedocs.io/en/latest/index.html).
 * ``cd`` into repo dir.
 * ``bandit --severity-level=medium -r levseq_dash``

### Unit Tests:
Facilitates in testing core package functionality at a modular level.
  * ``cd`` into repo dir.
  * Run all available tests: ``pytest .``
  * Run specific test: ``pytest tests/test_util.py::test_base_dummy``.

### Regression tests:
Facilitates in testing whether core data results differ during development.
  * WIP

### Smoke Tests:
Facilitates in testing at the application and infrastructure level.
  * WIP

### Build Docs:
Facilitates in building, testing & viewing the docs.
 * ``cd`` into repo dir.
 * ``pip install -r requirements/docs.txt``
 * ``cd docs``
 * ``make clean``
 * ``make html``
 * To view the docs in your default browser run ``open docs/_build/html/index.html``.
