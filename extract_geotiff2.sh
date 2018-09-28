#!/bin/bash
# Bash script to extract RGB geotiffs from S3 L1C images
# Arg 1 is the path to the folder containing unzipped S3 images
# Arg 2 is the folder to save the geotiff

# Script arguments
in_folder=$1
out_folder=$2
epsg=$3
bands=$4

for elem in $in_folder/*/
do
	# Fetch S3 image name from folder
	name=$(echo $elem | rev | cut -d'/' -f2 | rev | cut -d'.' -f 1) 
	echo $name

    # Get output name
    outfile=$out_folder/$name.tif

    # If the file exists skip the run
    if [  ! -f $outfile ]; then


    	# Run subset to keep bands (later pass bands to arguments)
    	gpt subset -Ssource=$elem/xfdumanifest.xml -PcopyMetadata='false' \
    	-PsourceBands=$bands  -t $out_folder/$name -f GeoTIFF-BigTIFF

    	# Run reproject to get to correct projection.
    	gpt reproject -Ssource=$out_folder/$name.tif -Pcrs=$epsg \
    	-PnoDataValue=-9999 -t $out_folder/$name -f GeoTIFF-BigTIFF
    fi
done
