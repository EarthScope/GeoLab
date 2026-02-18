# Storage options, limits, and management in GeoLab

GeoLab offers a few different options to store data as described below. These storage locations are for storing data processing results, intermediate data products, shared notebooks, etc. These locations are not for long term storage. Also, we strongly recommend using data in EarthScope repositories directly through programmatic access without making a copy.

## User home directories (aka folders)

All GeoLab users have a home directory (`/home/jovyan`) with these limitations: 

* Store up to a maximum of 50 GB
* Accounts that have not accessed GeoLab for a period of six months may have all contents in their home directory removed.

We highly recommend that you process data in memory. If you must save data to storage, do it in small batches and proactively delete the data once finished with your analysis. To see how much disk space you are using, use the command below from any Terminal window:

`du -sh --exclude=="shared*" ~/`

If you exceed the 50 GB limit, your current session will remain active but your processes will not be able to write to storage. This may result in your server instance crashing. To remedy this, start another server instance and immediately reduce your disk usage. If you are unable to restart a server after multiple attempts, please reach out to the GeoLab admins by sending an email to help@earthscope.org for assistance.

If your account is inactive and data are removed from your home directory, this does not affect your access to GeoLab or your EarthScope User account. If you log into GeoLab after a period of inactivity and subsequent data removal, you will start with an empty home directory.

## The `shared` storage

The `shared` storage is a directory that everyone can read files from but only hub admins can write to. This storage is located at:
* `shared` in the File Browser, and
* `/home/jovyan/shared/` on the file system

Shared storage is useful for common notebooks and (smallish) data sets for workshops or group exercises.  Contact us at help@earthscope.org if you would like us to consider temporarily adding files to this location.

## The `scratch` bucket storage

The `scratch` bucket is an S3 bucket that all GeoLab users can read and write to. The `scratch` bucket is available at `s3://earthscope-scratch/` and should only be used for temporary data as it will automatically delete files after 14 days.

## Bring your own S3 bucket

Users can create their own S3 bucket and use it from GeoLab. If you want to create your own bucket we recommend setting it up in the `us-east-2` AWS region, which is where GeoLab operates, to minimize transfer latency and costs. More details on configuring an AWS account can be found here: https://aws.amazon.com/pm/serv-s3/ 
