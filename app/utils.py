import json

import numpy as np
import xarray as xr


# https://stackoverflow.com/a/47626762
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def extract_field_along_tracks(dataset, var_name, tracks):
    """Extract data from a given field along one or more ship tracks.

    Parameters
    ----------
    dataset : :class:`xarray.Dataset`
        Dataset containing data to extract.
    var_name : str
        Name of the field (data variable).
    tracks : dict-like
        One or more ship tracks in the GeoJSON format (must be a
        `FeatureCollection` with `LineString` features only).

    Returns
    -------
    tracks_data : dict
        Data extracted along ship tracks.

    """
    tracks_data = []

    for feature in tracks["features"]:
        points_lat, points_lon = [
            xr.DataArray(list(points), dims="track")
            for points in zip(*feature["geometry"]["coordinates"])
        ]

        da_result = dataset[var_name].sel(
            lat=points_lat, lon=points_lon, method="nearest"
        )

        tracks_data.append({
            "track_id": feature["properties"]["track_id"],
            var_name: da_result.values
        })

    return {"data": json.dumps(tracks_data, cls=NumpyEncoder)}
