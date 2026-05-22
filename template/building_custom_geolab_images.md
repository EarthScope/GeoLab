# **Building Custom GeoLab Images**

GeoLab environments run inside **Docker containers** — self-contained packages that bundle an operating system, software libraries, and Python packages together. This guide walks you through customizing a GeoLab image by editing a few plain-text configuration files, then building and deploying the result.

## **Installing Docker Desktop**

You will need to install Docker Desktop to build and run images on your computer or make them available. If you are new to Docker, images, and containers, follow the [instructions](https://docs.docker.com/get-started/introduction/) to install Desktop for your operating system. Work through the [modules]([https://docs.docker.com/get-started/introduction/\#modules](https://docs.docker.com/get-started/introduction/#modules)) to learn how to build, run, and publish images.

After installing Docker Desktop, log into Docker. This enables saving or pushing an image to Docker Hub, Docker’s image repository.

## **Installing git**

Git is used to manage code. You will need git to make a copy of the GeoLab repository which contains the template for building custom images. Follow the [instructions]([https://github.com/git-guides/install-git](https://github.com/git-guides/install-git)) to install git. If you are unfamiliar with git, you can work through a [tutorial]([https://github.com/EarthScope/GeoLab-learning-hub/blob/main/tutorials/fundamentals/1\_git\_intro.ipynb](https://github.com/EarthScope/GeoLab-learning-hub/blob/main/tutorials/fundamentals/1_git_intro.ipynb)).

### **Copying the build template**

The `template` directory in the GeoLab repository contains all the files needed to build a custom GeoLab docker image. If you have git installed, open a terminal and type the following if your operating system is macOS or Linux:

```shell
cd ~  
git clone [https://github.com/EarthScope/GeoLab.git](https://github.com/EarthScope/GeoLab.git)  
cd Geolab  
cp -rf ./template ~  
```

This set of commands does the following:

1. Change from the current directory to your home directory.  
2. Use git to copy the GeoLab repository.
3. Changes directory to Geolab.  
4. Copy the \`template\` directory to your home directory.

Your \`template\` directory should have the following files:

```shell
./template  
├── apt.txt  
├── build-custom-image.md  
├── Dockerfile  
├── environment.yml  
├── requirements.txt  
└── start  
```

## **Configuring a custom image** 

A Docker image is a snapshot of a complete computing environment. When GeoLab launches, it starts a container from that image. The Dockerfile specifies how the image is built. GeoLab uses `pangeo/base-notebook` as its starting point, which builds the image from the configuration files listed below. To create a custom image, edit the configuration files before building:

| File | What it controls |
| :---- | :---- |
| `apt.txt` | System-level software (installed via `apt`) |
| `environment.yml` | Conda packages and channels |
| `requirements.txt` | Python packages from PyPI (installed via `pip`) |
| `postBuild` | Commands to run after the build completes |
| `start.sh` | The command that launches when the container starts |

### **Installing System Software with apt**

`apt` is the Ubuntu package manager — it installs system-level tools like compilers, runtime libraries, and command-line utilities. Add any packages you need, one per line, to apt.txt. Best practice is to list packages in alphabetical order, which makes it easier to find a specific package.

**Example:** Adding Node.js and npm:

```shell
build-essential
gfortran
git
gmt-dcw
gmt-gshhg
make
nodejs
npm
```

*Tip: Only add packages here that aren't available through conda. Most scientific Python libraries are better managed in environment.yml.*

### **Installing Conda Packages**

Conda manages Python (and non-Python) packages within isolated environments. Edit `environment.yml` to add packages by name under the appropriate section. Always use the `conda-forge` channel for the broadest package availability unless otherwise specified in the package’s installation instructions

**Example:** Adding ObsPy Plus (`obsplus`) to the Geophysics section:

```
channels:
 - conda-forge
dependencies:
 ...
 # ── Geophysics ──────────────────────────────────────
 - dascore
 - gmt
 - obspy
 - pygmt
 - obsplus
 ...
```

**Tip:** Prefer conda packages over pip when a package is available in both. Conda resolves environment-wide dependencies more reliably.

### **Installing pip Packages**

Some packages are only available on PyPI (Python's package index) and must be installed with `pip`. Add them to requirements.txt, one per line. You can pin a specific version with \== to ensure reproducibility.

**Example:** Adding `gnss-lib-py`:

```shell
# --- EarthScope ---
earthscope-sdk==1.4.1
earthscope-cli==1.2.0
earthscopestraintools
gnssrefl
hypoinvpy
gnss-lib-py
```

**Tip:** Pin versions for packages critical to your workflow (e.g., `earthscope-sdk==1.4.1`). This prevents silent breakage when upstream packages release updates if you rebuild the image.

### **Running a postBuild Script**

The postBuild script runs automatically after all packages are installed. Use it for one-time setup steps that can't be expressed as package installs — for example, configuring tools, downloading data files, or logging build metadata.

**Example:** Recording the build timestamp:

```shell
#!/bash
echo "--- Running post-build triggers ---"

# Record when this image was built
date > /etc/build_timestamp
echo "Build stage completed successfully."
```

Make sure the script is executable before building. In a terminal, update the file permissions for postBuild:

```shell
chmod +x postBuild
```

### **Start Script**

`start.sh` runs when a user launches a container. Its job is to start the main process — typically JupyterLab. The \--notebook-dir parameter sets the default working directory shown in JupyterLab's file browser.

Example: Starting JupyterLab at a specific directory:

```shell
#!/sh
# Exit immediately if any command fails
set -e

jupyter lab --ip=0.0.0.0 --no-browser --notebook-dir=/path/to/your/work
```

## **Building and Pushing the Image**

Once your configuration files are ready, you build the image locally and push it to a container registry so GeoLab can access it.

Step 1 — Build the image

The `--platform linux/amd64` flag ensures the image runs on standard cloud hardware regardless of whether you're building on an Apple Silicon Mac or an Intel machine. The Dockerfile wires together your four config files. Name the image using your repository username, a descriptive name and tag to track versions, such as `username/my_project:0.1.0`.

```shell
docker build --no-cache -f Dockerfile \
 --platform linux/amd64 \
 -t username/my_project:0.1.0 .
```

Replace `username` with your Docker Hub username (or your registry path) and `0.1.0` with your version tag.What does `--no-cache` do? It forces Docker to rerun every build step from scratch, ensuring your latest apt.txt, environment.yml, and requirements.txt changes are picked up rather than reused from a previous build.

Step 2 — Push to a registry

Push the image to Docker Hub, AWS ECR, or another registry so GeoLab can pull it. If you are using Docker Desktop and have logged into your account, you can push the image to Docker Hub with this command.

```shell
docker push username/my_project:0.1.0
```

If you use AWS ECR, follow these [instructions](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html).

## **Running Your Image in GeoLab**

1. Open GeoLab.  
2. Choose **Environment → Other**.  
   ![](./images/)  
3. Enter the full image name from your registry, e.g.: [**docker.io/username/shortcourse:0.1.0**](http://docker.io/username/shortcourse:0.1.0).  
   ![](./images/)  
4. Select **Start**.

GeoLab will pull and launch your custom environment. The first launch may take a minute while the image downloads.