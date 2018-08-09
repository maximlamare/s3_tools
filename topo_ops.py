#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np
from numba.decorators import autojit


@autojit
def horneslope(indem, pixel_size):
    """ Calculate slope and aspect from a DEM.
        Using autojit speeds up the function by a factor of 200 (benchmark
        tests).
        The algorithm is based on Horn's (1981) Finite Difference Weighted by
        reciprocal of Distance (Lee and Clarke, 2005). The algorithm has been
        shown to perform better than others (Lee and Clarke, 2005; Srinivasan
        and Engel, 1991; Dunn and Hickley, 1998). The Horn algorithm leads to
        a loss in local variability (smooths small dips and peaks), but doesn't
        overestimate the slopes or exagerate peaks. Jones (1998) showed that
        the algorithm performed well in comparison to reference surfaces.

        INPUTS: - indem: input dem as a numpy array
                - pixel_size: pixel size, has to be square pixels

        Outputs: - output_sl: an array with slope values in radians
                 - output_asp: an array with aspect values in radians"""

    output_sl = np.full_like(indem, np.nan)
    output_asp = np.full_like(indem, np.nan)

    rows, cols = indem.shape

    for x in range(1, cols - 1):
        for y in range(1, rows - 1):
            dzx = (
                (
                    indem[y - 1, x + 1]
                    + 2
                    * indem[y, x + 1]
                    + indem[y + 1, x + 1]
                )
                - (
                    indem[y - 1, x - 1]
                    + 2
                    * indem[y, x - 1]
                    + indem[y + 1, x - 1]
                )
            ) / (
                8 * pixel_size
            )
            dzy = (
                (
                    indem[y + 1, x - 1]
                    + 2
                    * indem[y + 1, x]
                    + indem[y + 1, x + 1]
                )
                - (
                    indem[y - 1, x - 1]
                    + 2
                    * indem[y - 1, x]
                    + indem[y - 1, x + 1]
                )
            ) / (
                8 * pixel_size
            )

            slope = np.sqrt(dzx ** 2 + dzy ** 2)
            aspect = 180 / np.pi * np.arctan2(dzy, -dzx)

            output_sl[y, x] = np.arctan(slope) * 180 / np.pi

            if output_sl[y, x] == 0:
                # If no slope, set aspect to 0. Setting it to nan messed up the
                # reinterpolation.
                output_asp[y, x] = 0
            else:
                if aspect > 90:
                    output_asp[y, x] = 360 - aspect + 90
                else:
                    output_asp[y, x] = 90 - aspect

    return np.deg2rad(output_sl), np.deg2rad(output_asp)

    return np.deg2rad(output_sl), np.deg2rad(output_asp)
