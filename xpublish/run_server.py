#!/usr/bin/env python3
# FROM https://github.com/jhamman/xpublish/blob/ef0842acae48522194dd1c35a36d3b11e463d610/.binder/test.py

import xarray as xr
import xpublish


if __name__ == "__main__":

    ds = xr.tutorial.open_dataset("air_temperature")
    print(ds)

    ds.rest.serve(host="0.0.0.0", port=9000)
