"""Prove the GPU actually computes, not just that torch imports.

Run inside the container after `docker run --gpus all ...` (needs
nvidia-container-toolkit on the host), or in a GeoLab session that was
actually scheduled onto a GPU node:

    python test_gpu.py
    python test_gpu.py --stress-seconds 60   # longer FurMark-style torture run

Two checks run:

1. A quick CPU vs GPU matmul comparison, saved as a bar chart to
   gpu_test_result.png.
2. A sustained, FurMark-style stress test: continuous heavy matmuls for
   --stress-seconds while sampling GPU utilization/temperature/memory via
   pynvml, saved as a time-series chart to gpu_stress_result.png. Where the
   first check only proves one op works, this checks the GPU holds up (no
   crash, no driver hang, no runaway temperature) under sustained full load.
"""

import argparse
import sys
import time

import matplotlib
matplotlib.use('Agg')  # headless: write straight to a file, no display needed
import matplotlib.pyplot as plt
import pynvml
import torch

MATRIX_SIZE = 4096
OUTPUT_PATH = "gpu_test_result.png"

STRESS_MATRIX_SIZE = 8192
STRESS_SAMPLE_INTERVAL_SECONDS = 0.5
STRESS_OUTPUT_PATH = "gpu_stress_result.png"
STRESS_TEMP_WARNING_C = 90  # informational only; not a hard failure


def timed_matmul(device):
    """Run one matmul on `device` and return (result, elapsed_seconds)."""
    a = torch.randn(MATRIX_SIZE, MATRIX_SIZE, device=device)
    b = torch.randn(MATRIX_SIZE, MATRIX_SIZE, device=device)

    if device.type == "cuda":
        torch.cuda.synchronize()  # don't count any pending work from setup
    start = time.perf_counter()
    c = a @ b
    if device.type == "cuda":
        torch.cuda.synchronize()  # matmul is async; wait for it before timing
    elapsed = time.perf_counter() - start

    return c, elapsed


def plot_comparison(cpu_seconds, gpu_seconds, gpu_name):
    """Save a bar chart comparing CPU vs GPU matmul time to OUTPUT_PATH."""
    fig, ax = plt.subplots(figsize=(5, 4))
    labels = ["CPU", gpu_name]
    seconds = [cpu_seconds, gpu_seconds]
    bars = ax.bar(labels, seconds, color=["#888888", "#2563eb"])

    ax.set_ylabel("seconds")
    ax.set_title(f"{MATRIX_SIZE}x{MATRIX_SIZE} matmul: CPU vs GPU")
    for bar, value in zip(bars, seconds):
        ax.annotate(f"{value:.3f}s", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    plt.close(fig)


def stress_test(device, duration_seconds):
    """Hammer the GPU with back-to-back matmuls for `duration_seconds`,
    sampling utilization/temperature/memory the whole time via pynvml.

    Returns a list of (elapsed_seconds, util_percent, temp_c, mem_used_mb).
    """
    pynvml.nvmlInit()
    try:
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        a = torch.randn(STRESS_MATRIX_SIZE, STRESS_MATRIX_SIZE, device=device)
        b = torch.randn(STRESS_MATRIX_SIZE, STRESS_MATRIX_SIZE, device=device)

        samples = []
        iterations = 0
        start = time.perf_counter()
        last_sample = 0.0

        while True:
            a @ b
            torch.cuda.synchronize()  # keep the loop paced to real GPU work, not queued-up async calls
            iterations += 1
            elapsed = time.perf_counter() - start

            if elapsed - last_sample >= STRESS_SAMPLE_INTERVAL_SECONDS:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                samples.append((elapsed, util.gpu, temp, mem.used / (1024 ** 2)))
                last_sample = elapsed

            if elapsed >= duration_seconds:
                break

        return samples, iterations
    finally:
        pynvml.nvmlShutdown()


def plot_stress(samples, gpu_name):
    """Save a time-series chart of GPU utilization and temperature during
    the stress test to STRESS_OUTPUT_PATH."""
    elapsed = [s[0] for s in samples]
    util = [s[1] for s in samples]
    temp = [s[2] for s in samples]

    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(elapsed, util, color="#2563eb", label="utilization")
    ax1.set_xlabel("seconds")
    ax1.set_ylabel("utilization (%)", color="#2563eb")
    ax1.set_ylim(0, 100)

    ax2 = ax1.twinx()
    ax2.plot(elapsed, temp, color="#dc2626", label="temperature")
    ax2.set_ylabel("temperature (C)", color="#dc2626")

    ax1.set_title(f"GPU stress test: {gpu_name}")
    fig.tight_layout()
    fig.savefig(STRESS_OUTPUT_PATH, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stress-seconds", type=float, default=20,
        help="how long to run the FurMark-style stress test for (default: 20)",
    )
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print(
            "No GPU visible to this container. Re-run with "
            "`docker run --gpus all ...` (needs nvidia-container-toolkit "
            "on the host), or confirm a GPU was actually scheduled onto "
            "this session.",
            file=sys.stderr,
        )
        sys.exit(1)

    gpu_name = torch.cuda.get_device_name(0)

    print(f"Running a {MATRIX_SIZE}x{MATRIX_SIZE} matmul on CPU for comparison...")
    _, cpu_seconds = timed_matmul(torch.device("cpu"))

    print(f"Running the same matmul on: {gpu_name}")
    c, gpu_seconds = timed_matmul(torch.device("cuda"))

    assert c.is_cuda
    print(f"Result: device={c.device}, shape={tuple(c.shape)}, c[0, 0]={c[0, 0].item():.4f}")
    print(f"CPU: {cpu_seconds:.3f}s   GPU: {gpu_seconds:.3f}s   speedup: {cpu_seconds / gpu_seconds:.1f}x")

    plot_comparison(cpu_seconds, gpu_seconds, gpu_name)
    print(f"Saved timing chart to {OUTPUT_PATH}")

    print(f"\nRunning a {args.stress_seconds:.0f}s FurMark-style stress test "
          f"({STRESS_MATRIX_SIZE}x{STRESS_MATRIX_SIZE} matmuls back to back)...")
    samples, iterations = stress_test(torch.device("cuda"), args.stress_seconds)

    utils = [s[1] for s in samples]
    temps = [s[2] for s in samples]
    mems = [s[3] for s in samples]
    print(f"Completed {iterations} iterations in {samples[-1][0]:.1f}s")
    print(f"Utilization: avg={sum(utils) / len(utils):.0f}%  max={max(utils)}%")
    print(f"Temperature: avg={sum(temps) / len(temps):.0f}C  max={max(temps)}C")
    print(f"Memory used: max={max(mems):.0f} MiB")
    if max(temps) >= STRESS_TEMP_WARNING_C:
        print(f"WARNING: GPU reached {max(temps)}C, at or above the "
              f"{STRESS_TEMP_WARNING_C}C informational threshold. Not a "
              f"failure by itself, but worth checking cooling/airflow if "
              f"this is sustained.")

    plot_stress(samples, gpu_name)
    print(f"Saved stress test chart to {STRESS_OUTPUT_PATH}")

    print("\nGPU compute test passed.")


if __name__ == "__main__":
    main()
