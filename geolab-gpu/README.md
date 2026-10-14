# geolab-gpu

GPU-enabled flavor of [`geolab-base`](../geolab-base/): the same baked-in NVIDIA driver and CUDA-build PyTorch as before, plus a geometric deep learning stack (torchvision, torchaudio, PyTorch Geometric, torch_scatter/torch_sparse/torch_cluster, networkx) and a seismic phase-association and location toolkit (PyOcto, GaMMA, Pyrocko, REAL, NonLinLoc, HypoDD, HypoInverse) on top. If you haven't built a custom GeoLab image before, read the [`geolab-base` guide](../geolab-base/README.md) first, it covers cloning the template, editing `environment.yml`/`requirements.txt`/`apt.txt`, building and testing locally, publishing, and running the result in GeoLab. Everything there applies here too; this README only covers what's different.

Steps:

- [What's different from geolab-base](#whats-different-from-geolab-base)
- [The driver is baked into this image](#the-driver-is-baked-into-this-image)
- [Changing the driver version](#changing-the-driver-version)
- [Testing GPU access locally](#testing-gpu-access-locally)
- [Adding a GPU/ML package](#adding-a-gpuml-package)
- [Adding an association/location tool](#adding-an-associationlocation-tool)
- [Quick reference](#quick-reference)

---

## What's different from geolab-base

| File | What changed |
| --- | --- |
| `Dockerfile` | Installs the NVIDIA driver's userspace libraries (`nvidia-utils-580`, `libnvidia-compute-580`) via a new `ARG NVIDIA_DRIVER_VERSION` build stage. See [The driver is baked into this image](#the-driver-is-baked-into-this-image). Also adds a build stage (still as `root`, alongside the driver install) that clones and compiles **REAL**, **NonLinLoc**, **HypoDD**, and **HypoInverse** from source and copies the resulting binaries to `/usr/local/bin` (HypoInverse's bundled `testone` reference case also gets copied to `/opt/geolab-tests/hypoinverse/` for the notebook test). None of the four have a conda-forge, PyPI, or apt package, they're legacy Fortran/C research codes distributed as source only. See the comment above that `RUN` block for the exact repos and build quirks (REAL's `pick2real.o`, HypoInverse's interactive-prompt command script). A separate `RUN` block builds `torch_scatter`/`torch_sparse`/`torch_cluster` from source too: PyG's own wheel index has no prebuilt wheel for the pinned torch, and these need `--no-build-isolation` against torch already installed, which a `pip install -r requirements.txt` doesn't guarantee the order of. This image has no CUDA toolkit, so those three specifically compile CPU-only extensions, same build host, different problem than the NVIDIA driver note above. |
| `apt.txt` | Adds `cmake`, needed to build NonLinLoc (the other compiled tools only need `build-essential`/`gfortran`, already present). |
| `environment.yml` | Adds a `# --- GPU / machine learning ---` section: `jupyterlab-nvdashboard` (GPU utilization widget), `scikit-learn`, `scikit-image`, `xgboost`, `dask-ml`, `seaborn`, `networkx` (used directly by `torch_geometric`), and profiling tools (`line_profiler`, `memory_profiler`, `snakeviz`, `watermark`). PyTorch is *not* installed here, see the next row. |
| `requirements.txt` | Adds `torch==2.14.0+cu126` (pinned to match the baked-in driver, not left to whatever pip resolves by default) and `seisbench` (deep-learning seismic phase picking, PhaseNet/EQTransformer among its models, built on that pinned torch); `torchvision`/`torchaudio` pinned to exactly match that same torch build; `torch_geometric` (pure Python, no per-torch-version wheel); `pyocto`, `gmma` (imports as `gamma`), and `pyrocko` (phase association/location, none on conda-forge). `torch_scatter`/`torch_sparse`/`torch_cluster` are deliberately *not* here, see the `Dockerfile` row. |
| `test_notebook.ipynb` | Adds a `## GPU / machine learning` section testing the packages above, plus an informational (non-blocking) `torch.cuda.is_available()` check, and a `### GPU compute test` cell that actually runs a computation on the GPU and fails loudly if there isn't one. Adds a `## Phase association & location` section: `py()` checks for the three association pip packages, `cli()` checks for five helper/intermediate binaries, and a real functional test for each of `REAL`, `NLLoc`, `hypoDD`, and `hyp1.40` (HypoInverse) — each one runs the real binary against either a hand-built synthetic dataset with a known-true hypocenter, or (for HypoInverse) its own bundled reference case, and asserts the result matches. A `--version`/`$PATH` check wouldn't catch a binary that's on `$PATH` but silently mislocating; the functional tests do. |
| `test_gpu.py` | Same GPU compute test as the notebook cell, as a standalone script for running from a terminal or a CI step instead of a notebook. Times the matmul on CPU vs GPU (chart: `gpu_test_result.png`), then runs a sustained, FurMark-style stress test that samples utilization/temperature/memory via `pynvml` while hammering the GPU with back-to-back matmuls (chart: `gpu_stress_result.png`). |

`start` and `test_helpers.py` are unchanged from `geolab-base`.

## The driver is baked into this image

A container shares the host's kernel and can never carry its own kernel module, so only the driver's *userspace* half (the parts `nvidia-smi` and `libcuda.so.1` need) can live in the image; the kernel module is whatever the host already has loaded. The `Dockerfile` installs exactly that userspace half at build time, `nvidia-utils-${NVIDIA_DRIVER_VERSION}` and `libnvidia-compute-${NVIDIA_DRIVER_VERSION}`, not the `nvidia-driver-*` meta-package, which pulls in DKMS and tries (and fails) to build a kernel module inside the build sandbox.

This only works because `NVIDIA_DRIVER_VERSION` (580 by default) exactly matches the driver already loaded on the target GPU host. A mismatch isn't caught at build time, it fails at container *runtime*, typically as `CUDA driver version is insufficient for CUDA runtime version` or an `nvidia-smi` version-mismatch error. `torch` is pinned in `requirements.txt` to a `cu126` build for the same reason: CUDA 12.6 needs driver ≥560.28.03, which the 580 default satisfies; a newer, unpinned torch would target a newer CUDA runtime the baked-in driver can't run.

The install pulls from Ubuntu's own apt archive, no separate NVIDIA repo is added, and that archive only carries specific driver branches, not every release NVIDIA ships. At the time of writing that's 470, 550, 570, 575, 580, 590, and 610; 580 is the closest branch above the 560.28.03 minimum `torch+cu126` needs. Run `apt-cache search nvidia-utils` inside the base image to see what's currently available before picking a version.

> [!TIP]
> If your GPU host isn't fixed and known ahead of time, for example GeoLab's own shared, elastically-scheduled Kubernetes cluster, this strategy is the wrong fit: a pod can land on any node, and no single baked-in driver version will match all of them. That's the case this image's driver strategy was built for a known, dedicated host; for an elastic cluster, use a strategy that relies on the cluster's device plugin to mount whatever driver the node already has instead.

## Changing the driver version

Rebuild with a different `NVIDIA_DRIVER_VERSION` any time the host driver changes, and update the `torch` pin in `requirements.txt` to a build whose minimum required driver is still ≤ the new version:

```shell
docker build --platform linux/amd64 \
 --build-arg NVIDIA_DRIVER_VERSION=575 \
 --build-arg GEOLAB_VERSION=1.0.0 \
 -t my-geolab-gpu-image .
```

Check [NVIDIA's CUDA Toolkit and driver compatibility table](https://docs.nvidia.com/deploy/cuda-compatibility/) for the minimum driver a given CUDA/torch build needs, and the [PyTorch previous-versions page](https://pytorch.org/get-started/previous-versions/) for the wheel's exact `cuXXX` tag.

## Testing GPU access locally

`docker run` alone won't expose a GPU even with the driver baked in. You need [`nvidia-container-toolkit`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed on the host, and to pass `--gpus all`:

```shell
docker run --rm --gpus all -p 8888:8888 my-geolab-gpu-image:0.1.0
```

Without `--gpus all` (or on a host with no GPU at all), the image still builds and runs, `torch.cuda.is_available()` just reports `False` and the informational cell in `test_notebook.ipynb` prints that instead of a device name. That's not a test failure: the `## GPU / machine learning` section's `py()`/`cli()` checks import and exercise each package on the CPU either way, they don't require a GPU to pass.

The `### GPU compute test` cell right after it is different: it's a real pass/fail test, not just an import check. It allocates two 4096x4096 tensors on the GPU, multiplies them, and prints the device name and a sample result, asserting `torch.cuda.is_available()` first with a clear error message if it isn't. Run it after `--gpus all` to confirm the driver, CUDA, and torch are actually wired together correctly, not just installed. The same test is also available as a standalone script, `test_gpu.py`, for running from a terminal instead of a notebook:

```shell
python test_gpu.py
```

That quick check only proves one op works, it doesn't say whether the GPU holds up under sustained load. `test_gpu.py` also runs a FurMark-style stress test: continuous back-to-back matmuls for a fixed duration (20s by default) while sampling GPU utilization, temperature, and memory use via `pynvml` (from the `nvidia-ml-py` package, also used by `jupyterlab-nvdashboard`). It prints a summary and saves a time-series chart of utilization/temperature to `gpu_stress_result.png`, and warns (without failing) if temperature reaches 90°C, worth a look, not necessarily a problem. Adjust the duration with `--stress-seconds`:

```shell
python test_gpu.py --stress-seconds 60
```

## Adding a GPU/ML package

Same process as `geolab-base`: add it to `environment.yml` (or `requirements.txt` if it's pip-only) under the `# --- GPU / machine learning ---` section, then add a matching `py()`/`cli()` check to the `## GPU / machine learning` cell in `test_notebook.ipynb`. See [geolab-base's "Adding a test for a new package"](../geolab-base/README.md#step-3-build-and-test-locally) for the details.

If the package needs `torch`, don't add it to `environment.yml` too, pip will detect the pinned `torch` in `requirements.txt` already satisfies that dependency.

## Adding an association/location tool

If it's a Python package: add it to `requirements.txt` (none of the six added here are on conda-forge, check before assuming `environment.yml`), then add a `py()` check to the `## Phase association & location` cell in `test_notebook.ipynb`. `pyocto` and `gamma` need real arguments to construct anything (see the existing calls for a minimal, working example of each), most others will import cleanly with no arguments.

If it has no Python package at all, REAL, NonLinLoc, HypoDD, and HypoInverse didn't, it means building from source. Add the `git clone` + build commands to the `RUN` block in the `Dockerfile` (as `root`, before the final `USER ${NB_USER}`), copy the resulting binary to `/usr/local/bin`, then add a `cli()` check for it, or a real `functional()` test if you can derive or find a known-correct result to check it against (see HypoInverse's own bundled `testone` example for a case where the tool ships one, instead of hand-deriving a synthetic one like REAL/NLLoc/hypoDD). Before writing the `RUN` block, actually try the build in a plain `ubuntu:24.04` container first, exactly the way this project's own four were verified, checked-in prebuilt objects, macOS-only compiler defaults, interactive-only command scripts, and READMEs that don't match the actual build are all real things that happen with research code like this, and a failed build step is an expensive way to find out during a real `docker build`. For a tool with no public git source at all (USGS doesn't host HypoInverse on one, for instance), look for an unofficial mirror before giving up, check it's a clean, unauthenticated clone of genuinely public-domain or appropriately-licensed source, not a workaround for a paywall or registration requirement.

## Quick reference

| What you want to do | Where to do it |
| --- | --- |
| Add a conda GPU/ML package | `environment.yml`, under `# --- GPU / machine learning ---` |
| Add a pip-only ML package | `requirements.txt` |
| Change the baked-in driver version | `--build-arg NVIDIA_DRIVER_VERSION=<version>`, and update the `torch` pin to match |
| Test locally with a GPU | `docker run --rm --gpus all -p 8888:8888 <image>` (needs `nvidia-container-toolkit` on the host) |
| Test locally without a GPU | `docker run --rm -p 8888:8888 <image>` (packages still import; `torch.cuda.is_available()` reports `False`) |
| Check CUDA is visible in a session | Run the `## GPU / machine learning` cell in `test_notebook.ipynb` |
| Prove the GPU actually computes | Run the `### GPU compute test` cell in `test_notebook.ipynb`, or `python test_gpu.py` |
| Stress-test the GPU under sustained load | `python test_gpu.py --stress-seconds 60` |
| Add a pip association/location package | `requirements.txt` (check it's not on conda-forge first) |
| Add a source-built association/location tool | `Dockerfile`, the `RUN` block that builds REAL/NonLinLoc/HypoDD/HypoInverse |
| Check the association/location tools installed | Run the `## Phase association & location` cell in `test_notebook.ipynb` |
| Everything else (build, publish, run in GeoLab) | See [geolab-base's README](../geolab-base/README.md) |
