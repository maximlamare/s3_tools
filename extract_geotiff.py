#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Extract multiband geotiff from Sentinel 3 OLCI L1C images.
"""
import argparse
from pathlib import Path
from snappy import ProductIO, HashMap, GPF


# Parse command line
parser = argparse.ArgumentParser(
    description='Extract multiband tiff from S3 OLCI.')

parser.add_argument('s3_scene', metavar='S3 input file',
                    help='Input S3 file (either xfdumanifest, or .dim file)')

parser.add_argument('-o', '--output', default=None, metavar='output',

                    help='Path where the geotiff is saved')

parser.add_argument('-c', '--channels', default='Oa21_radiance',
                    metavar="channels",
                    help='S3 OLCI L1C bands to store in the geotiff')

parser.add_argument('-p', '--epsg', default='4326',
                    metavar="projection", help='EPSG of geotiff projection')

args = parser.parse_args()

# Open the S3 OLCI product with snappy
s3_path = Path(args.s3_scene)

# Collect the filename
if "xml" in s3_path.name:
    s3_name = s3_path.parents[0].name.split('.')[0]
else:
    s3_name = s3_path.name.split('.')[0]

try:
    prod = ProductIO.readProduct(str(s3_path))
except IOError:
    print("Error: SNAP cannot read specified file!")

# Read product size
w, h = (prod.getSceneRasterWidth(), prod.getSceneRasterHeight())

# Read bands
user_bands = [x.replace(" ", "") for x in args.channels.split(',')]
s3bands = list(prod.getBandNames())
selected_bands = [i for e in user_bands for i in s3bands if e in i]

# Create a subset with the input bands
# Empty HashMap
parameters = HashMap()

# Subset parameters
parameters.put("sourceBands", ','.join(selected_bands))
parameters.put("region", "0,0,%s,%s" % (w, h))
parameters.put("subSamplingX", "1")
parameters.put("subSamplingY", "1")
parameters.put("copyMetadata", "true")

# Create subset using operator
prod_subset = GPF.createProduct("Subset", parameters, prod)

# Reproject subset to epsg
reproj_params = HashMap()

# Snap operator parameters for reprojection
reproj_params.put("addDeltaBands", "true")
reproj_params.put("crs", args.epsg)
reproj_params.put("resampling", "Nearest")
reproj_params.put("noDataValue", "NaN")
reproj_params.put("orthorectify", "false")

# Run the operator
reproj_prod = GPF.createProduct("Reproject", reproj_params, prod_subset)

# Save to geotiff
if args.output is None:
    outputfile = s3_path.parents[0] / s3_name
else:
    outputfile = Path(args.output) / s3_name

ProductIO.writeProduct(reproj_prod, str(outputfile), "GeoTIFF-BigTIFF")
