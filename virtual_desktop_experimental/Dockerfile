# for local builds use geolab-default
# FROM geolab-local AS stage
# ===================================
# this is untested with this image, if it fails try geolab-default
FROM public.ecr.aws/earthscope-dev/geolab/geolab-default:agu_wkshp-dc9cd124 

USER root

#install packages
RUN apt-get update -qq --yes > /dev/null \
    && apt-get install --yes -qq gnupg2 > /dev/null \
    && apt-get install gcc --yes \
    && apt-get install gfortran --yes \
    && apt-get install g++ --yes \
    && apt-get install make \
    && apt-get install ftp --yes \
    && apt-get install gmt-dcw gmt-gshhg --yes\
    && apt-get install gedit --yes \
    && apt-get install man-db --yes \
    && apt-get install openjdk-11-jre-headless --yes \
    && apt-get install xdg-utils --yes \
    && apt-get clean

# unminimize to install man-db
RUN yes | unminimize

#install gmt and pygmt from conda-forge
RUN mamba install -c conda-forge --yes gmt pygmt 

# install taup
WORKDIR /opt
RUN wget -P /opt/ https://zenodo.org/records/16884103/files/TauP-3.1.0.zip \
    && unzip /opt/TauP-3.1.0.zip \
    &&  echo 'export PATH=$PATH:/opt/TauP-3.1.0/bin'  >> ~/.bashrc \
    && rm /opt/TauP-3.1.0.zip

USER NB_USER