# Using Git with GeoLab

 `Git` is a broadly used version control system included in all GeoLab images. The git toolkit provides users with a robust open-source development tool for collaborating on various projects.

If you want to utilize repositories maintained on a different platform (GitHub, for example), you can simply `clone` them into your GeoLab account. However, each user is expected to manage the repositories they clone to prevent any issues that may arise. Per the [Acceptable Use Policy](../welcome/geolab_AUP.md), the GeoLab administrators are not responsible for any issues that may arise during repository management.

To avoid complications, it is highly advisable to avoid nested cloning of repositories (i.e., don't clone a repository within another repository) and to use a single directory to clone all repositories of interest (`/home/jovian/` is a fine choice).

## Learning Git
There are many, _many_ resources for learning to use git. While GeoLab does have an integrated git dashboard on the left sidebar, we recommend learning the git CLI (command-line interface) so that your learning is portable to any future computing environments you might encounter. Once you understand git on the command line, using any version of a Git GUI is a smooth transition. 

Some git resources we love:
[Why Git? Illustrated](https://openscapes.org/blog/2022-05-27-github-illustrated-series/)
[Happy Git](https://happygitwithr.com/) - Though the title of this article implies it is for RStudio, _very little_ of the content is R-specific. We think it's a fantastic resource for _all_ git learners.
[Free Code Camp](https://www.freecodecamp.org/news/learn-the-basics-of-git-in-under-10-minutes-da548267cc91/)


## The nbgitpuller of it all...