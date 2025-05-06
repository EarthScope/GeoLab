# How to manage your GeoLab hub environment

## Installing packages Using `pip` or `conda`

If you find the need to install a Python package that is not included in the GeoLab base image, you can use either `pip` or `conda` to install the package yourself. Due to the ephemeral nature of the JupyterHub servers, these packages will only be valid for the current session and will not persist from one session to another.

>[!NOTE]
<!-- >Guidance for suggesting packages to add to the base image can be found in the Contributor Guide. -->
>Guidance for suggesting packages to add to the base image can be found in the [Contributor Guide](../contributor_guide.ipynb)

To use a package between sessions, we recommend either of the two following strategies:
1. Install the package each time you need it: either by typing the below in a Terminal window after logging in, or including it in the first cell of your Jupyter notebook
  - `%pip install packagename` or `%conda install packagename`
    - The `%pip` / `%conda` forms here are better than their `!pip` / `!conda` counterparts to ensure that the package is installed to the right directory

2. Create your own image that can be loaded from the server startup page that includes the package(s) that are needed.

## Creating a custom image:
