# Changelog

All notable changes to this project will be documented in this file.

## [0.10.0]

### Added

- pin base image to pangeo-base:04bb14b
- geolab-base version is set as ENV GEOLAB_VERSION
- graphviz
- pygraphviz
- ipycytoscape
- nano
- vim
- nbgitpuller
- jupyterlab-topbar-stop-server
- tests for new packages
- a build_process.png for README

### Changed

- removed test_packages.py
- moved test_notebook functions to test_helpers.py module to facilitate writing tests by importing functions
- updated test_notebook.ipynb to use test_helpers functions
- updated README to match Building Custom Images in docs
- updated earthscope-sdk to 1.9.3