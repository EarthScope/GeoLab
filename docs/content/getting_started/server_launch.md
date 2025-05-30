# Launching your Server

## Select an Instance Size
The Server Options page presents computing environments tailored to your computing requirements to ensure sufficient resources for your projects.

![Server](../img/Server.png)

Choose a server instance that meets your computational needs without overcommitting resources. We recommend starting with the smallest server option available to keep operational costs low. Only use a larger instance when it is no longer performant. Below are the available server options, along with their specifications and recommended use cases.

```{dropdown} Shared Small Server
The Shared Small server is a multi-user environment where up to four users may be on the same machine. Resources are allocated according to respective workloads. This is the most efficient compute configuration and is recommended for most users, especially those starting out or working on less intensive tasks.  

Use Cases:
  - Initial development and testing
  - Educational purposes
  - Light to moderate data analysis
```

```{dropdown} Small Server (Dedicated)
The Small server is a dedicated machine for a single user. This option is suitable for projects requiring more computational power and memory. It provides consistent access to resources without competition from other users.

Use Cases:
  - More intensive data analysis and processing
  - Running medium-sized machine learning models
  - Projects requiring higher memory capacity
```

```{dropdown} Medium and Large Servers
Medium and Large servers for computationally intensive projects are available by request on a case-by-case basis. To request a larger server for your project, please email data-help@earthscope.org.
```

## Select an Image
Several pre-configured compute environments are available. Use the dropdowns below to select your initial configuration. Please see [Envrionment Management](../advanced_topics/env_mgmt.md) for more details on customizing your instance after launch or bringing your custom image.

```{dropdown} GeoLab
The default GeoLab image contains a variety of Python packages to enable a broad range of geophysical data analysis.

This image inherits all software in pangeo/pytorch_notebook and includes additional support for EarthScope SDK/CLI and other geophysics tools. For a complete list of packages included in this image, see the GeoLab [github](geolab_github_url).

Note: If you've missed a well-loved geophysical data analysis tool, please let us know by filling out the [Geolab Feedback Form](geolab_feedback_form)!
```

```{dropdown} R Studio
The RStudio image is a stock image provided by 2i2c. EarthScope does not currently provide support or geophysical package extensions for this image.
```

```{dropdown} Short Course Images
EarthScope supports short courses and workshops hosted in GeoLab throughout the year. If you use GeoLab as part of one of these workshops, select the image corresponding to your course.

Short Course Images are available temporarily only and contain software configurations specific to the course; they are not intended for public use and should not be used for ongoing research or external projects.

Sometimes, short courses use a custom image that is unavailable in the dropdown. See Other—Bring Your Own Image below.

You can learn more about EarthScope's educational short course offerings [here.](https://www.earthscope.org/education/skill-building-learning/courses/)
```

```{dropdown} Other - Bring Your Image

GeoLab is compatible with other custom compute environments configured to run in JupyterHub.

Custom images must be Docker containers available in a public image repository (e.g., aws ECR, ACR, DockerHub, quay.io)

Select 'Other' from the dropdown menu and specify the public URL of the container.

For more details on building your own image, see [Environment Management](../advanced_topics/env_mgmt.md).
```

## Stopping Your Server and Logging Out

Release the resources used in your session for improved cost and operational efficiency. When finished, shut down your server instance and log out of your EarthScope account. The hub will reallocate resources to other users and reduce costs by eliminating unused computing.

The complete shutdown sequence is as follows:

1. Navigate to `File` --> `Hub Control Panel` (this opens a new browser tab)
1. In the new tab, push the big red button ![image](../img/bigredbutton.png)
1. Once the button disappears, the server instance has stopped.

```{note}
If you are using a "Shared Small" instance for your session, this will _not_ shutdown the server for other users.
```

1. Next, select `Log Out`
1. Finally, close all browser tabs for GeoLab before logging in again.

By following these steps, you will avoid any errors that might appear when starting GeoLab from the same browser tab.