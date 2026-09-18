# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0]

### Added

- pin base image to pangeo-base:04bb14b
- add geolab-base version as ENV GEOLAB_VERSION (set during CI build)
- add graphviz package
- add pygraphviz package
- add ipycytoscape
- added tests for new packages
- add build_process.png for README

### Changed

- removed test_packages.py
- moved test_notebook functions to test_helpers.py module to make it easier for users to import when writing tests
- updated test_notebook.ipynb to use test_helpers functions
- updated README to match Building Custom Images in docs
