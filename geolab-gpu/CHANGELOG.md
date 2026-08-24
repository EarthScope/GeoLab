# Changelog

All notable changes to this project will be documented in this file.

## [1.0.1]

### Added

- pin base image to pangeo-base:04bb14b
- add geolab-base version as ENV GEOLAB_VERSION (must be manually edited)
- add graphviz package
- add pygraphviz package
- add ipycytoscape
- added tests for new packages

### Changed

- removed test_packages.py
- moved test_notebook functions to test_helpers.py module to make it easier for users to import when writing tests
- updated test_notebook.ipynb to use test_helpers functions
