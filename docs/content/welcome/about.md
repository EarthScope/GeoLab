# About GeoLab

## Our Motivation
The nature of scientific discovery and collaboration is changing right in front of us, in ways that continue to astonish and inspire us. The ways research is conducted, data is collected, and results are communicated to public and private stakeholders are rapidly evolving. Broadly, we see science trending away from isolated, privileged institutions to distributed networks of communities with individual members that move dynamically from one group to another. With GeoLab, we seek to leverage that new, contemporary structure to make geophysical science more transparent, productive, repeatable, and inclusive.

One of the key objectives of EarthScope GeoLab is to demonstrate how cloud infrastructure and services can facilitate high-quality, repeatable geophysical research. We are acutely aware of the barriers that exist for individuals that may want to transition from the traditional ways of downloading and managing large amounts of data on their local workstations to a cloud-based workflow. Among other things, the complexity of deploying and maintaining infrastructure, the uncertainty of cost-control measures, the unfamiliarity with commercial cloud services, and a general lack of awareness of community standards and knowledge all contribute to the hesitancy of adopting cloud technologies for your own research goals.

Based on the welcoming, interconnected practices of open-science communities like [Pangeo](https://www.pangeo.io) that have pioneered data-intensive JupyterHub workflows in the cloud, we seek to overcome these barriers by building on existing open-source infrastructure and software to lower the barrier of entry for researchers looking to move their workflows into the cloud.

## What is GeoLab?

GeoLab is a JupyterHub deployed on Amazon Web Services (AWS) that is managed by the [International Interactive Computing Collaboration (2i2c)](https://www.2i2c.org).

GeoLab provides persistent, customizable, cloud-based compute environments to geophysical researchers and educators for data analysis and visualization. Environments built from the same image are identical, ensuring that software versions are consistent from one user to another. And since GeoLab operates in the cloud, anyone with a reliable internet connection can access their environment.

One of the primary benefits of GeoLab is that it sits alongside the EarthScope [Data Repositories](https://www.earthscope.org/data/) in AWS (US-East2). This means that users can leverage low-latency, high-througput access methods to analyze large volumes of data.

GeoLab has been designed with analysis of miniSEED and/or RINEX data in mind, but it is not limited to the fields of seismology or geodesy. (?)Any(?) group looking to work with large datasets or that would prefer not to maintain their own complicated compute environment could benefit from working in GeoLab.

### Hub Management

Our cloud platform is built and maintained by [2i2c](https://2i2c.org), a non-profit organization that excels in using open-source inferstructure tools to design and operate JupyterHubs for other research and education institutions that align with best practices and standards. An outline of their community service model that brings together a community of users into a shared compute instance focused on doing cutting-edge data science is shown below.

With the [Right to Replicate](https://2i2c.org/right-to-replicate/) policy, 2i2c ensures that GeoLab remains flexible with respect to commercial cloud providers and avoids the potential for vendor lock-in.

Together, we co-develop cloud-based workflows to guide our community towards open-source tools and software that drives innovative solutions to data-intensive geoscientific challenges.

![2i2c Service Model](img/2i2c_service.png)