#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import subprocess
from bs4 import BeautifulSoup


def s3_download(outdir, lat, lon, startdate, enddate, prodtype):
    """Download the list of S3 images (user specifies product type)
     for a given location and date range; the number of queries is limited
     to 100.
     INPUTS:
     - outdir: Posix path object of location to save results
     - lat: latitude in degrees
     - lon: longitude in degrees,
     - startdate: YYYY-MM-DD (string)
     - enddate: YYYY-MM-DD (string)
     - prodtype: the S3 product type

     The function needs wget to work. """

    # Path to results .xml file
    xml_path = outdir / "query_results.xml"

    # Remove the query result file if it exists in the target folder
    try:
        xml_path.unlink()
    except OSError:
        pass

    # Prepare wget for the catalog search
    base_url = "https://scihub.copernicus.eu/s3/search?start=0&rows=100&q="

    # Identifiers for S3 scihub - clear
    (account, passwd) = ('s3guest', 's3guest')
    auth = '--user="%s" --password="%s"' % (account, passwd)

    # Wget options
    wg = "wget --no-check-certificate "
    search_output = "--output-document=%s" % str(xml_path)

    # Sensor options
    query = 'filename:S3*%s*' % prodtype

    query_date = "beginposition:[%sT00:00:01.000Z" \
                 " TO %sT23:59:59.000Z]" % (startdate, enddate)

    # Geometry options
    query_geom = 'footprint:\\"Intersects(%f, %f)\\"' % (lat, lon)

    query = "%s AND %s AND %s" % (query, query_date, query_geom)

    wget_command = '%s %s %s "%s%s"' % (wg, auth, search_output,
                                        base_url, query)

    # Run query subprocess
    subprocess.call(wget_command, shell=True)

    # Parse the xml file
    with open(str(xml_path), "r") as xmlfile:
        xmlcontent = xmlfile.read()
    soupxml = BeautifulSoup(xmlcontent, "xml")

    # Total number of results in the query
    total_results = soupxml.find("totalResults").text

    if int(total_results) == 100:
        raise ValueError('Too many results: narrow search criteria.')

    # Combination of name and id in the xml
    prod_id = []
    entries = soupxml.find_all('entry')
    for elem in entries:
        title = elem.find('title')
        id_val = elem.find('id')

        # Remove the NR products
        # TODO: pass as option
        if 'NR' not in title.text:
            prod_id.append((title.text, id_val.text))

    # Save csv file with dates
    fname = '%s_%s.csv' % (startdate, enddate)
    file = outdir.joinpath(fname)
    with open(str(file), 'w') as out:
        csv_out = csv.writer(out)
        for row in prod_id:
            csv_out.writerow(row)

    # Remove query xml
    xml_path.unlink()
