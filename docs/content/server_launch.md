# Launching your Server

## Select an Instance Size
The Server Options page lets you select a computing environment tailored to your needs, ensuring you have the right resources for your projects.
![Server](img/Server.png)
When selecting a server for your JupyterHub environment, it's important to choose a server instance that meets your computational needs without overcommitting resources. Below are the available server options along with their specifications and recommended use cases.

In order to keep oeprational costs low, we recommend that you start with the smallest server option available, and only move to a larger instance when you hit performance barriers.

```{dropdown} Shared Small Server
The Shared Small server is a multi-user environment where resources may be shared among up to four different users. This is the recommended option for most users, especially for those starting out or working on less intensive tasks.
Server Specifications:

Use Cases:
  - Initial development and testing
  - Educational purposes
  - Light to moderate data analysis
```

```{dropdown} Small Server (Dedicated)
The **Small server** is a dedicated environment just for you. This option is suitable for users who need more computational power and memory for their projects. It ensures that you have consistent access to the allocated resources without competition from other users.
Server Specifications:
Use Cases:
  - More intensive data analysis and processing
  - Running medium-sized machine learning models
  - Projects requiring higher memory capacity
```

```{dropdown} Medium and Large Servers
Medium and Large servers are available by request, on a case-by-case basis. To request a larger server for your project, please email data-help@earthscope.org.
```

## Select an Image
Several pre-configured compute environments are available to choose from. Use the dropdowns below to select your initial configuration. Please see Envrionment Management[environment_management] for more details on customizing your ephemeral server instance after launch, or bringing your own custom image.

```{dropdown} GeoLab
The default GeoLab image contains a variety of python packages to enable a broad range of geophyiscal data analysis.
This image inherits all software in pangeo/pytorch_notebook, and includes additional support for EarthScope SDK/CLI and other geophysics tools. For a complete list of packages included in this image, see [github software list].

Note: If you believe we've missed a well-loved geophysical data analysis tool, please let us know by filling out the Geolab Feedback Form[geolab_feedback_form]!
```

```{dropdown} R Studio
The R image is a stock image provided by 2i2c. EarthScope does not currently provide support or geophysical packages for this image.
```

```{dropdown} Short Course Images
EarthScope supports several educational short courses and workshops hosted in GeoLab throughout the year. If you are using GeoLab as part of one of these workshops, select the image corresponding to your course.

Short Course Images are available on a temporary basis only and contain software configurations specific to the course; they are not intended for public use and should not be used for ongoing research or external projects.

To learn more about EarthScope's educational short course offerings, visit [link]
```

```{dropdown} Other - Bring Your Own Image

GeoLab is compatible with many other custom compute environments that are configured to run in JupyterHub.

Custom images must be built docker containers that are available in a public image repository (e.g., aws ECR, ACR, dockerhub, quay.io)

Select 'Other' from the dropdown menu and specify the public URL of the container.

See Environment Management[environment_management.md] for more details on building your own image.
```

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