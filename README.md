# S3_tools
In this repository you will find a collection of [ESA Sentinel-3](https://sentinel.esa.int/web/sentinel/missions/sentinel-3/overview/mission-summary) processing tools, mainly based on snappy: the 
[SNAP API](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/19300362/How+to+use+the+SNAP+API+from+Python) from Python.
I have developed these tools for my own work, so there are probably many bugs lying around (and the code will seem shabby to all you real programmers out there). However, keeping this in mind, these may be of use to Sentinel-3 users.

# Download S3 scenes 
 
 ## 1. Get a list of S3 scenes at a given location for a given date range

+ *s3_scenes_tolist.py*: python script based on the Copernicus Scihub API. For the moment is designed for OLCI. Call the functions in *download_list.py*. From a csv containing a list of sites (in the format: Site_name, lat, lon), extract image names covering the site for a given date range. The user can specify a flag to extract a single image per day, which is the closest to the specified time.
For more info, run the command `python s3_scenes_tolist.py -h`
Example run: `python s3_scenes_tolist.py -o /path/to/target/folder -s "2018-06-08" -e "2018-06-10" -p "EFR" -t 12:00:00 /path/to/csv` will search for the images of the sites located in the input csv file (user specified), between the 8th June 2018 00h00 UTC to the 10th June 2018 23h59 UTC, for EFR images. The script will create a folder for each site containing: a list of images (image name + product id) for each day, an overall list of images, and a list of 1 image / day (closest to 12H00 UTC).

## 2. Convert image list to html links

+ *csv_to_html.py*: python script that converts a list of image names + product id obtained from *s3_scenes_tolist.py* (see above) into a html document with download links. The .html file can then be opened with [DownThemAll](https://www.downthemall.net/) (or another download manager) for fast downloads of S3 images. 
Example run: `python csv_to_html.py /csv/file/from/s3_scenes_to_list_output /path/to/html/file`

# Extract a geotiff from a Sentinel 3 OLCI L1C scene (or multiple scenes)

+ *extract_geotiff.py*: python script based on snappy. The script reads in a Sentinel 3 file, creates a subset with the specified bands, reprojects the scene to the specified EPSG code and saves to a Geotiff file. The script runs __so slowly__ that other options were explored (see below).
For more info, run the command `python extract_geotiff.py -h`
Example run: `python extract_geotiff.py -c 'Oa01_radiance' -p 4326 -o /path/to/folder /path/to/S3/image.xml`
to extract Band 1 from an OLCI scene in a geotiff with the EPSG code 4326.

+ *extract_geotiff.sh*: bash script based on SNAP GPT processing, [see documentation here](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/70503475/Bulk+Processing+with+GPT) 
The parameters are passed from a parameter file to the processing xml graph, both located in the "./s3_geotiff_files" folder. 
The options are modified in the "options.properties" file. S3 scenes can be batch processed, since the script needs the path containing S3 scenes as an input. As for the python script, execution is __very slow__ (to be tested).
Example run: `./extract_geotiff.sh ./s3_geotiff_files/s3geotiff.xml ./s3_geotiff_files/options.properties /path/to/folder/containing/S3/images /path/to/target/folder`.

+ *extract_geotiff2.sh*: a bash processing chain based on a series of individual GPT commands (not the xml tree). The subset operator is called, writing the bands to a geotiff, then the reprojection operator overwrites the geotiff. This less elegant solution is __much faster__ than the previous 2.
Example run: `./extract_geotiff2.sh /path/to/folder/containing/S3/images /path/to/target/folder 4326 Oa01_radiance,Oa02_radiance
` to extract Band 1 and 2 from the Sentinel-3 OLCI scenes located in the input folder, to a Geotiff with the EPSG code 4326.

# Change the TiePointGrid of a Sentinel 3 OLCI product

## 1. Change Solar Zenith Angle to Effective Solar Zenith Angle
+ *extract_geotiff.py*: python script based on snappy. Calls the function *topo_ops.py*. The script opens a S3 OLCI image (in the native format; i.e. xml file in a SEN3 folder), resizes the TiePointGrids (TPG) to the scene size (this was necessary to obtain an acceptable resolution for the new TPG), and converts the SZA TPG to an effective SZA TPG( sun effective incident angle to the local tilt of the surface). 
See [this paper](https://doi.org/10.5194/tc-11-1091-2017).
Although this script may not be of use to users, it could serve as a base for people wishing to modify a TiePointGrid in an OLCI image. If interest is expressed, I will make a generic version of the script.
Example run: `python extract_geotiff.py /path/to/Sentinel3/xfdumanisfest.xml /path/to/target/folder`.
