
# EarthScope GeoLab Docker Images

The images defined in this repository are reproducible computing environments developed for use in [EarthScope's Geolab JupyterHub](https://www.earthscope.org/data/geolab/). They build on top of the Ubuntu operating system and include [conda environments](https://conda.io/projects/conda) with a curated set of Python packages for geophysical data analyses.

More details on GeoLab can be found in [our documentation](https://docs.earthscope.org/geolab).

Images are hosted on [AWS ECR](https://gallery.ecr.aws/earthscope-dev)

| Image           | Description                                   |
|-----------------|-----------------------------------------------|
| geolab-base     | Base image for GeoLab. Includes EarthScope tools, common geophysics tools, and rich Jupyter Lab widget tools, based on the Pangeo base image.  See the [Instructions](https://github.com/EarthScope/GeoLab/blob/main/geolab-base/README.md) for using this as a template to build custom images.|
| geolab-gpu      | GPU-enabled flavor of geolab-base. Adds CUDA-build PyTorch, seismic machine learning (seisbench), and general ML/GPU tooling. See the [Instructions](https://github.com/EarthScope/GeoLab/blob/main/geolab-gpu/README.md) for details on what's different from geolab-base.|
| geolab-gpu2     | Builds on geolab-gpu. Adds a seismic phase-association and location toolkit (PyOcto, GaMMA, Pyrocko, REAL, NonLinLoc, HypoDD). See the [Instructions](https://github.com/EarthScope/GeoLab/blob/main/geolab-gpu2/README.md) for details on what's different from geolab-gpu.|
