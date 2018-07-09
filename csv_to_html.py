#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to convert the output results of the Sentinel 3 image search
to a html file that can be opened with DownthemAll for faster image downloads.
"""
import csv
import sys
from pathlib import Path


in_csv = Path(sys.argv[1])  # Import file containing products
out_html = Path(sys.argv[2])  # Output file to be written (.html)

# Read csv
all_dates = []
with open(str(in_csv), "r") as csvfile:
    rdr = csv.reader(csvfile, delimiter=",")
    for row in rdr:
        print(row[0])
        all_dates.append((row[0], row[1]))

baseurl = "https://scihub.copernicus.eu/s3/odata/v1/Products("

# Write to output
with open(str(out_html), "w") as cartfile:
    cartfile.write(
        '<html>\n'
    )

    for prod in all_dates:
        cartfile.write(
            "<url>%s%%27%s%%27)/$value</url><br>\n"
            % (baseurl, prod[1])
        )

    cartfile.write("</html>")
