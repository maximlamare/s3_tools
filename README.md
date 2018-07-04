# S3_tools
A collection of sentinel 3 processing tools

## 1. Extract a geotiff from a Sentinel 3 OLCI L1C scene (or multiple scenes)

+ *extract_geotiff.py*: python script based on snappy. The script reads in the Sentinel 3 file, creates a subset with the specified bands, 
reprojects the scene to the specified EPSG code and saves the Geotiff. The script run so slowly that other options were explored.

+ *extract_geotiff.sh*: based on the documentation here: https://senbox.atlassian.net/wiki/spaces/SNAP/pages/70503475/Bulk+Processing+with+GPT 
The parameters are passed from a parameter file to the processing xml graph, both located in the "s3_geotiff_files" folder. 
As for the python script execution is very slow (to be tested).

+ *extract_geotiff2.sh*: a bash processing chain based on the gpt commands. The subset operator is called, writing the bands to a geotiff, then the reprojection operator overwrites the geotiff. This less elegant solution is __much faster__ than the previous 2. 
