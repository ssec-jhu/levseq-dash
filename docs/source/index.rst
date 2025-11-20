Welcome to LevSeqDash Documentation!
==========================================

**LevSeq-Dash** is a user-friendly web application that provides a rich and interactive 
visualization dashboard for directed evolution experiments. It allows researchers to explore 
protein structures in 3D, analyze sequence variants, and make data-driven decisions about 
which mutations lead to enhanced activity.

🌐 **Live Application**: `https://enzengdb.org/ <https://enzengdb.org/>`_

📦 **Source Code**: `GitHub Repository <https://github.com/ssec-jhu/levseq-dash>`_

Key Features
------------

* **3D Protein Structure Visualization**: Interactive protein viewer with Molstar integration
* **Sequence-Function Database**: Comprehensive storage of directed evolution experiment data
* **Variant Analysis**: Compare and analyze mutations across experiments
* **Sequence Alignment**: BLASTP-style pairwise alignment for finding related sequences
* **Interactive Visualizations**: Heatmaps, rank plots, and single-site mutagenesis plots
* **Lab Data Management**: Upload, manage, and analyze your own experiment data

Quick Start
-----------

Get started quickly with the Public Playground mode:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/ssec-jhu/levseq-dash.git
   cd levseq-dash

   # Build and run with Docker
   docker build . -t levseq-dash:playground --no-cache
   docker run -p 8050:8050 levseq-dash:playground

   # Access at http://0.0.0.0:8050

For detailed setup instructions, see :doc:`usage`.

.. note::

   This project is under active development. Features and APIs may change.

Documentation Sections
----------------------

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   usage

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   developer
   api

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   GitHub Repository <https://github.com/ssec-jhu/levseq-dash>
   Contributing Guide <https://github.com/ssec-jhu/levseq-dash/blob/main/CONTRIBUTING.md>
   Issue Tracker <https://github.com/ssec-jhu/levseq-dash/issues>
