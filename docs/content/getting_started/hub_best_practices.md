# Best practices when using GeoLab

These tips and strategies will help keep your logins clean, avoid artifacts from previous sessions, and reduce costs by avoiding unutilized storage and computing resources.

## Personal Storage Limits

Every GeoLab user has a "home" directory where the files, scripts, notebooks, Git repos, and other files associated with their work persist from one session to the next. When using the Terminal, this directory will appear as `/home/jovyan/`. It is also the top-most directory seen in the navigation pane.

We recommend using this directory to store files and notebooks associated with _processing_ the data. However, users are encouraged to stream data and _access it directly_ from cloud storage to avoid downloading and storing copies of data on a long-term basis. Using these direct-access / data-proximate techniques will keep storage costs to a minimum and avoid managing the data yourself.

<details>
  <summary>A brief aside on why we don't like to "download" data anymore</summary>

  Hopefully, this will be an insightful but brief discussion/link to why we favor data-proximate workflows in the hub and cloud.
</details>

Please keep personal storage in the home directory to <10 GB. Your current storage size can be determined using the Resource Monitor or by typing `du -sh` from a command Terminal in your home directory.

### Other Storage Options


## Installing packages Using `pip` or `conda`

If you need to install a Python package that is not included in the GeoLab base image, you can use `pip` or `conda` to install the package yourself. Unfortunately, these packages are only valid for the current session and will not persist from one session to another.

>[!NOTE]
<!-- >Guidance for suggesting packages to add to the base image can be found in the Contributor Guide. -->
>Guidance for suggesting packages to add to the base image can be found in the [Contributor Guide](contributor_guide.ipynb)

To use a package between sessions, we recommend either of the two following strategies:
1. Install the package each time you need it either by typing the below in a Terminal window after logging in or including it in the first cell of your Jupyter notebook
  - `%pip install packagename` or `%conda install packagename`
  - The `%pip` / `%conda` forms here are better than their `!pip` / `!conda` counterparts to ensure that the package is installed in the correct directory

1. Create your own image that can be loaded from the login page and includes the package(s) needed.


## Using Custom Images at Startup

When selecting a server size, a default environment defined by the GeoLab base image is provided. This includes many Python packages and programs commonly used for geoscience data analysis.

However, you can load a different image for your base environment if you prefer other apps and capabilities. At the server selection screen, click the dropdown menu for the image and select `Other...` In the text box labeled "Custom Image," provide the URL for the image address you would like to use.

Please see our How-To article on developing, archiving, and maintaining a custom image and environment for further instructions.