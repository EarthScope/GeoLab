# geolab-gpu-base

GPU-enabled flavor of [`geolab-base`](../geolab-base/): the exact same package set (`environment.yml`, `requirements.txt`, and `apt.txt` are unchanged, byte-for-byte), plus an NVIDIA driver baked into the image at build time. No GPU-specific Python packages (PyTorch, CuPy, etc.) are added here, this image exists for workloads that need GPU *driver* access but want to bring their own GPU/ML stack rather than starting from one someone else picked. If you haven't built a custom GeoLab image before, read the [`geolab-base` guide](../geolab-base/README.md) first, it covers cloning the template, editing `environment.yml`/`requirements.txt`/`apt.txt`, building and testing locally, publishing, and running the result in GeoLab. Everything there applies here too; this README only covers what's different.

> [!TIP]
> If you know you want PyTorch and seismic ML tooling pre-installed and pinned to the driver, start from [`geolab-gpu`](../geolab-gpu/) instead (adds `torch`, `seisbench`, `scikit-learn`, and friends, plus a real GPU compute test), or [`geolab-gpu2`](../geolab-gpu2/) (that, plus a seismic phase-association/location toolkit). This image is the minimal "driver only" starting point for building your own GPU stack on top of `geolab-base`.

Steps:

- [What's different from geolab-base](#whats-different-from-geolab-base)
- [The driver is baked into this image](#the-driver-is-baked-into-this-image)
- [Changing the driver version](#changing-the-driver-version)
- [Testing GPU access locally](#testing-gpu-access-locally)
- [Adding a GPU/ML package](#adding-a-gpuml-package)
- [Quick reference](#quick-reference)

---

## What's different from geolab-base

| File | What changed |
| --- | --- |
| `Dockerfile` | Installs the NVIDIA driver's userspace libraries (`nvidia-utils-580`, `libnvidia-compute-580`) via a new `ARG NVIDIA_DRIVER_VERSION` build stage. See [The driver is baked into this image](#the-driver-is-baked-into-this-image). |
| `test_notebook.ipynb` | Adds a `## GPU driver` section with an informational `cli('nvidia-smi')` check -- confirms the userspace driver installed, not that a GPU is actually reachable from the container (that needs `--gpus all` at `docker run`, see [Testing GPU access locally](#testing-gpu-access-locally)). |

`environment.yml`, `requirements.txt`, `apt.txt`, `start`, and `test_helpers.py` are unchanged from `geolab-base`.

## The driver is baked into this image

A container shares the host's kernel and can never carry its own kernel module, so only the driver's *userspace* half (the parts `nvidia-smi` and `libcuda.so.1` need) can live in the image; the kernel module is whatever the host already has loaded. The `Dockerfile` installs exactly that userspace half at build time, `nvidia-utils-${NVIDIA_DRIVER_VERSION}` and `libnvidia-compute-${NVIDIA_DRIVER_VERSION}`, not the `nvidia-driver-*` meta-package, which pulls in DKMS and tries (and fails) to build a kernel module inside the build sandbox.

This only works because `NVIDIA_DRIVER_VERSION` (580 by default) exactly matches the driver already loaded on the target GPU host. A mismatch isn't caught at build time, it fails at container *runtime*, typically as `CUDA driver version is insufficient for CUDA runtime version` or an `nvidia-smi` version-mismatch error. Unlike `geolab-gpu`, there's no pinned CUDA-build PyTorch here to drive the version choice, so pick whichever branch matches your actual host; if you add a GPU-accelerated package yourself later, pin it to a CUDA build whose minimum driver requirement is ≤ the version you choose here (see `geolab-gpu`'s `requirements.txt` for a worked example with `torch+cu126`).

The install pulls from Ubuntu's own apt archive, no separate NVIDIA repo is added, and that archive only carries specific driver branches, not every release NVIDIA ships. At the time of writing that's 470, 550, 570, 575, 580, 590, and 610. Run `apt-cache search nvidia-utils` inside the base image to see what's currently available before picking a version.

> [!TIP]
> If your GPU host isn't fixed and known ahead of time, for example GeoLab's own shared, elastically-scheduled Kubernetes cluster, this strategy is the wrong fit: a pod can land on any node, and no single baked-in driver version will match all of them. That's the case this image's driver strategy was built for a known, dedicated host; for an elastic cluster, use a strategy that relies on the cluster's device plugin to mount whatever driver the node already has instead.

## Changing the driver version

Rebuild with a different `NVIDIA_DRIVER_VERSION` any time the host driver changes:

```shell
docker build --platform linux/amd64 \
 --build-arg NVIDIA_DRIVER_VERSION=575 \
 --build-arg GEOLAB_VERSION=1.0.0 \
 -t my-geolab-gpu-base-image .
```

Check [NVIDIA's CUDA Toolkit and driver compatibility table](https://docs.nvidia.com/deploy/cuda-compatibility/) if you're pairing this with a CUDA-accelerated package you add yourself.

## Testing GPU access locally

`docker run` alone won't expose a GPU even with the driver baked in. You need [`nvidia-container-toolkit`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) installed on the host, and to pass `--gpus all`:

```shell
docker run --rm --gpus all -p 8888:8888 my-geolab-gpu-base-image:0.1.0
```

Without `--gpus all` (or on a host with no GPU at all), the image still builds and runs; `nvidia-smi` will be on `$PATH` (installed at build time) but can't report a real device, since the driver's kernel module and device nodes are only present with GPU passthrough. The `## GPU driver` cell's `cli('nvidia-smi')` check is informational for exactly this reason: unlike `geolab-gpu`'s `### GPU compute test`, there's no Python package here to run a real computation against, so this image has no automated pass/fail GPU test. Confirm the driver is actually working by running `nvidia-smi` yourself from a terminal inside the container after `--gpus all` and checking it reports a real device.

## Adding a GPU/ML package

Same process as `geolab-base`: add it to `environment.yml` (or `requirements.txt` if it's pip-only), then add a matching `py()`/`cli()` check to `test_notebook.ipynb`. See [geolab-base's "Adding a test for a new package"](../geolab-base/README.md#step-3-build-and-test-locally) for the details.

If the package needs a CUDA build (PyTorch, CuPy, etc.), pin it in `requirements.txt` to a build whose minimum driver requirement is ≤ `NVIDIA_DRIVER_VERSION` above; see `geolab-gpu`'s `requirements.txt` for exactly this pattern with `torch==2.14.0+cu126`.

## Quick reference

| What you want to do | Where to do it |
| --- | --- |
| Add a conda package | `environment.yml` |
| Add a pip-only package | `requirements.txt` |
| Change the baked-in driver version | `--build-arg NVIDIA_DRIVER_VERSION=<version>` |
| Test locally with a GPU | `docker run --rm --gpus all -p 8888:8888 <image>` (needs `nvidia-container-toolkit` on the host) |
| Test locally without a GPU | `docker run --rm -p 8888:8888 <image>` (packages still import; `nvidia-smi` won't report a real device) |
| Check the driver installed | Run the `## GPU driver` cell in `test_notebook.ipynb`, or run `nvidia-smi` from a terminal |
| Everything else (build, publish, run in GeoLab) | See [geolab-base's README](../geolab-base/README.md) |
