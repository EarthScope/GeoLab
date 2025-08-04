FROM pangeo/pytorch-notebook:2025.01.24

USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH ${NB_PYTHON_PREFIX}/bin:$PATH

# Needed for apt-key to work, gcc compiler for 
RUN apt-get update -qq --yes > /dev/null \
    && apt-get install --yes -qq gnupg2 > /dev/null \
    && apt-get install gcc --yes \
    && apt-get install gfortran --yes \
    && apt-get install g++ --yes \
    && apt-get install make \
    && apt-get install ftp --yes \
    && apt-get clean

USER ${NB_USER}

COPY environment.yml /tmp/

RUN mamba env update --name ${CONDA_ENV} -f /tmp/environment.yml \
    && pip cache purge \
    && mamba clean -afy
RUN conda install awscli==2.27.0
RUN conda create -n passoft3 passoft -c https://onyx.passcal.nmt.edu/passcal -c conda-forge

# Set up the start command 
USER ${NB_USER}
RUN chmod +x start \
    && cp start /srv/start

ENTRYPOINT ["/srv/start"]