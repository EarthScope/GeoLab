# Changelog

All notable changes to this project will be documented in this file.

## [0.10.2] - 2026-10-28

### Changed

- pin s3fs>=2026.9.0 in environment.yml (conda-lock.yml previously resolved s3fs to 0.4.2); the lock now also includes aiobotocore 3.10.0 and aioitertools, and boto3/botocore moved from 1.43.114 to 1.43.117
- test_notebook.ipynb fails if the installed s3fs is older than 2026.9.0

## [0.10.1] - 2026-10-23

### Security

- run `apt-get upgrade` during the build to pick up Ubuntu security fixes released since the pinned pangeo base image (OpenSSL CVE-2026-45447/CVE-2026-84782, wget, gnutls, util-linux/mount, tar, gzip, and others)
- pin certifi>=2026.10.19 (removes the compromised emSign ECC Root CA - G3, GHSA-6q48-6c7w-9gw2) and urllib3>=2.8.0 (CVE-2026-97687, CVE-2026-97689, CVE-2026-44431, CVE-2026-44432, CVE-2026-97688) in environment.yml
- update the base conda install's build tooling to fixed versions (certifi, urllib3, cryptography, msgpack-python, h2, hpack, pip, setuptools)
- remove conda-lock, GitPython, dulwich, and virtualenv from the base conda install after the environment is built (GitPython CVE-2026-78676 and others); conda-lock is only needed during the build, and its pinned dulwich can't be updated to a fixed version
- regenerate conda-lock.yml
- add a `## Security updates` section to test_notebook.ipynb that fails if any of these fixes is missing from the image: certifi >= 2026.10.19 without the emSign ECC Root CA - G3, urllib3 >= 2.8.0, Ubuntu OpenSSL >= 3.0.13-0ubuntu3.16, and conda-lock/GitPython/dulwich/virtualenv absent from the base conda install with fixed certifi/urllib3/cryptography there

### Changed

- GEOLAB_VERSION build arg no longer has a default value; it must be passed with `--build-arg GEOLAB_VERSION=...` or the build fails

## [0.10.0] - 2026-10-16

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
- conda-lock.yml

### Changed

- removed test_packages.py
- moved test_notebook functions to test_helpers.py module to facilitate writing tests by importing functions
- updated test_notebook.ipynb to use test_helpers functions
- updated README to match Building Custom Images in docs
- updated earthscope-sdk to 1.9.3