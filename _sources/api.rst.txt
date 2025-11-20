API Reference
=============

This page contains the API documentation for LevSeq-Dash, automatically generated from docstrings in the source code.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The LevSeq-Dash API is organized into several key modules:

- **Components**: UI widgets, graphs, and visualization utilities
- **Data Manager**: Data storage and retrieval abstractions
- **Sequence Aligner**: Pairwise sequence alignment functionality
- **Utils**: Helper functions for protein visualization, reactions, and alignment formatting
- **Config**: Configuration and settings management

Module Reference
----------------

.. autosummary::
   :toctree: generated
   :recursive:

   levseq_dash

Key Modules
-----------

Components
~~~~~~~~~~

.. autosummary::
   :toctree: generated

   levseq_dash.app.components.widgets
   levseq_dash.app.components.graphs
   levseq_dash.app.components.vis
   levseq_dash.app.components.column_definitions

Data Management
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated

   levseq_dash.app.data_manager.base
   levseq_dash.app.data_manager.disk_manager
   levseq_dash.app.data_manager.experiment
   levseq_dash.app.data_manager.manager

Sequence Alignment
~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated

   levseq_dash.app.sequence_aligner.bio_python_pairwise_aligner

Utilities
~~~~~~~~~

.. autosummary::
   :toctree: generated

   levseq_dash.app.utils.utils
   levseq_dash.app.utils.u_protein_viewer
   levseq_dash.app.utils.u_seq_alignment

Configuration
~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated

   levseq_dash.app.config.settings
   levseq_dash.app.global_strings

Using the API
-------------

Import Patterns
~~~~~~~~~~~~~~~

For application components:

.. code-block:: python

    from levseq_dash.app.components import widgets, graphs
    from levseq_dash.app.data_manager import create_data_manager
    from levseq_dash.app.sequence_aligner import BioPythonPairwiseAligner

For configuration:

.. code-block:: python

    from levseq_dash.app.config import settings
    from levseq_dash.app import global_strings as gs

Common Usage Examples
~~~~~~~~~~~~~~~~~~~~~

**Creating a Data Manager**:

.. code-block:: python

    from levseq_dash.app.data_manager import create_data_manager
    
    # Creates appropriate manager based on configuration
    data_manager = create_data_manager()
    
    # Get all experiments
    experiments = data_manager.get_all_lab_experiments_with_meta_data()

**Using the Sequence Aligner**:

.. code-block:: python

    from levseq_dash.app.sequence_aligner import BioPythonPairwiseAligner
    
    aligner = BioPythonPairwiseAligner()
    results = aligner.align(query_sequence, target_sequences)

**Creating Visualizations**:

.. code-block:: python

    from levseq_dash.app.components import graphs
    import pandas as pd
    
    df = pd.DataFrame(...)  # Your data
    fig = graphs.create_heatmap(df, x_col='position', y_col='value')

Notes
-----

- All classes and functions include detailed docstrings following Google style
- Type hints are used throughout for better IDE support
- See :doc:`developer` for architectural details and contribution guidelines
