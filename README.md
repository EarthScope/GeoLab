
# EarthScope GeoLab Docker Images

The images defined in this repository are reproducible computing environments developed for use by [EarthScope's Geolab JupyterHub](https://www.earthscope.org/data/geolab/). They build on top of the Ubuntu operating system and include [conda environments](https://conda.io/projects/conda) with a curated set of Python packages for geophysical data analysis. 

More details can be found in [our documentation](https://docs.earthscope.org).

Images are hosted on [AWS ECR](https://gallery.ecr.aws/earthscope-dev)

| Image           | Description                                   |
|-----------------|-----------------------------------------------|
| geolab-default      | Foundational Dockerfile for builds. Includes earthscope authentication tools and foundational geophysics tools, inheriting base content from the [Pangeo Pytorch image](https://github.com/pangeo-data/pangeo-docker-images/tree/master)          |
| mspass_shortcourse | Image containing the [MsPASS software](https://www.mspass.org/), built for the [MsPASS Technical ShortCourse](https://www.earthscope.org/event/using-mspass-for-data-processing-on-hpc-and-cloud-systems/)|
| mt_shortcourse | Image developed for the [MagnetoTellurics ShortCourse](https://www.earthscope.org/event/2024-short-course-magnetotelluric-instrumentation-and-data-processing/) |
