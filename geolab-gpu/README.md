# geolab-gpu

GPU-enabled flavor of [`geolab-base`](../geolab-base/): the same baked-in NVIDIA driver and CUDA-build PyTorch as before, plus a geometric deep learning stack (torchvision, torchaudio, PyTorch Geometric, torch_scatter/torch_sparse/torch_cluster, networkx) and a seismic phase-association and location toolkit (PyOcto, GaMMA, Pyrocko, REAL, NonLinLoc, HypoDD, HypoInverse) on top. If you haven't built a custom GeoLab image before, read the [`geolab-base` guide](../geolab-base/README.md) first, it covers cloning the template, editing `environment.yml`/`requirements.txt`/`apt.txt`, building and testing locally, publishing, and running the result in GeoLab. Everything there applies here too; this README only covers what's different.

Steps:

- [What's different from geolab-base](#whats-different-from-geolab-base)
- [Keeping in sync with geolab-base](#keeping-in-sync-with-geolab-base)
- [The driver is baked into this image](#the-driver-is-baked-into-this-image)
- [Changing the driver version](#changing-the-driver-version)
- [Building for other NVIDIA drivers](#building-for-other-nvidia-drivers)
- [Testing GPU access locally](#testing-gpu-access-locally)
- [Adding a GPU/ML package](#adding-a-gpuml-package)
- [Adding an association/location tool](#adding-an-associationlocation-tool)
- [Quick reference](#quick-reference)

---

## What's different from geolab-base

| File | What changed |
| --- | --- |
| `Dockerfile` | Installs the NVIDIA driver's userspace libraries (`nvidia-utils-580`, `libnvidia-compute-580`) via a new `ARG NVIDIA_DRIVER_VERSION` build stage, or skips it with `NVIDIA_DRIVER_VERSION=none` to use the host's driver instead. See [The driver is baked into this image](#the-driver-is-baked-into-this-image) and [Building for other NVIDIA drivers](#building-for-other-nvidia-drivers). Also adds a build stage (still as `root`, alongside the driver install) that clones and compiles **REAL**, **NonLinLoc**, **HypoDD**, and **HypoInverse** from source and copies the resulting binaries to `/usr/local/bin` (HypoInverse's bundled `testone` reference case also gets copied to `/opt/geolab-tests/hypoinverse/` for the notebook test). None of the four have a conda-forge, PyPI, or apt package, they're legacy Fortran/C research codes distributed as source only. See the comment above that `RUN` block for the exact repos and build quirks (REAL's `pick2real.o`, HypoInverse's interactive-prompt command script). A separate `RUN` block builds `torch_scatter`/`torch_sparse`/`torch_cluster` from source too: PyG's own wheel index has no prebuilt wheel for the pinned torch, and these need `--no-build-isolation` against torch already installed, which a `pip install -r requirements.txt` doesn't guarantee the order of. They're compiled with CUDA kernels so their ops run on the GPU: the `Dockerfile` installs a CUDA 12.6 compiler toolkit (nvcc plus the CUDA runtime and cuBLAS/cuSPARSE/cuSOLVER/cuRAND headers, matching torch's `cu126` build) from NVIDIA's apt repo, and it stays in the image (`CUDA_HOME`, `nvcc` on `PATH`) so you can compile your own CUDA code too. No GPU is needed to build. The `TORCH_CUDA_ARCH_LIST` build arg picks which GPU architectures to compile for. It defaults to `7.5`, the Tesla T4 the GeoLab GPU host has, so these three packages' CUDA ops run only on a T4; for another GPU, pass its compute capability, e.g. `--build-arg TORCH_CUDA_ARCH_LIST="8.0"` for an A100. |
| `apt.txt` | Adds `cmake`, needed to build NonLinLoc (the other compiled tools only need `build-essential`/`gfortran`, already present). |
| `environment.yml` | Pins `numpy>=2.0,<2.5` where `geolab-base` leaves numpy unpinned: `numba-cuda` 0.30.4 calls `np.row_stack`, which numpy 2.5 removed, so compiling any CUDA kernel fails on newer numpy. Pins `scikit-learn=1.7.0` because `gmma` (GaMMA) requires exactly `scikit-learn==1.7`; without the pin, pip would replace conda's newer scikit-learn during the `requirements.txt` step. Adds a `# --- GPU / machine learning ---` section: `jupyterlab-nvdashboard` (GPU utilization widget), `nvidia-ml-py` (pynvml, GPU utilization/temperature queries used by `test_gpu.py`'s stress test), `scikit-learn`, `scikit-image`, `dask-ml`, `seaborn`, `networkx` (used directly by `torch_geometric`), and profiling tools (`line_profiler`, `memory_profiler`, `snakeviz`, `watermark`). PyTorch and the other GPU-accelerated packages are *not* installed here, see the next row: conda-forge's CUDA builds need a GPU present at solve time, which `docker build` doesn't have, so conda would silently fall back to CPU-only builds. |
| `requirements.txt` | Adds `torch==2.14.0+cu126` (pinned to match the baked-in driver, not left to whatever pip resolves by default) and `seisbench` (deep-learning seismic phase picking, PhaseNet/EQTransformer among its models, built on that pinned torch); `torchvision`/`torchaudio` pinned to exactly match that same torch build; `torch_geometric` (pure Python, no per-torch-version wheel); GPU-accelerated compute as CUDA 12 wheels that share torch's CUDA libraries rather than adding a second CUDA runtime: `xgboost-cu12` (GPU training with `device="cuda"`, imports as `xgboost`), `cupy-cuda12x` (NumPy/SciPy-compatible GPU arrays), and `numba-cuda[cu12]` (Numba's CUDA target, `numba.cuda`); `pyocto`, `gmma` (imports as `gamma`), and `pyrocko` (phase association/location, none on conda-forge). `torch_scatter`/`torch_sparse`/`torch_cluster` are deliberately *not* here, see the `Dockerfile` row. |
| `test_notebook.ipynb` | Adds a `## GPU / machine learning` section testing the packages above, plus an informational (non-blocking) `torch.cuda.is_available()` check, and a `### GPU compute test` cell that actually runs a computation on the GPU with each of torch, CuPy, Numba, and XGBoost, and fails loudly if there isn't one. Adds a `## Phase association & location` section: `py()` checks for the three association pip packages, `cli()` checks for two helper binaries (`pick2real`, `ph2dt`), and a real functional test for each of `REAL`, `NLLoc` (which also runs `Vel2Grid` and `Grid2Time`), `hypoDD`, `velest`, and `hyp1.40` (HypoInverse) — each one runs the real binary against either a hand-built synthetic dataset with a known-true answer, or (for HypoInverse) its own bundled reference case, and asserts the result matches. The `velest` test runs a joint velocity-and-hypocenter inversion: it starts from a wrong 1D model (5.6 km/s) and must recover the true 6.0 km/s and relocate 40 synthetic events. A `--version`/`$PATH` check wouldn't catch a binary that's on `$PATH` but silently mislocating; the functional tests do. |
| `test_gpu.py` | Same torch GPU compute test as the notebook cell, as a standalone script for running from a terminal or a CI step instead of a notebook. Times the matmul on CPU vs GPU (chart: `gpu_test_result.png`), then runs a sustained, FurMark-style stress test that samples utilization/temperature/memory via `pynvml` while hammering the GPU with back-to-back matmuls (chart: `gpu_stress_result.png`). |

| `test_helpers.py` | Adds a `functional(label, fn)` helper: runs `fn()` as a real functional test and records its success detail (or the exception) in the results table. The notebook uses it for the `REAL`, `NLLoc`, `hypoDD`, `velest`, and `hyp1.40` tests. |

`start` is the same as `geolab-base`'s apart from its header comment.

## Keeping in sync with geolab-base

`geolab-gpu` builds `FROM` the same pangeo base image as `geolab-base` rather than from the `geolab-base` image, so it has its own copies of the files the build reads. `environment.yml`, `requirements.txt`, and `apt.txt` are `geolab-base`'s files, in the same order, with this image's changes kept in fixed places so they're easy to compare:

| File | Differs from `geolab-base`'s only by |
| --- | --- |
| `environment.yml` | The `numpy` entry is replaced in place by the pinned `numpy>=2.0,<2.5` (with its comment); the `# --- GPU / machine learning ---` section is added at the end of `dependencies`. |
| `requirements.txt` | The header comment says "GPU image"; everything from `# --- GPU / machine learning ---` on is added at the end. |
| `apt.txt` | `cmake` is added at the end (no comments allowed: the build passes every line to `apt-get install`). `geolab-base`'s `apt.txt` has no final newline, so `diff` also shows its last line (`vim`) as changed, with a "No newline at end of file" note; that's expected. |

When `geolab-base` changes one of these files, make the same change in the same place here and keep the GPU additions at the end. Then, from `geolab-gpu/`, check that only the differences above remain and regenerate the lock file:

```shell
diff ../geolab-base/environment.yml environment.yml
diff ../geolab-base/requirements.txt requirements.txt
diff ../geolab-base/apt.txt apt.txt
conda-lock lock -f environment.yml -p linux-64 --virtual-package-spec virtual-packages.yml --lockfile conda-lock.yml
```

`virtual-packages.yml` tells `conda-lock` the build target's glibc version; regenerate the lock after any `environment.yml` change, since the build installs from `conda-lock.yml`, not `environment.yml`.

The `Dockerfile` and `test_notebook.ipynb` need the same care. Every instruction in `geolab-base`'s `Dockerfile` (its `FROM` pangeo base-image tag, the `GEOLAB_VERSION` check, `ENV`, the "Security updates" step, `CMD`) should appear unchanged in this one; only the `IMAGE_TITLE` default differs. Every test notebook section except `## Setup` and the GPU and phase-association sections should match `geolab-base`'s.

## The driver is baked into this image

A container shares the host's kernel and can never carry its own kernel module, so only the driver's *userspace* half (the parts `nvidia-smi` and `libcuda.so.1` need) can live in the image; the kernel module is whatever the host already has loaded. The `Dockerfile` installs exactly that userspace half at build time, `nvidia-utils-${NVIDIA_DRIVER_VERSION}` and `libnvidia-compute-${NVIDIA_DRIVER_VERSION}`, not the `nvidia-driver-*` meta-package, which pulls in DKMS and tries (and fails) to build a kernel module inside the build sandbox.

This only works because `NVIDIA_DRIVER_VERSION` (580 by default) exactly matches the driver already loaded on the target GPU host. A mismatch with the host isn't caught at build time, it fails at container *runtime*, typically as `CUDA driver version is insufficient for CUDA runtime version` or an `nvidia-smi` version-mismatch error. To check a host, run the `### GPU compute test` cell in `test_notebook.ipynb` there: it prints the host's kernel driver and the `libcuda` the container loaded, and fails with an explanation if they differ. `torch` is pinned in `requirements.txt` to a `cu126` build for the same reason: CUDA 12.6 needs driver ≥560.28.03, which the 580 default satisfies; a newer, unpinned torch would target a newer CUDA runtime the baked-in driver can't run.

The install pulls from Ubuntu's own apt archive, no separate NVIDIA repo is added, and that archive only carries specific driver branches, not every release NVIDIA ships. At the time of writing, the branches it really installs are 470, 580, 595, and 615, each also as a `-server` variant. The other numbers in the archive (535, 550, 570, 575, 590, 610) are transitional packages that install one of those branches instead. 580 is the default; 470 is below the 560.28.03 minimum `torch+cu126` needs. See [Building for other NVIDIA drivers](#building-for-other-nvidia-drivers) for how to check what a branch really installs before picking a version.

> [!TIP]
> If your GPU host isn't fixed and known ahead of time, for example GeoLab's own shared, elastically-scheduled Kubernetes cluster, this strategy is the wrong fit: a pod can land on any node, and no single baked-in driver version will match all of them. This image's default driver strategy was built for a known, dedicated host. For an elastic cluster, build it with [Any driver](#any-driver-use-the-hosts-driver), which relies on the NVIDIA Container Toolkit on each node to mount whatever driver the node already has.

## Changing the driver version

Rebuild with a different `NVIDIA_DRIVER_VERSION` any time the host driver changes, and update the `torch` pin in `requirements.txt` to a build whose minimum required driver is still ≤ the new version:

```shell
docker build --platform linux/amd64 \
 --build-arg NVIDIA_DRIVER_VERSION=595 \
 --build-arg GEOLAB_VERSION=0.1.0 \
 -t my-geolab-gpu-image .
```

Check [NVIDIA's CUDA Toolkit and driver compatibility table](https://docs.nvidia.com/deploy/cuda-compatibility/) for the minimum driver a given CUDA/torch build needs, and the [PyTorch previous-versions page](https://pytorch.org/get-started/previous-versions/) for the wheel's exact `cuXXX` tag.

## Building for other NVIDIA drivers

There are two ways to build this image, depending on whether you know which driver the GPU host runs:

| Build | Use it when | Runs on |
| --- | --- | --- |
| [One specific driver](#one-specific-driver) (the default, 580) | The image only runs on one known host, or hosts that all run the same driver version, and Ubuntu's archive has that exact version | Hosts running exactly that driver version. Works with only the GPU device nodes passed in (`--device`), no NVIDIA Container Toolkit needed |
| [Any driver](#any-driver-use-the-hosts-driver) | The host isn't known ahead of time, hosts run different drivers, or Ubuntu's archive doesn't have the host's exact version, e.g. a shared Kubernetes cluster or cloud GPU instances that get driver updates | Any host with a driver ≥560.28.03 and the NVIDIA Container Toolkit (on Kubernetes, as the nodes' container runtime, e.g. installed by the GPU Operator) |

### One specific driver

1. On the GPU host, get the exact driver version:

   ```shell
   nvidia-smi --query-gpu=driver_version --format=csv,noheader   # e.g. 580.178.04
   ```

2. Check what the base image would really install for that branch. Replace both `580`s with the host's branch, the first number of the version (or e.g. `580-server`, see below):

   ```shell
   docker run --rm --platform linux/amd64 -u root --entrypoint bash pangeo/base-image:04bb14b -c \
     "apt-get update -qq && apt-get install -s --no-install-recommends nvidia-utils-580 libnvidia-compute-580 | grep '^Inst nvidia-utils'"
   ```

   This is a dry run (`-s`): it installs nothing, it only lists what the Dockerfile's driver step would install. For 580 it prints `Inst nvidia-utils-580 (580.178.04-0ubuntu0.24.04.1 ...)`. You can use the branch only if both of these hold:
   - It prints exactly one line, for the branch you asked for. A second line for another branch means the package is transitional and really installs that other branch. At the time of writing, 535, 550, 570 and 575 install 580, 590 installs 595, and 610 installs 615. Most of their package descriptions don't say so. The Dockerfile's driver step also fails the build if you pass a transitional branch, and prints what it would have installed.
   - The version in that line, up to the first `-` (`580.178.04` above), equals the host's version from step 1 exactly, not just the branch.

   The driver libraries in the image talk to the host's kernel module and refuse any other version: `nvidia-smi` reports `Driver/library version mismatch`. Ubuntu's archive usually only offers the newest release of each branch. If the host is a release behind, update the host's driver. If you can't change the host's driver, or the branch is transitional, or the host's driver didn't come from Ubuntu 24.04's archive, use [Any driver](#any-driver-use-the-hosts-driver) instead.

   If the host runs NVIDIA's server (datacenter) driver, use the `-server` package: check with `dpkg -l | grep nvidia-utils` on the host, then pass e.g. `NVIDIA_DRIVER_VERSION=580-server`. The Dockerfile installs `nvidia-utils-${NVIDIA_DRIVER_VERSION}` and `libnvidia-compute-${NVIDIA_DRIVER_VERSION}`, and both exist as `-server` packages.

3. Check the driver supports the image's CUDA version. `torch` (`cu126`) and the CUDA 12.6 toolkit need a driver ≥560.28.03. Of the branches Ubuntu's archive really installs, 580, 595 and 615 qualify unchanged; 470 is too old. For a host driver below 560.28.03, whichever build you use, these all have to move to an older CUDA version together (see [Changing the driver version](#changing-the-driver-version)):
   - the `torch`, `torchvision` and `torchaudio` pins
   - the `--extra-index-url` in `requirements.txt`
   - the `CUDA_TOOLKIT_VERSION` build arg

4. Build:

   ```shell
   docker build --platform linux/amd64 \
    --build-arg NVIDIA_DRIVER_VERSION=580-server \
    --build-arg GEOLAB_VERSION=0.1.0 \
    -t my-geolab-gpu-image:0.1.0 .
   ```

5. On the host, check that the image's driver works with the host's kernel module. Pass the GPU in with `--device` flags, not `--gpus all`: with `--gpus all`, the NVIDIA Container Toolkit mounts the host's own `nvidia-smi` into the container, which would report the host's driver whatever the image has.

   ```shell
   docker run --rm --device /dev/nvidia0 --device /dev/nvidiactl --entrypoint nvidia-smi my-geolab-gpu-image:0.1.0
   ```

   It should print the GPU and the driver version from step 1. `Failed to initialize NVML: Driver/library version mismatch` means the versions differ. To run CUDA work this way, e.g. the notebook's GPU compute test, also pass `--device /dev/nvidia-uvm`.

### Any driver (use the host's driver)

Leave the driver out of the image entirely. When the container starts, the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) mounts the host's own driver libraries (`libcuda.so.1`, `libnvidia-ml.so.1`, `nvidia-smi`) into it, so they always match whatever driver the host is running. On Kubernetes, each GPU node needs the toolkit as its container runtime plus the [NVIDIA device plugin](https://github.com/NVIDIA/k8s-device-plugin), which advertises the GPUs; the [GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html) installs both. The toolkit then mounts the driver into any pod that requests an `nvidia.com/gpu` resource.

1. Build with `NVIDIA_DRIVER_VERSION=none`, which skips the driver install:

   ```shell
   docker build --platform linux/amd64 \
    --build-arg NVIDIA_DRIVER_VERSION=none \
    --build-arg GEOLAB_VERSION=0.1.0 \
    -t my-geolab-gpu-image:0.1.0 .
   ```

   Nothing else in the build needs the driver. The CUDA toolkit install and the check that `torch_scatter`/`torch_sparse`/`torch_cluster` were built with CUDA both run without it, and every GPU package (torch, CuPy, XGBoost, `numba.cuda`, `pynvml`) still imports.

2. Run it with the toolkit (`--gpus all`), or on Kubernetes by requesting an `nvidia.com/gpu` resource. `nvidia-smi` is now the host's, so this should print the host's driver version:

   ```shell
   docker run --rm --gpus all --entrypoint nvidia-smi my-geolab-gpu-image:0.1.0
   ```

   Without the toolkit (with only `--device` flags, or with no GPU) the image has no driver at all: there's no `nvidia-smi`, and `torch.cuda.is_available()` is `False`.

The host's driver still has to support the image's CUDA version: ≥560.28.03 for `torch` `cu126`. Any newer branch works too, since NVIDIA drivers run older CUDA versions. The toolkit mounts the `compute` and `utility` driver libraries by default, which is all this image uses. If your platform sets `NVIDIA_DRIVER_CAPABILITIES`, it must include both.

Either way, the driver doesn't decide which GPU *models* the image runs on. `torch_scatter`, `torch_sparse` and `torch_cluster` are compiled only for the architectures in `TORCH_CUDA_ARCH_LIST` (default `7.5`, the T4). If your hosts have other GPUs, list them all, e.g. `--build-arg TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;8.9;9.0"` for T4, A100, A10, L4 and H100. Each architecture adds compile time.

## Testing GPU access locally

`docker run` alone won't expose a GPU even with the driver baked in. You need [`nvidia-container-toolkit`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed on the host, and to pass `--gpus all`. With the default baked-in driver you can instead pass the device nodes directly, without the toolkit: `--device /dev/nvidia0 --device /dev/nvidiactl --device /dev/nvidia-uvm` (see [One specific driver](#one-specific-driver)).

```shell
docker run --rm --gpus all -p 8888:8888 my-geolab-gpu-image:0.1.0
```

Without `--gpus all` (or on a host with no GPU at all), the image still builds and runs, `torch.cuda.is_available()` just reports `False` and the informational cell in `test_notebook.ipynb` prints that instead of a device name. That's not a test failure: the `## GPU / machine learning` section's `py()`/`cli()` checks import and exercise each package on the CPU either way, they don't require a GPU to pass.

The `### GPU compute test` cell right after it is different: it's a real pass/fail test, not just an import check. It allocates two 4096x4096 tensors on the GPU, multiplies them, and prints the device name and a sample result, asserting `torch.cuda.is_available()` first with a clear error message if it isn't. Before that it checks the NVIDIA driver: it prints the driver baked into the image (or `none`), the host's kernel driver, and the `libcuda` actually loaded, and fails with a clear message if `libcuda` and the kernel driver aren't the exact same version, which would otherwise only show up as "no GPU visible". It then runs a CuPy matmul (checked against NumPy), compiles and runs a Numba CUDA kernel, and trains a small XGBoost model with `device="cuda"`, asserting it really trained on the GPU (XGBoost otherwise falls back to CPU with only a warning). Run it after `--gpus all` to confirm the driver, CUDA, and each GPU package are actually wired together correctly, not just installed. The torch part of this test is also available as a standalone script, `test_gpu.py`, for running from a terminal instead of a notebook:

```shell
python test_gpu.py
```

That quick check only proves one op works, it doesn't say whether the GPU holds up under sustained load. `test_gpu.py` also runs a FurMark-style stress test: continuous back-to-back matmuls for a fixed duration (20s by default) while sampling GPU utilization, temperature, and memory use via `pynvml` (from the `nvidia-ml-py` package, also used by `jupyterlab-nvdashboard`). It prints a summary and saves a time-series chart of utilization/temperature to `gpu_stress_result.png`, and warns (without failing) if temperature reaches 90°C, worth a look, not necessarily a problem. Adjust the duration with `--stress-seconds`:

```shell
python test_gpu.py --stress-seconds 60
```

## Adding a GPU/ML package

Add it to `environment.yml` (or `requirements.txt` if it's pip-only) under the `# --- GPU / machine learning ---` section, regenerate `conda-lock.yml` if you changed `environment.yml` (see [Keeping in sync with geolab-base](#keeping-in-sync-with-geolab-base)), then add a matching `py()`/`cli()` check to the `## GPU / machine learning` cell in `test_notebook.ipynb`. See [geolab-base's "Adding a test for a new package"](../geolab-base/README.md#step-3-build-and-test-locally) for the details.

If the package needs `torch`, don't add it to `environment.yml` too, pip will detect the pinned `torch` in `requirements.txt` already satisfies that dependency.

## Adding an association/location tool

If it's a Python package: add it to `requirements.txt` (none of the three added here, `pyocto`, `gmma`, and `pyrocko`, are on conda-forge, check before assuming `environment.yml`), then add a `py()` check to the `## Phase association & location` cell in `test_notebook.ipynb`. `pyocto` and `gamma` need real arguments to construct anything (see the existing calls for a minimal, working example of each), most others will import cleanly with no arguments.

If it has no Python package at all, REAL, NonLinLoc, HypoDD, and HypoInverse didn't, it means building from source. Add the `git clone` + build commands to the `RUN` block in the `Dockerfile` (as `root`, before the final `USER ${NB_USER}`), copy the resulting binary to `/usr/local/bin`, then add a `cli()` check for it, or a real `functional()` test if you can derive or find a known-correct result to check it against (see HypoInverse's own bundled `testone` example for a case where the tool ships one, instead of hand-deriving a synthetic one like REAL/NLLoc/hypoDD). Before writing the `RUN` block, actually try the build in a plain `ubuntu:24.04` container first, exactly the way this project's own four were verified, checked-in prebuilt objects, macOS-only compiler defaults, interactive-only command scripts, and READMEs that don't match the actual build are all real things that happen with research code like this, and a failed build step is an expensive way to find out during a real `docker build`. For a tool with no public git source at all (USGS doesn't host HypoInverse on one, for instance), look for an unofficial mirror before giving up, check it's a clean, unauthenticated clone of genuinely public-domain or appropriately-licensed source, not a workaround for a paywall or registration requirement.

## Quick reference

| What you want to do | Where to do it |
| --- | --- |
| Add a conda GPU/ML package | `environment.yml`, under `# --- GPU / machine learning ---`, then regenerate `conda-lock.yml` |
| Add a pip-only ML package | `requirements.txt`, under `# --- GPU / machine learning ---` |
| Change the baked-in driver version | `--build-arg NVIDIA_DRIVER_VERSION=<version>` (or `<version>-server`), and update the `torch` pin to match (see [One specific driver](#one-specific-driver)) |
| Run on any host driver | `--build-arg NVIDIA_DRIVER_VERSION=none`, then run with the NVIDIA Container Toolkit (see [Any driver](#any-driver-use-the-hosts-driver)) |
| Run on other GPU models | `--build-arg TORCH_CUDA_ARCH_LIST="<arch>;<arch>"` |
| Test locally with a GPU | `docker run --rm --gpus all -p 8888:8888 <image>` (needs `nvidia-container-toolkit` on the host) |
| Test locally without a GPU | `docker run --rm -p 8888:8888 <image>` (packages still import; `torch.cuda.is_available()` reports `False`) |
| Check CUDA is visible in a session | Run the `## GPU / machine learning` cell in `test_notebook.ipynb` |
| Prove the GPU actually computes | Run the `### GPU compute test` cell in `test_notebook.ipynb`, or `python test_gpu.py` |
| Stress-test the GPU under sustained load | `python test_gpu.py --stress-seconds 60` |
| Add a pip association/location package | `requirements.txt` (check it's not on conda-forge first) |
| Pick up a new geolab-base release | Copy its changes into the same places here, then `diff` and regenerate `conda-lock.yml` (see [Keeping in sync with geolab-base](#keeping-in-sync-with-geolab-base)) |
| Add a source-built association/location tool | `Dockerfile`, the `RUN` block that builds REAL/NonLinLoc/HypoDD/HypoInverse |
| Check the association/location tools installed | Run the `## Phase association & location` cell in `test_notebook.ipynb` |
| Everything else (build, publish, run in GeoLab) | See [geolab-base's README](../geolab-base/README.md) |
