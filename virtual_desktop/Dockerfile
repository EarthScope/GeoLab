FROM public.ecr.aws/earthscope-dev/geolab/geolab-default:agu_wkshp-dc9cd124 AS stage 

ENV NB_GID=1000

FROM stage

USER root

COPY setup-scripts/setup-linux-desktop.bash /opt/setup-scripts/setup-linux-desktop.bash
COPY setup-scripts/fix-permissions.bash /usr/local/bin/fix-permissions.bash

# Set DISPLAY env variable, so processes know where to open GUI windows.
# Allows python processes running in notebooks to open windows in the GUI.
ENV DISPLAY=":1.0"

# Setup Linux Desktop
RUN chmod a+x /opt/setup-scripts/setup-linux-desktop.bash
RUN chmod a+x /usr/local/bin/fix-permissions.bash

RUN /opt/setup-scripts/setup-linux-desktop.bash

COPY startup-scripts /usr/local/bin/start-notebook.d/

# env variables used by downstream images for setting up desktop files or
# mime associations. Consumed by the startup-scripts in startup-scripts/
ENV DESKTOP_FILES_DIR=/opt/desktop-files
ENV MIME_FILES_DIR=/opt/mime-files

RUN mkdir -p ${DESKTOP_FILES_DIR} ${MIME_FILES_DIR}

#install GMT
RUN apt-get update -qq --yes > /dev/null \
    && apt-get install --yes -qq gnupg2 > /dev/null \
    && apt-get install gcc --yes \
    && apt-get install gfortran --yes \
    && apt-get install g++ --yes \
    && apt-get install make \
    && apt-get install ftp --yes \
    # && apt-get install gmt gmt-dcw gmt-gshhg --yes\
    # && apt-get install gedit --yes \
    # && apt-get install man-db --yes \
    && apt-get clean

USER ${NB_UID}

# Pin jupyterhub and pydantic to older version
# because of https://github.com/NASA-IMPACT/veda-jupyterhub/issues/52#issuecomment-2277453902
RUN python -m pip install --no-cache "jupyterhub<5.0.0" "pydantic<2.0"
RUN python -m pip install --no-cache jupyter-remote-desktop-proxy
# RUN python -m pip install --no-cache git+https://github.com/sunu/jupyter-remote-qgis-proxy@e1a49e0ba98700c2f49fc092d5fc1e43ca5442eb