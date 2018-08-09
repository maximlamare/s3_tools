#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' change_tiepoint.python3
The script opens a S3 OLCI image (in the native format),
resizes the TiePointGrids to the scene size (this was necessary to
obtain an acceptable resolution for the TPGs), and converts the SZA
TPG to an effective SZA ( sun effective incident an-
gle to the local tilt of the snow surface).
See doi 10.5194/tc-11-1091-2017

The script takes 2 input arguments:

1. The path to the xfdumanifest.xml file of a S3 product (or a dim)
2. The output folder where the new product will be saved'''
import numpy as np
import sys
from bs4 import BeautifulSoup
from pathlib import Path
from snappy import (ProductIO, TiePointGrid, HashMap, GPF)
import topo_ops

# Input / output
s3_file = Path(sys.argv[1])
outfile = Path(sys.argv[2])

# Open Snap product
try:
    prod = ProductIO.readProduct(str(s3_file))
except ImportError:
    print("Error: SNAP cannot read specified file!")

# Product band size
height = prod.getSceneRasterHeight()
width = prod.getSceneRasterWidth()

# Get original TiePointGrid specs from SZA TiePoint Grid
szatp = prod.getTiePointGrid("SZA")
height_tp = szatp.getGridHeight()
width_tp = szatp.getGridWidth()
samp_x = szatp.getSubSamplingX()
samp_y = szatp.getSubSamplingY()

# Resize TiePointGrids to match scene size
tpg_dict = {}
for tpg in list(prod.getTiePointGridNames()):
    # Read in TPG as RasterDataNodes
    current_tpg = prod.getRasterDataNode(tpg)
    array = np.zeros((height, width), dtype=np.float32)

    if tpg == 'SZA':
        sza_raster = current_tpg.readPixels(0, 0, width, height, array)
    else:
        if tpg == 'SAA':
            saa_raster = current_tpg.readPixels(0, 0, width, height, array)

        current_raster = current_tpg.readPixels(0, 0, width, height, array)

        # Store in dictionnary
        new_tpg = TiePointGrid(tpg,
                               width,
                               height,
                               szatp.getOffsetX(),
                               szatp.getOffsetY(),
                               1.0,
                               1.0,
                               current_raster,)
        tpg_dict.update({tpg: new_tpg})

# Get band array of altitude
altitude = prod.getRasterDataNode("altitude")

# Read band arrays to rasters
array = np.zeros((height, width), dtype=np.float32)
altitude_raster = altitude.readPixels(0, 0, width, height, array)

# Calculate slope and aspect from the DEM
slope, aspect = topo_ops.horneslope(altitude_raster, 300)

# Convert to radians
sza_rad = np.deg2rad(sza_raster)
saa_rad = np.deg2rad(saa_raster)

# Calculate effective SZA
mu = np.cos(sza_rad) * np.cos(slope) + np.sin(sza_rad) * np.sin(slope) * \
    np.cos(saa_rad - aspect)
eff = np.arccos(mu)

# Rebuild SZA TiePointGrid
sza_tpg = TiePointGrid('SZA',
                       width,
                       height,
                       szatp.getOffsetX(),
                       szatp.getOffsetY(),
                       1.0,
                       1.0,
                       np.rad2deg(eff))

# Remove all TiePoint GRids
for tpg in list(prod.getTiePointGridNames()):
    tpg_prd = prod.getTiePointGrid(tpg)
    prod.removeTiePointGrid(tpg_prd)

# Add all TiePointGrids back
for newtpg in tpg_dict:
    prod.addTiePointGrid(tpg_dict[newtpg])

# Add the new SZA TPG
prod.addTiePointGrid(sza_tpg)

# Write to a new product
# Get original product name
print(s3_file.name)
if "xml" in str(s3_file.name):
    with open(str(s3_file), "r") as xmlfile:
        xmlcontent = xmlfile.read()
    soupxml = BeautifulSoup(xmlcontent, "xml")
    xml_name = soupxml.find("sentinel3:productName").text.split('.')[0]
else:
    xml_name = str(s3_file.name).split('.')[0]

parameters = HashMap()
parameters.put("file", xml_name + "_szaeff.dim")
parameters.put("formatName", "BEAM-DIMAP")
output = GPF.createProduct("Write", parameters, prod)
ProductIO.writeProduct(output, str(outfile.joinpath(xml_name + "szaeff.dim")),
                       "BEAM-DIMAP")
