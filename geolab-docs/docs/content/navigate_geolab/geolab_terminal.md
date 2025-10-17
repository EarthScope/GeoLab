# Using the Terminal in GeoLab

## Familiar `shell`

Users will often need to use an interactive shell type to organize files on their home directory, install software that might not be included in the base GeoLab image, clone repositories into their environment using git, or develop a shell-scripting data analysis workflow.

GeoLab provides easy access to the Terminal window to accomplish all of these tasks.

## How to Open a Terminal

If you want to open Terminal immediately after logging into GeoLab, then you can use the `Launcher` window that opens by default in your workspace - a quick link to the Terminal app is provided in the bottom left corner, under the "Other" section. Click on the "Terminal" tile to launch.

![image](../img/terminal_tile.png)

If you ever lose the `Launcher` window while working in GeoLab, you can always open a new one by clicking on the blue "+" button at the upper left section of the `File Browser` panel.

![image](../img/launcher_button.png)

By default, GeoLab uses the Bourne Again Shell `bash`. Once the Terminal is launched, you can use the command line just as you would in any other Unix-like Terminal.

## User `jovyan` and Root Privileges

As is [customary with the Jupyter community](https://docs.jupyter.org/en/latest/community/content-community.html#what-is-a-jovyan), the `home` directory path for each user is listed as `/home/jovyan` in the Terminal window. This is mostly just a labeling convention - your unique identity tied to your email or Google/Cilogon profile is preserved by JupyterHub and the GeoLab administrators.

If you are interested in more details about the `jovyan` user and how to use this user id to develop custom images, please see the environment management section.

As a generic user id, the `jovyan` user does not have a password associated with it. As a practical matter, this means that GeoLab users cannot use the `sudo` command to override system commands.