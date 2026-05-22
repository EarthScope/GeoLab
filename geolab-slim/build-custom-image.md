# Building Custom GeoLab Images

GeoLab uses the `pangeo/base-notebook` for the base image. The image uses the Docker ONBUILD directive to install software, python packages, postbuild scripts, and a start script.

## Installing software with apt

To install software add the apt packages in the `apt.txt` file. For example, to add nodejs and npm to the image edit the apt.txt file.

```txt
git
build-essential
gfortran
make
gmt-dcw
gmt-gshhg
nodejs <---
npm <---
```

## Installing conda packages

To install conda packages edit the environment.yml file by adding the package names. For example, add obsplus to the Geophysics section.

```yml
channels:
  - conda-forge
dependencies:
  ...
  # ── Geophysics ──────────────────────────────────────
  - dascore
  - gmt
  - obspy
  - pygmt
  - obsplus <---
  ...
  ```

## Install pip packages

To install packages from PyPI with pip, add the packages by editing the requirements.txt file. For example, to install gnss-lib-py edit the file to add it.

```txt
# --- EarthScope ---
earthscope-sdk==1.4.1
earthscope-cli==1.2.0
earthscopestraintools
gnssrefl
hypoinvpy
gnss-lib-py <---
```
## Run a postBuild script

The postBuild script runs after the build is completed. Examples of postbuild scripts are configuring applications or adding information to the build. For example:

```bash
#!/bin/bash
echo "--- Running post-build triggers ---"
# Example: Cleanup temporary build files or log the build time
date > /etc/build_timestamp
echo "Build stage completed successfully."
```

## Start script

The start script executes a command to start a process such as starting jupyter lab. To start Jupyter lab and open a notebook create a `start.sh` script with the --notebook-dir parameter.

```bash
#!/bin/sh
# Fail on any error
set -e 

jupyter lab--ip=0.0.0.0" "--no-browser" --notebook-dir=/path/to/your/work
```

## Build and push to repository

To build the image for amd64, note that Dockerfile4 builds this image and uses the environment.yml, apt.txt, requirements.txt and start file.

```bash
docker build  --no-cache -f Dockerfile4 \
--platform linux/amd64 \
-t username/geolab-slim:0.4.5-amd64  .
```

Push to Docker Hub, AWS ECR, or other image repository to make the image available to GeoLab.

```bash
docker push username/geolab-slim:0.4.5-amd64
```

## Run image in GeoLab

1. Open GeoLab.
2. Choose Environment > Other

![Choose Environment](./images/choose_environment.png)

3. Enter the image name from the repository, e.g., username/geolab-slim:0.4.5-amd64

![Enter image name](./images/custom_image.png)

4. Select Start