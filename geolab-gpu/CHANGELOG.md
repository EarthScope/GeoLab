# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0]

### Added

- initial geolab-gpu image, based on geolab-base 0.1.0
- bake in NVIDIA userspace driver (nvidia-utils/libnvidia-compute, NVIDIA_DRIVER_VERSION build arg, default 580)
- add torch==2.14.0+cu126, pinned to match the baked-in driver
- add seisbench package
- add scikit-learn, scikit-image, dask-ml, seaborn packages
- add GPU-accelerated xgboost-cu12, cupy-cuda12x, and numba-cuda[cu12] pip packages (CUDA 12 wheels sharing torch's CUDA libraries); xgboost-cu12 replaces conda-forge's CPU-only xgboost
- add GPU compute tests for CuPy, Numba, and XGBoost to test_notebook.ipynb; the Numba kernel launch is sized from the data (4096 blocks) instead of a fixed 4 blocks, avoiding Numba's low-occupancy warning
- add a velest functional test (joint 1D velocity + hypocenter inversion of synthetic data, must recover the true model from a wrong starting one); drop the velest/Vel2Grid/Grid2Time --version checks, which only showed a "control file not found" message (Vel2Grid and Grid2Time are already exercised by the NLLoc functional test)
- pin numpy>=2.0,<2.5: numba-cuda 0.30.4 calls np.row_stack, which numpy 2.5 removed, so compiling any CUDA kernel failed
- add jupyterlab-nvdashboard package
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
