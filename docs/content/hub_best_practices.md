# Best practices when using GeoLab

A few things to keep in mind as you develop a workflow based around GeoLab. Adopting these tips and strategies will help keep your logins clean while avoiding artifacts from previous sessions and save money by avoiding unutilized storage and compute resources.

## Stopping Your Server and Logging Out

In order to save money, it is important to release the resources that you have claimed during the session by shutting down your server instance and logging out of your EarthScope account once you're finished. This allows the hub to re-allocate those resources to other users and saves money by not charging for unused compute.

The full shutdown sequence is as follows:

1. Navigate to `File` --> `Hub Control Panel`
  - This will create a separate browser tab
1. In the new tab, push the big red button that looks like this ![image](./img/bigredbutton.png)
1. Once the button disappears, your server instance will be stopped.

> [!NOTE]
> If you are using a "Shared Small" instance for your session, this will _not_ shutdown the server for other users.

1. Next, click `Log Out`
1. Finally, close all browser tabs for GeoLab before logging in again.

If you follow these steps, you will avoid any errors that might appear if you try to start GeoLab from the same browser tab.

## Personal Storage Limits

Every GeoLab user has a "home" directory where the files, scripts, notebooks, Git repos, and any other files associated with their work will persist from one session to the next. This directory will appear as `/home/jovyan/` when using the Terminal. This is also the top-most directory seen in the navigation pane.

We recommend using this directory to store files and notebooks associated with _processing_ the data. However, users are encouraged to stream data and _access it directly_ from cloud storage as much as possible to avoid downloading and storing a copy of the data in this directory on a long-term basis. Using these direct-access / data-proximate techniques will help keep storage costs to a minimum and avoid having to manage the data yourself.

<details>
  <summary>A brief aside on why we don't like to "download" data anymore</summary>

  Hopefully an insightful, but relatively brief, discussion/links to why we favor data-proximate workflows in the hub and cloud.
</details>

Please keep personal storage in the home directory to <10 Gb. Your current storage size can be determined by using the Resource Monitor or by typing `du -sh` from a command Terminal in your home directory.

### Other Storage Options


## Installing packages Using `pip` or `conda`

If you find the need to install a Python package that is not included in the GeoLab base image, you can use either `pip` or `conda` to install the package yourself. Unfortunately, these packages will only be valid for the current session and will not persist from one session to another.

>[!NOTE]
<!-- >Guidance for suggesting packages to add to the base image can be found in the Contributor Guide. -->
>Guidance for suggesting packages to add to the base image can be found in the [Contributor Guide](contributor_guide.ipynb)

To use a package between sessions, we recommend either of the two following strategies:
1. Install the package each time you need it either by typing the below in a Terminal window after logging in, or including it in the first cell of your Jupyter notebook
  - `%pip install packagename` or `%conda install packagename`
    - The `%pip` / `%conda` forms here are better than their `!pip` / `!conda` counterparts to ensure that the package is installed to the right directory

1. Create your own image that can be loaded from the login page that includes the package(s) that are needed.


## Using Custom Images at Startup

When selecting your server size, you are provided with a default environment defined by the GeoLab base image. This includes many Python packages and programs that are commonly used for geoscience data analysis.

However, you have the option of loading a different image for your base environment if you have a preference for other apps and capabilities. At the server selection screen, click the dropdown menu for the image, and select `Other...` In the text box labeled "Custom Image", provide the URL for the image address you would like to use.

Further instructions for developing, archiving, and maintaining a custom image and environment, please see our How-To article on the topic.