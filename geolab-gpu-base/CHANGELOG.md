# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0]

### Added

- initial geolab-gpu-base image, based on geolab-base 0.2.0
- bake in NVIDIA userspace driver (nvidia-utils/libnvidia-compute, NVIDIA_DRIVER_VERSION build arg, default 580)
- add a GPU driver check (`cli('nvidia-smi')`) to test_notebook.ipynb

No packages were added beyond what `geolab-base` already has -- `environment.yml`, `requirements.txt`, and `apt.txt` are unchanged.
