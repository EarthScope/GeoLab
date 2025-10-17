# Environment Management
GeoLab images have many well-loved geophysics tools installed, but we cannot include everything. Additional software and packages can be installed by users in GeoLab, with two options:
1. Ephemeral Installation: Due to the ephemeral nature of the JupyterHub servers, packages installed on the server will only be valid for your current session and will not persist from one session to another. You will need to reinstall them each time you log back in to GeoLab. 
2. Use a Custom Image: If you need to use the same software repeatedly, during multiple sessions, or for multiple users, you can create your own software environment and load it at launch time.  

## 1. Ephemeral Installation
### Installing python packages
 Use `pip` or `conda` to install the package yourself at the beginning of your session, either by typing the below in a GeoLab Terminal, or including it in the first cell of your Jupyter notebook.
  - `%pip install packagename` or `%conda install packagename`
    - The `%pip` / `%conda` forms here are better than their `!pip` / `!conda` counterparts to ensure that the package is installed to the correct directory.

### Installing ubuntu packages
Some software can be installed via the terminal using `apt-get`. Please be advised that users do not have the ability to run commands as super users: `sudo` will not work and these permissions _cannot_ be granted to individual users. If you need to install something foundational, please create a custom image.

## 2. Create a Custom Image:
```{note} Section Under Development!
EarthScope is working to build more comprehensive documentation. In the mean time, please see the [2i2c guide on building your own image from a template.](https://docs.2i2c.org/admin/howto/environment/update-community-image/). We recommend starting with an image from [Pangeo.](https://github.com/pangeo-data/pangeo-docker-images)
```

## A note on C/C++/Fortran Compilers:
Most GeoLab images have `gcc`, `g++`, and `gfortran` compilers installed. You will need to move your makefiles into your home directory and compile them within GeoLab. 
