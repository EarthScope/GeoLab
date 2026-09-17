# Building Custom GeoLab Images

GeoLab environments run as **containers** based on **images** — self-contained packages that include an operating system, software libraries, Python packages, and more. This guide documents the steps using Docker and git to create such an image.

Steps:

- [Installing and logging into Docker](#installing-and-logging-into-docker)
- [Installing git](#installing-git)
- [Copy the base template](#copy-the-base-template)
- [Configuring a custom image](#configuring-a-custom-image)
  - [Installing system software with apt](#installing-system-software-with-apt)
  - [Installing Conda packages](#installing-conda-packages)
  - [Installing pip packages](#installing-pip-packages)
  - [Creating a postBuild script](#creating-a-postbuild-script)
- [Building and testing the image locally](#building-and-testing-the-image-locally)
  - [Building the local testing image](#building-the-local-testing-image)
  - [Running the local testing image](#running-the-local-testing-image)
  - [Verifying the installed packages](#verifying-the-installed-packages)
- [Building and publishing the image](#building-and-publishing-the-image)
  - [Setting the version and updating the changelog](#setting-the-version-and-updating-the-changelog)
  - [Building the platform image](#building-the-platform-image)
  - [Publishing the platform image](#publishing-the-platform-image)
- [Running your published image in GeoLab](#running-your-published-image-in-geolab)

> [!NOTE]
> These instructions are written for macOS, Linux and similar systems. While the same steps can be executed in Windows the details will vary.

---

## Installing and logging into Docker

Docker Desktop is the recommended option to build and run images on your computer and to publish them for access by others (and GeoLab itself). Follow the [instructions](https://docs.docker.com/get-started/introduction/) to install it. If you are new to Docker, images, and containers, we recommend working through the [getting-started modules](https://docs.docker.com/get-started/introduction/#modules) to learn how to build, run, and publish images.

> [!TIP]
> Alternatively, Docker Engine (with build plugins) can be used; this is what is often installed on Linux systems.

After starting Docker Desktop, log into Docker, creating an account if needed. This enables pushing (aka publishing) an image to Docker Hub, Docker’s image repository where it is available to others.

> [!TIP]
> Docker Hub is just one of many repositories for images, many others exist and can be used, but Docker Hub is easiest because it is the default repository for components in the ecosystem, including in GeoLab.

---

## Installing git

Git is needed to make a copy of the GeoLab repository containing the template for the base image for building custom images. The git program is often already installed, or easily installed on macOS and Linux systems.  Follow the [instructions](https://github.com/git-guides/install-git) to check for and install git if needed.

---

## Copy the base template

The `geolab-base` directory in the GeoLab repository contains all the files needed to build a custom GeoLab image.  Open a terminal and execute the following commands:

```shell
cd ~
git clone --depth 1 https://github.com/EarthScope/GeoLab.git
cp -R GeoLab/geolab-base my-geolab-image
cd my-geolab-image
```

This set of commands does the following:

1. Change from the current directory to your home directory.
2. Use git to copy the GeoLab repository, only getting the current state (`--depth 1`)
3. Copy the geolab-base directory to a new directory in your home directory.
4. Change into the newly created directory with a copy of the image template files.

Your `my-geolab-image` directory should have the following files:

```shell
./my-geolab-image
├── apt.txt
├── README.md
├── Dockerfile
├── environment.yml
├── requirements.txt
├── start
├── test_helpers.py
├── test_notebook.ipynb
└── ...
```

> [!TIP]
> For image development it is recommended to keep your files in a git repository to track changes, share with others, etc.  The sooner this is started the better.  This is the right stage to commit these starting files to a new repo.

---

## Configuring a custom image

A container image is a snapshot of a complete computing environment. When GeoLab launches, it starts a container from such an image.  The `geolab-base` image is based on a Pangeo image (`pangeo/base-image`) as its starting point.  A custom image can be created by modifying the build of this image.

The `Dockerfile` specifies how the image is built. To create a custom image, edit the configuration files before building:


| File               | What it controls                                             |
| ------------------ | ------------------------------------------------------------ |
| `apt.txt`          | System-level software (installed via `apt`)                  |
| `environment.yml`  | Python from Conda packages and channels                      |
| `requirements.txt` | Python packages from PyPI (installed via `pip`)              |
| `postBuild`        | Commands to run after the build completes (create if needed) |
| `start`            | Entrypoint script; normally leave unchanged                  |


### Installing system software with apt

`apt` is the Ubuntu package manager — it installs system-level tools like compilers, runtime libraries, and command-line utilities. Edit `apt.txt` to add any packages you need, one per line. Best practice is to list packages in alphabetical order, which makes it easier to find a specific package.

**Example:** Adding Node.js (nodejs) and npm to `apt.txt`:

```shell
build-essential
gfortran
git
gmt-dcw
gmt-gshhg
make
nodejs  <-- NEW
npm     <-- NEW
```

> [!TIP]
> Only add packages here that aren't available through conda. Most scientific Python libraries are better managed in environment.yml.

### Installing Conda packages

Conda manages Python (and non-Python) packages within isolated environments. Edit `environment.yml` to add packages by name under the appropriate section (the sections are comments, not important for conda). Always use the `conda-forge` channel for the broadest package availability unless otherwise specified in the package’s installation instructions.

**Example:** Adding SimPEG (`simpeg`) to the Geophysics section of `environment.yml`:

```yaml
...
dependencies:
  ...
 # ── Geophysics ──────────────────────────────────────
  - dascore
  - obspy
  - obsplus
  - gmt
  - pygmt
  - simpeg  <-- NEW
 ...
```

> [!TIP]
> Prefer conda packages over pip when a package is available in both. Conda resolves environment-wide dependencies more reliably.

### Installing pip packages

Some packages are only available on PyPI (Python's package index) and can be installed with `pip`. Add them to `requirements.txt`, one per line. You can pin a specific version with `==` to ensure reproducibility.

**Example:** Adding `gnss-lib-py`:

```shell
# --- EarthScope ---
earthscope-sdk==1.6.1
earthscope-cli==1.2.0
earthscopestraintools
gnss-lib-py  <-- NEW
```

> [!TIP]
> Pin versions for packages critical to your workflow (e.g., `earthscope-sdk==1.6.1`). This prevents silent breakage when upstream packages release updates if you rebuild the image.

### Creating a postBuild script

A postBuild script runs automatically after all packages are installed. Use it for one-time setup steps that can't be expressed as package installs — for example, configuring tools, downloading data files, or logging build metadata.

**Example:** Create a `postBuild` file to record the build timestamp:

```shell
#!/bin/bash
set -euo pipefail  # fail fast: on command error, unset variable, or any pipeline stage failing

echo "--- Running post-build commands ---"

# Record when this image was built
date > ${CONDA_DIR}/etc/build_timestamp

echo "Build stage completed successfully."
```

---

## Building and testing the image locally

Building and testing the image locally is the fastest way to iterate on changes and fix issues.  Services that are only available in GeoLab such as direct access to repositories in S3 storage cannot be tested locally.

### Building the local testing image

```shell
docker build -f Dockerfile --tag my-geolab-image:0.1.0 .
```

You may omit the `:0.1.0` part of the tag if you wish.

> [!TIP]
> Do not publish and try to run this image in GeoLab, it may not be the correct platform.  See the next section for instructions to build the platform image.

### Running the local testing image

Use Docker to run the image with this command:

```shell
docker run --rm -p 8888:8888 my-geolab-image:0.1.0
```

Copy the URL from the log that looks like: `http://127.0.0.1:8888/lab?token...` (with the token value) and connect to the container with a web browser.

What is the docker run command doing?  The `--rm` flag will delete the container created from the image after the run completes, keeping repeated commands from creating a new container on each run.  The `-p 8888:8888` option maps the network port for the service in the container so the local computer can reach it.

> [!TIP]
> This image is not running in the GeoLab platform, so any features only available in GeoLab will not work from this local environment.

### Verifying the installed packages

The image includes `test_notebook.ipynb`, which ensures installed packages import and run. It is copied into the container at build time, so it is available in the running container. Use it after a build to confirm nothing is broken (a missing system library or version conflict often installs cleanly but fails at import). Adjust as needed for the packages that you added or removed from the build.

The notebook's checks are built on top of `test_helpers.py`, a small module of test helpers (also copied into the container) that the notebook imports rather than duplicating this logic in every cell:

| Function | Use for | What it does |
| --- | --- | --- |
| `py(modname, alias=None, smoke=None)` | Python packages | Imports `modname` and, if given, calls `smoke(mod)` as a minimal sanity check (e.g. constructing an object or calling a function). Records a pass with the package's `__version__`, or a fail with the exception. |
| `cli(cmd, version_flag='--version')` | Command-line tools | Confirms `cmd` is on `$PATH` and responds to `version_flag`. Records a pass with the version string, or a fail if it's missing. |

Each call appends a `(name, status, version, error)` row to the shared `RESULTS` list, which the notebook's final cell renders as a summary table.

In the Jupyter interface at `http://127.0.0.1:8888/lab...`, open `test_notebook.ipynb` and run all cells (Run → Run All Cells). The notebook is organized into one section per category in `environment.yml`/`requirements.txt` (Cloud & storage, Geospatial, Core scientific stack, etc.), each running `py()`/`cli()` checks for the packages in that category, and ends with a summary table listing the status (and version) of each package, with failures highlighted in red.

**Adding a test for a new package.** If you add a package to `environment.yml` or `requirements.txt`, add a matching check to `test_notebook.ipynb` so it's covered by the summary table. Pick the section that matches where you added the package (or add a new section), and add a `py()` or `cli()` call.

For example, adding `seisfetch` (a Python package) to the Geo / geoscience section:

```python
py('dascore')
cli('gmt', version_flag='--version')
py('obspy',
   smoke=lambda m: m.UTCDateTime('2020-01-01').timestamp)
py('obsplus')
py('pygmt')
py('seisfetch',
   smoke=lambda m: m.Client())  # replace with a minimal, side-effect-free call
```

The `smoke` argument is optional but recommended — a bare import can succeed even when the package is broken in ways that only show up on first use (e.g. a missing compiled extension). Pick a call that exercises the package without hitting the network or requiring credentials, since the notebook may run without EarthScope services available locally.

> [!TIP]
> A failure here points at the package, not your notebook code — usually a missing system dependency (add it to `apt.txt`) or a version conflict between conda and pip packages. If you add or remove a package in `environment.yml` or `requirements.txt`, update the notebook to match.

---

## Building and publishing the image

Once your configuration files are ready, you build the image locally *for the GeoLab platform* and push it to a container registry so GeoLab can access it.

### Building the platform image

The `--platform linux/amd64` flag ensures the image runs on the same platform as GeoLab regardless of your own computer architecture.  Name the image using your repository username, a descriptive name and tag to track versions, such as `username/my-geolab-image:0.1.0`.

```shell
docker build --no-cache -f Dockerfile \
 --platform linux/amd64 \
 --build-arg IMAGE_TITLE=my-geolab-image \
 --build-arg IMAGE_AUTHORS=you@university.edu \
 --tag username/my-geolab-image:0.1.0 .
```

> [TIP]
> When building an image, setting a version in the image tag is a best practice. Versioning can track image changes to allow reproducibility. If a version tag, e.g. 0.1.0, Docker will automatically tag the image as `latest`.

Replace `username` with your Docker Hub username (or your registry path), `my-geolab-image` with your image name, and `0.1.0` with your version tag. The `--build-arg` values for `IMAGE_TITLE` and `IMAGE_AUTHORS` are optional but recommended for image metadata; image tag versions should be added to a `CHANGELOG.md` file which list the changes associated to that version.

`--no-cache` forces Docker to rerun build steps from scratch, ensuring a clean build when publishing.

> [!NOTE]
> Images will be cached by different systems, including the image repository and GeoLab.  If you are using a version (e.g. `0.1.0`) you should increment it for each build to avoid inadvertently using cached copies.

### Publishing the platform image

Push the image to Docker Hub, AWS ECR, or another registry so GeoLab can access it. If you have logged into your Docker account, you can push the image to Docker Hub with this command:

```shell
docker push username/my-geolab-image:0.1.0
```

Replace the details to match the --tag value in the build command.

> [!TIP]
> If the push results in an error, make sure you are logged into Docker Hub using `docker login` if needed.

Many other image repositories exist. If you use AWS ECR, follow these [instructions](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).

---

## Running your published image in GeoLab

1. Open [GeoLab's Hub Control Panel](https://geolab.earthscope.cloud/hub/home/)
  * Login with your [EarthScope account](https://www.earthscope.org/user/login)
  * If "Stop My Server" button is visible, select it to stop your current server
  * Select "Start My Server" button
2. Choose **Environment → Other**
3. In **Custom image** enter the image name from your registry, e.g.: `username/my-geolab-image:0.1.0` (for Docker Hub)
4. Select **Start**

> [!TIP]
> If the image is not in Docker Hub, the **Custom image** value should be the full image reference.

GeoLab will pull and launch your custom environment. The first launch may take a bit longer while the image is transferred from the repository.
