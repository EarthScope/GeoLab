# Building the GeoLab "slim" image

The GeoLab slim image is a base image containing minimal software for working in the platform.

GeoLab environments run as **containers** based on **images** — self-contained packages that include an operating system, software libraries, and Python packages together. This guide documents the steps using Docker to create the geolab-slim image.

GeoLab images use the `pangeo/base-notebook` image as the starting point. This base image contains the fundamentals needed for an environment in JupyterHub. You customize it by editing four files before building:

| File | What it controls |
| :--- | :--------------- |
| `apt.txt` | System-level software (installed via `apt`) |
| `environment.yml` | Conda packages and channels |
| `requirements.txt` | Python packages from PyPI (installed via `pip`) |
| `start` | The command that launches when the container starts |

---

## Installing System Software with apt

`apt` is the Ubuntu package manager — it installs system-level tools like compilers, runtime libraries, and command-line utilities. Add any packages you need, one per line, to `apt.txt`.

> **Tip:** Only add packages here that aren't available through conda. Most scientific Python libraries are better managed in `environment.yml`.

---

## Installing Conda Packages

Conda manages Python (and non-Python) packages within isolated environments. Edit `environment.yml` to add packages by name under the appropriate section. Always use the `conda-forge` channel for the broadest package availability.

> **Tip:** Prefer conda packages over pip when a package is available in both. Conda resolves environment-wide dependencies more reliably.

---

## Installing pip Packages

Some packages are only available on PyPI (Python's package index) and must be installed with `pip`. Add them to `requirements.txt`, one per line. You can pin a specific version with `==` to ensure reproducibility.

> **Tip:** Pin versions for packages critical to your workflow (e.g., `earthscope-sdk==1.4.1`). This prevents silent breakage when upstream packages release updates.

---

## Start Script

`start` runs when a user launches a container. Its job is to start the main process — typically JupyterLab.
For this image the contents simply executes the command provided by the Hub.

---

## Building and Pushing the Image

Once your configuration files are ready, you build the image locally and push it to a container registry so GeoLab can access it.

**Step 1 — Build the image**

The `--platform linux/amd64` flag ensures the image runs on standard cloud hardware regardless of whether you're building on an Apple Silicon or an Intel machine. `Dockerfile` is the GeoLab-specific Dockerfile that wires together your four config files.

```bash
docker build --no-cache -f Dockerfile \
  --platform linux/amd64 \
  -t username/geolab-slim:latest-amd64 .
```

Replace `username` with your Docker Hub username (or your registry path) and `latest-amd64` with your version tag of choice.

> **What does `--no-cache` do?** It forces Docker to re-run every build step from scratch, ensuring your latest `apt.txt`, `environment.yml`, and `requirements.txt` changes are picked up rather than reused from a previous build.

**Step 2 — Push to a registry**

Push the finished image to Docker Hub, AWS ECR, or another registry so GeoLab can pull it:

```bash
docker push username/geolab-slim:latest-amd64
```

> **First time?** You'll need to log in first with `docker login` (Docker Hub) or the appropriate CLI for your registry.

---

## Running Your Image in GeoLab

1. Open GeoLab.
2. Choose **Environment → Other**.

   ![Choose Environment](./images/choose_environment.png)

3. Enter the full image name from your registry, e.g.:
   ```
   username/geolab-slim:latest-amd64
   ```

   ![Enter image name](./images/custom_image.png)

4. Select **Start**.

GeoLab will pull and launch your custom environment. The first launch may take a minute while the image downloads.

## Final steps

If the image works as desired create a PR against the `main` branch for review by the ownership team.
Once accepted the production image will be built and deployed automatically in the EarthScope AWS container registry.

## Local build and test

An image built for your machine can be created using:

```bash
docker build --no-cache -f Dockerfile -t geolab-slim:test .
```

> **Not for GeoLab!** Without the guarantee of `--platform linux/amd64` this image is not for GeoLab

Run a container using this image with:

```bash
docker run --rm -p 8888:8888 geolab-slim:test
```

Then use a web browser to connect to: `http://127.0.0.1:8888/lab`,
open `smoke_tests.ipynb` and run all cells.
