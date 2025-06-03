FROM pangeo/pangeo-notebook:2024.05.21

USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH ${NB_PYTHON_PREFIX}/bin:$PATH

# Needed for apt-key to work
RUN apt-get update -qq --yes > /dev/null && \
    apt-get install --yes -qq gnupg2 > /dev/null

USER ${NB_USER}

COPY environment.yml /tmp/

RUN mamba env update --name ${CONDA_ENV} -f /tmp/environment.yml