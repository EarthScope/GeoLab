# Navigating GeoLab and its File System

GeoLab looks and feels like a familiar IDE. Here's a quick tour:

![Landing](../img/geolab_nav.png)

## Main Panel:
The Main Panel is home to the Launcher, where you can launch all of GeoLab's connected apps. You can open new Python notebooks, terminal consoles, and text/markdown files from here. 

You can always open the launcher with the blue + button on the top left by navigating to `File` -> `New Launcher` or opening a new tab in the main panel. 

## Sidebar
The sidebar contains several tabs to help you navigate the GeoLab environment and its extensions. Some images may contain extensions that differ from the ones described here. 

### ![folder](../img/folder.png) File Browser:
Your files are connected to your user account and will be loaded each time you log into GeoLab, regardless of which server options you select.

Individual user storage quotas are in place. Treat your file system as a place to keep notebooks and _intermediate_ data while actively working on your workflow and analysis. Do not use GeoLab for long-term raw data storage or final data products.

```{note}
The `\shared` and `\shared_readwrite` directories are available to all GeoLab users. <br>
The `\shared` drive is read-only. Look here for materials specific to EarthScope Short Courses / Workshops and tutorials. <br>
The `\shared_readwrite` is accessible to all users. Other users may view, modify, or delete any data placed here. Please use this space as a _temporary_ means of sharing with colleagues. Please keep this space organized, clean up after yourself, and use respect and caution by the [Acceptable Use Policy](../welcome/geolab_AUP.md) and [Code of Conduct](../welcome/geolab_CoC.md)! 
```

At the top of the File Navigation Pane, you'll find shortcuts to:
- create a new folder
- upload files
- refresh the file system navigation pane
- clone a git repository (see [Using Git](./using_git.md))
- filter/search your files

Right-clicking on a file or folder allows you to perform standard file operations (e.g., rename, delete, copy, paste, etc.). 

### ![usage](../img/usage_monitor.png) Usage Browser:
The usage browser makes it easy to toggle between your active tabs, python kernels, and workspaces. This tab offers a quick way to organize your work and manage resources.

### ![dask](../img/dask_icon.png) Dask Dashboard:
Dask is a powerful extension that orchestrates workflow parallelization. This panel allows you to configure Dask workers and explore performance metrics manually. See [Dask](../advanced_topics/dask.md) for more details.

### ![git](../img/git_icon.png) Git Dashboard:
Git is a powerful tool for version control, collaboration, and sharing work by Open Science and Reproducibility values. The git dashboard allows manual/visual control of git repositories. See [Using Git](./using_git.md) for more details.

### ![toc](../img/toc_icon.png) Table of Contents:
If the Python notebook or markdown file in the active tab in the main panel contains headers and subsections, you can navigate to sections of the file using this panel. When developing notebooks longer than a couple of cells, it is recommended that you add section headers and annotate your work to keep it organized and take advantage of this feature. 

### ![jb](../img/jb_icon.png) JB - JupyterBook Navigation:
Select this button if git repositories in your file system contain JupyterBook documentation. 

### ![extension](../img/extension_icon.png) JupyterLab Extension Manager:
Manage community-developed extensions for JupyterLab that you may wish to install in GeoLab.
