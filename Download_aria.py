#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 08:58:17 2018

@author: lamarem
"""

import subprocess
import csv
import sys
from pathlib import Path
from os import chdir

# Import file containing hand sorted cloud S3 images
sat_file = Path(sys.argv[1])
cart = Path(sys.argv[2])
# Output files
outfls = Path(sys.argv[3])


# Read csv
all_dates = []
with open(str(sat_file), "r") as csvfile:
    rdr = csv.reader(csvfile, delimiter=",")
    next(rdr)
    for row in rdr:
        all_dates.append((row[0], row[1]))

baseurl = "https://scihub.copernicus.eu/s3/odata/v1/Products("

with open(str(cart), "w") as cartfile:
    cartfile.write(
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        '<metalink xmlns="urn:ietf:params:xml:ns:metalink">\n'
    )

    for prod in all_dates:
        cartfile.write(
            "<file name=\"%s.zip\"><url>%s'%s')/$value</url></file>"
            % (prod[0], baseurl, prod[1])
        )

    cartfile.write("</metalink>")

chdir(str(outfls))
commandearia = "aria2c -c --http-user=s3guest --http-passwd=s3guest"\
               " --check-certificate=false --max-concurrent-downloads=2"\
               " -M %s" % cart

subprocess.call(commandearia, shell=True)
