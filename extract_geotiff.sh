#!/bin/bash

############################################
# Command line handling
############################################

# first parameter is a path to the graph xml
graphXmlPath="$1"

# second parameter is a path to a parameter file
parameterFilePath="$2"

# use third parameter for path to source products
sourceDirectory="$3"

# use fourth parameter for path to target products
targetDirectory="$4"


############################################
# Main processing
############################################

# Create the target directory
mkdir -p "${targetDirectory}"

for F in $(ls -1d "${sourceDirectory}"/S3*.SEN3); do
    echo $F
    sourceFile=$F/xfdumanifest.xml
    echo $sourceFile
    subdir="/$F/${1##*/}"
    namedir=$(basename $F)
    fname="${namedir%%.*}"
    
    targetFile=${targetDirectory}/$fname.tiff
    gpt ${graphXmlPath} -e -p ${parameterFilePath} -t ${targetFile} -f "GeoTIFF-BigTIFF" ${sourceFile}
done