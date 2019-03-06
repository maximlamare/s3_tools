#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Import libraries

import sys
import matplotlib.pyplot as plt
from osgeo import gdal, osr, ogr
import numpy as np

tif = sys.argv[1]
outfold = sys.argv[2]
outtype = sys.argv[3]

if outtype not in ['rgb', 'band21']:
    raise RuntimeError("Error: select 'rgb' or 'band21' !")


def normalize(arr):
    ''' Function to normalize an input array to 0-1 '''
    arr_min = arr.min()
    arr_max = arr.max()
    return (arr - arr_min) / (arr_max - arr_min)

# Read the data and metadata
DMC_lat = -75.099626667
DMC_lon = 123.302526667

ds = gdal.Open(tif)

if outtype == 'rgb':
    bnd1 = ds.GetRasterBand(1).ReadAsArray()
    bnd2 = ds.GetRasterBand(2).ReadAsArray()
    bnd3 = ds.GetRasterBand(3).ReadAsArray()
    masked1 = np.ma.masked_where(bnd8 == -9999, bnd1)
    masked2 = np.ma.masked_where(bnd6 == -9999, bnd2)
    masked3 = np.ma.masked_where(bnd3 == -9999, bnd3)

    rgb = np.dstack((normalize(masked1), normalize(masked2), normalize(masked3)))
else:
    bnd4 = ds.GetRasterBand(4).ReadAsArray()
    masked4 = np.ma.masked_where(bnd4 == -9999, bnd4)
    rgb = normalize(masked4)


gt = ds.GetGeoTransform()
proj = ds.GetProjection()

xres = gt[1]
yres = gt[5]

# get the edge coordinates and add half the resolution
# to go to center coordinates
xmin = gt[0] + xres * 0.5
xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
ymax = gt[3] - yres * 0.5

ds = None

inproj = osr.SpatialReference()
inproj.SetWellKnownGeogCS("WGS84")
outproj = osr.SpatialReference()
outproj.ImportFromWkt(proj)


point = ogr.Geometry(ogr.wkbPoint)
point.AddPoint(DMC_lon, DMC_lat)
coordTransform = osr.CoordinateTransformation(inproj, outproj)
point.Transform(coordTransform)
col = int((point.GetX() - gt[0]) / gt[1])
row = int((gt[3] - point.GetY()) / -gt[5])

All_scene = plt.figure()
ax = All_scene.add_subplot(121)
ax.imshow(rgb)
ax.plot(col, row, 'r+', markersize=4)

ax.axis('off')

ax2 = All_scene.add_subplot(122)
ax2.plot(col, row, 'r+', markersize=4)

ax2.imshow(rgb)
ax2.axis('off')
ax2.set_xlim([col-150, col+150])
ax2.set_ylim([row-150, row+150])

# Get date and time
datetime = tif.split('/')[-1].split('.')[0].split('_')[7].split('T')
date = datetime[0][:4] + '_' + datetime[0][4:6] + '_' + datetime[0][6:]
time = datetime[1][:2] + 'H' + datetime[1][2:4] + 'm' + datetime[1][4:] + 's'

plt.suptitle('Date: %s, Time: %s' % (date, time))
plt.tight_layout()
plt.savefig(outfold + '/' + datetime[0] + '_' + datetime[1] + '.png', dpi=600)

plt.close()
