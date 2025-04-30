# Using Git with GeoLab

With the base GeoLab image, the `git` version control software is included by default. This toolkit provides users with a powerful open-source development tool to collaborate on various projects together.

If you want to utilize repositories maintained on a different platform (GitHub, for example) you can simply `clone` them into your GeoLab account. However, it is expected that each users will need to manage the repositories they clone to prevent any issues. Per the [Acceptable Use Policy](../geolab_AUP.md), the GeoLab administrators are not responsible for any issues that may arise during repository management.

To avoid complications, it is highly advisable that you avoid any nested cloning of repositories (ie, don't clone a repository within another repository) and to use a single directory to clone all repositories of interest (`/home/jovyan/` is a fine choice).

## The nbgitpuller of it all...