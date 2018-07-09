# S3_tools
A collection of sentinel 3 processing tools

## 1. Extract a geotiff from a Sentinel 3 OLCI L1C scene (or multiple scenes)

+ *extract_geotiff.py*: python script based on snappy. The script reads in the Sentinel 3 file, creates a subset with the specified bands, 
reprojects the scene to the specified EPSG code and saves the Geotiff. The script run so slowly that other options were explored.

+ *extract_geotiff.sh*: based on the documentation here: https://senbox.atlassian.net/wiki/spaces/SNAP/pages/70503475/Bulk+Processing+with+GPT 
The parameters are passed from a parameter file to the processing xml graph, both located in the "s3_geotiff_files" folder. 
As for the python script execution is very slow (to be tested).

+ *extract_geotiff2.sh*: a bash processing chain based on the gpt commands. The subset operator is called, writing the bands to a geotiff, then the reprojection operator overwrites the geotiff. This less elegant solution is __much faster__ than the previous 2. 

## 2. Get a list of S3 scenes at a given location for a given date range

+ *s3_scenes_tolist.py*: python script based on the Copernicus Scihub API. From a csv containing a list of sites (in the format: Site_name, lat, lon), extract image names covering the site for a given date range. The user can specify a flag to extract a single image per day, which is the closest to the specified time.
