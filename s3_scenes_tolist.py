#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List_s3_scenes
"""
import argparse
from pathlib import Path
from datetime import datetime
import csv
import pandas as pd
from itertools import groupby
import numpy as np

# Import
from download_list import s3_download

# Parse command line
parser = argparse.ArgumentParser(
    description="Extract multiband tiff from S3 OLCI."
)

parser.add_argument(
    "sites_csv",
    metavar="CSV input file containing" " site names and coordinates",
    help="Input csv file: name, lat, lon",
)

parser.add_argument(
    "-o",
    "--output",
    default=None,
    metavar="output",
    help="Path where the results are saved",
)

parser.add_argument(
    "-s",
    "--start_date",
    default=datetime.strptime("2017-02-16", "%Y-%m-%d"),
    metavar="startdate",
    help="Date to search images from",
)

parser.add_argument(
    "-e",
    "--end_date",
    default=datetime.now(),
    metavar="enddate",
    help="Date to search images until",
)

parser.add_argument(
    "-p",
    "--product",
    default="EFR",
    metavar="Product type",
    help="S3 product type to query",
)

parser.add_argument(
    "-t",
    "--time_sort",
    default=None,
    metavar="timeofday",
    help="If specified, a file with 1 image per day closest to"
    "the given time of day will be returned in a file. Format:"
    "HH:MM:SS",
)

args = parser.parse_args()

# Open the csv containing list of sites
sites = []
sites_csv_file = Path(args.sites_csv)
with open(str(sites_csv_file), "r") as csvfile:
    rdr = csv.reader(csvfile, delimiter=",")
    for row in rdr:
        sites.append(row)

# Build date range using pandas
dates = pd.date_range(args.start_date, args.end_date).tolist()

# Store results in a folder with the site's name in the output folder
for site in sites:
    site_output = Path(args.output).joinpath(site[0])
    site_output.mkdir(exist_ok=False)  # Don't allow overwrite

    # Run the search tool for each day in range to avoid too many results
    for day in dates:
        s3_download(
            site_output,
            float(site[1]),
            float(site[2]),
            day.strftime("%Y-%m-%d"),
            day.strftime("%Y-%m-%d"),
            args.product,
        )

    # Collate results to a single file

    # List files
    list_files = [x for x in site_output.iterdir() if x.is_file()]

    # Loop over files in directory
    all_list = []
    for fl in list_files:
        with open(str(fl), "r") as csvfile:
            rdr = csv.reader(csvfile, delimiter=",")
            for row in rdr:
                # Append filename, product value, datetime
                all_list.append(
                    (
                        row[0],
                        row[1],
                        datetime.strptime(
                            row[0].split("_")[7], "%Y%m%dT%H%M%S"
                        ),
                    )
                )

    # Keep only unique entries
    unique_all = list(set(all_list))

    # If there are reprocessed 2018 scenes in the list
    sub_2018 = [
        x
        for x in unique_all
        if datetime.strptime(x[0].split("_")[9], "%Y%m%dT%H%M%S").year == 2018
    ]

    if sub_2018:

        # Find the last date in 2018 dates
        # Append missing 2017 processed data
        sub_2017 = [
            x
            for x in unique_all
            if datetime.strptime(x[0].split("_")[9], "%Y%m%dT%H%M%S").year
            < 2018
        ]

        # Join lists
        unique_all = sub_2018 + sub_2017

    # Sort list based on datetime
    unique_all.sort(key=lambda tup: tup[2])

    # If option selected to get 1 image / day at a specific time
    if args.time_sort:

        timesearch = datetime.strptime(args.time_sort, "%H:%M:%S")
        # Sort by day
        alldays = []
        for k, v in groupby(unique_all, key=lambda x: x[2].date()):
            alldays.append([k, list(v)])

        list1day = []
        for i in alldays:
            if len(i[1]) > 1:
                day = i[1][0][2]
                solarnoon = day.replace(
                    hour=timesearch.hour,
                    minute=timesearch.minute,
                    second=timesearch.second,
                )
                numpos = np.argmin([abs(x[2] - solarnoon) for x in i[1]])
                list1day.append(i[1][numpos])
            else:
                list1day.append(i[1][0])

        # Save to csv
        ts = site_output.joinpath("time_search.csv")
        with open(str(ts), "w") as out:
            csv_out = csv.writer(out)
            csv_out.writerow((site[0], site[1], site[2]))
            for row in list1day:
                csv_out.writerow((row[0], row[1]))

    # Save all images
    all_csv = site_output.joinpath("all_images.csv")
    with open(str(all_csv), "w") as outcsv:
        csv_out = csv.writer(outcsv)
        for row in unique_all:
            csv_out.writerow((row[0], row[1]))
