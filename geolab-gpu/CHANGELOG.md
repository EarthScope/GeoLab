# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0]

### Added

- initial geolab-gpu image, based on the geolab-base 0.10.2 configuration: its environment.yml, requirements.txt, and apt.txt are the base for this image's (including s3fs>=2026.9.0 and the vim apt package), plus the GPU, ML, and seismic location additions below
- add the s3fs >= 2026.9.0 check from geolab-base 0.10.2 to test_notebook.ipynb
- bake in NVIDIA userspace driver (nvidia-utils/libnvidia-compute, NVIDIA_DRIVER_VERSION build arg, default 580)
- `--build-arg NVIDIA_DRIVER_VERSION=none` leaves the driver out, so the image runs on any host driver >= 560.28.03 that the NVIDIA Container Toolkit mounts at runtime (e.g. a Kubernetes cluster with mixed or changing drivers)
- the driver step fails the build if NVIDIA_DRIVER_VERSION names a transitional Ubuntu package (535, 550, 570, 575, 590, 610 at the time of writing), which would otherwise silently install a different branch (e.g. 570 installs 580); it also prints the exact driver version installed
- the GPU compute test in test_notebook.ipynb first checks the NVIDIA driver: it prints the driver baked into the image, the host's kernel driver, and the libcuda in use, and fails with an explanation if libcuda and the kernel driver differ
- add a "Building for other NVIDIA drivers" section to README.md: how to check which driver a branch really installs (several Ubuntu branches are transitional and install another branch), how to verify the baked-in driver on the host, and the NVIDIA_DRIVER_VERSION=none build
- add torch==2.14.0+cu126, pinned to match the baked-in driver
- add seisbench package
- add scikit-learn, scikit-image, dask-ml, seaborn packages
- add GPU-accelerated xgboost-cu12, cupy-cuda12x, and numba-cuda[cu12] pip packages (CUDA 12 wheels sharing torch's CUDA libraries); xgboost comes from the CUDA 12 pip wheel rather than a CPU-only conda-forge build
- add GPU compute tests for CuPy, Numba, and XGBoost to test_notebook.ipynb; the Numba kernel launch is sized from the data (4096 blocks) instead of a fixed 4 blocks, avoiding Numba's low-occupancy warning
- add a velest functional test (joint 1D velocity + hypocenter inversion of synthetic data, must recover the true model from a wrong starting one); drop the velest/Vel2Grid/Grid2Time --version checks, which only showed a "control file not found" message (Vel2Grid and Grid2Time are already exercised by the NLLoc functional test)
- pin numpy>=2.0,<2.5: numba-cuda 0.30.4 calls np.row_stack, which numpy 2.5 removed, so compiling any CUDA kernel failed
- pin scikit-learn=1.7.0: gmma (GaMMA) pins scikit-learn==1.7 exactly in every release from 1.2.17 (the version requirements.txt uses) up to the current 1.15.0, so pip was replacing conda's newer scikit-learn with 1.7.0 during the build; conda now installs 1.7.0 itself
- add jupyterlab-nvdashboard package
- add nvidia-ml-py (pynvml) package, used by test_gpu.py's stress test
- add line_profiler, memory_profiler, snakeviz, watermark packages
- add pyocto, gmma (imports as `gamma`), pyrocko packages
- build REAL, NonLinLoc, and HypoDD from source (no conda-forge/PyPI package exists); add cmake to apt.txt for NonLinLoc
- raise HypoDD's compile-time event limits to 20000 (hypoDD MAXEVE from 6500, ph2dt MEV from 12000) for full aftershock-sequence catalogs; built with -mcmodel=medium, and hypoDD's peak memory rises from ~2.0 GB to ~3.0 GB per run
- build HypoInverse (hyp1.40) from source; no conda-forge/PyPI package, and USGS only distributes it via a request/FTP process, not a git repo -- built from github.com/BORONG-SEIS/HypoInverse, an unofficial but clean, unauthenticated mirror of the same public-domain source
- add torchvision, torchaudio pip packages, pinned to exactly match the existing torch==2.14.0+cu126 build
- add torch_geometric pip package
- add torch_scatter, torch_sparse, and torch_cluster, built from source (no prebuilt wheel exists for the pinned torch build)
- add a CUDA 12.6 compiler toolkit (nvcc, CUDA runtime, cuBLAS/cuSPARSE/cuSOLVER/cuRAND headers) from NVIDIA's apt repo, matching torch's cu126 build; CUDA_HOME set and nvcc on PATH
- build torch_scatter, torch_sparse, and torch_cluster with CUDA kernels (GPU builds), for the GPU architectures in the new TORCH_CUDA_ARCH_LIST build arg (default 7.5, the Tesla T4 on the GeoLab GPU host); the build fails if any of them ends up without CUDA
- add networkx conda package
- added tests for new packages/tools; REAL, NLLoc, hypoDD, and hyp1.40 get real functional tests (synthetic dataset -- or, for hyp1.40, its own bundled reference case -- with a known-true/known-correct result, run the binary, assert the recovery), not just a `$PATH`/`--version` check

### Security

- run `apt-get upgrade` during the build to pick up Ubuntu security fixes released since the pinned pangeo base image (OpenSSL CVE-2026-45447/CVE-2026-84782, wget, gnutls, util-linux/mount, tar, gzip, and others)
- pin certifi>=2026.10.19 (removes the compromised emSign ECC Root CA - G3, GHSA-6q48-6c7w-9gw2) and urllib3>=2.8.0 (CVE-2026-97687, CVE-2026-97689, CVE-2026-44431, CVE-2026-44432, CVE-2026-97688) in environment.yml
- update the base conda install's build tooling to fixed versions (certifi, urllib3, cryptography, msgpack-python, h2, hpack, pip, setuptools)
- remove conda-lock, GitPython, dulwich, and virtualenv from the base conda install after the environment is built (GitPython CVE-2026-78676 and others); conda-lock is only needed during the build, and its pinned dulwich can't be updated to a fixed version
- regenerate conda-lock.yml
- add a `## Security updates` section to test_notebook.ipynb that fails if any of these fixes is missing from the image: certifi >= 2026.10.19 without the emSign ECC Root CA - G3, urllib3 >= 2.8.0, Ubuntu OpenSSL >= 3.0.13-0ubuntu3.16, and conda-lock/GitPython/dulwich/virtualenv absent from the base conda install with fixed certifi/urllib3/cryptography there

### Changed

- GEOLAB_VERSION build arg has no default value and must be passed with `--build-arg GEOLAB_VERSION=...`, or the build fails (as in geolab-base 0.10.2)
