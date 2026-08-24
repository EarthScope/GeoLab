# NVIDIA Driver Strategy: Kubernetes-Injected vs. Fixed-in-Image

This repo has two GPU-enabled image flavors that take opposite approaches to
getting an NVIDIA driver into the container:

- **[geolab-injected](geolab-gpu/)** — installs CUDA-toolkit packages (conda's
  `cuda-version`, `cuda12*`-tagged TensorFlow/JAX builds) and relies on the
  container runtime (`nvidia-container-toolkit`, the standard Kubernetes/GKE
  device-plugin pattern) to mount the host's actual driver into the
  container at pod start.
- **[gpu-container](gpu-container/)** — `apt-get install`s a specific
  NVIDIA driver's *userspace* libraries (`nvidia-utils-550`,
  `libnvidia-compute-550`) directly into the image at build time.

This document compares the two strategies side by side.

## Side-by-side comparison

| Aspect | Kubernetes-injected (`geolab-injected`) | Fixed-in-image (`gpu-container`) |
|---|---|---|
| **Portability across nodes** | Runs on any GPU node regardless of driver version, as long as it's new enough for the image's CUDA toolkit | Must run on a node whose loaded kernel driver *exactly* matches the version baked into the image |
| **Self-containment** | Not fully self-contained — depends on the cluster's device plugin / driver DaemonSet being correctly configured | Self-contained for the userspace half; still needs the host's kernel module to match and device passthrough at run time |
| **Failure mode on mismatch** | Minor-version CUDA compatibility usually absorbs driver differences within a major version | Hard runtime failure (e.g. "CUDA driver version is insufficient") — not caught at build time |
| **Driver upgrades** | Centralized — cluster admins patch the node pool once, every image benefits immediately | Manual — image must be rebuilt and re-pinned (`NVIDIA_DRIVER_VERSION`) every time the host driver changes |
| **Local (non-cluster) testing** | `docker run` still needs `nvidia-container-toolkit` installed locally to expose the GPU | Works with plain `docker run` + device passthrough on any host, no GPU-operator tooling required |
| **Reproducibility** | Driver version isn't pinned to the image; can drift as the cluster's node driver is upgraded over time | Image tag captures the exact driver+CUDA combination used, reproducible years later |
| **Fit for a multi-tenant, elastic scheduler** | Designed for this — a pod can land on any node in a heterogeneous fleet | Poor fit — can't guarantee which exact node/driver a pod lands on in a shared, autoscaled cluster |
| **Fit for a single, fixed, known host** | Unnecessary overhead (device-plugin infra) for a box you fully control | Ideal — one Dockerfile, one driver, no cluster GPU tooling needed |
| **Image size / duplication** | No driver duplication; only the toolkit rides in the image | Each image bakes its own driver copy, no sharing across images or nodes |
| **Debuggability** | "No GPU" can mean a broken image, node, device-plugin, or scheduling issue — often needs cluster-level access to diagnose | Failure is local to the image/host pairing — narrower surface, but the mismatch itself is invisible until run time |
| **Operational maturity** | Standard, widely adopted pattern (NVIDIA device plugin / GPU operator) | Bespoke Dockerfile logic; less common, more manual upkeep |

## Kubernetes-injected driver — pros and cons

**Pros**
- Portable across any sufficiently-new GPU node, no rebuild needed per driver version
- Centralized driver upgrades at the node-pool level
- Decouples the image/notebook release cycle from infrastructure driver management
- The only approach that scales across a heterogeneous, autoscaled fleet
- Standard, well-supported ecosystem (NVIDIA device plugin / GPU operator)

**Cons**
- Not self-contained — depends on correct cluster-side device-plugin configuration
- Local testing still requires `nvidia-container-toolkit` on the dev machine
- Harder to debug: image, node, device-plugin, and scheduling issues all look the same ("no GPU")
- Mixed-driver node pools can still surface edge-case incompatibilities
- No per-image control over an exact driver version

## Fixed driver in image — pros and cons

**Pros**
- Fully reproducible, self-contained artifact — the tag captures the exact driver+CUDA pairing
- Works outside Kubernetes entirely (plain Docker + device passthrough)
- No dependency on a cluster GPU operator being installed or maintained
- Simple to reason about: one Dockerfile, one driver, no node variability

**Cons**
- Fragile: must exactly match the host's loaded kernel driver, and mismatches fail at run time, not build time
- Requires manual, ongoing coordination between image rebuilds and host driver upgrades
- Does not scale to a multi-tenant, elastically-scheduled cluster where pod-to-node placement isn't controlled
- Only the userspace half of the driver can be baked in — a container still can't carry its own kernel module
- No sharing across images; each one duplicates its own driver copy

## Summary

Given GeoLab is a shared JupyterHub on Kubernetes with elastic pod scheduling
(per the [root README](README.md)), the **Kubernetes-injected pattern
(`geolab-injected`) is the right default** — it's the only one of the two that
scales across a fleet where you don't control which node a given pod lands
on, and it keeps driver maintenance centralized instead of scattered across
every GPU image. The **fixed-driver pattern (`gpu-container`) earns its keep
for a narrower case**: a known, dedicated, non-elastic target — a single
on-prem GPU box, or a reproducibility snapshot pinned to one exact
driver+CUDA combination for a specific published result — which is the use
case it was built for. Neither approach eliminates the host dependency
entirely: even a fixed-driver image still needs a matching kernel module and
device passthrough at run time, since a container can never carry its own
kernel module.
