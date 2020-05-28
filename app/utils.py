from flask import jsonify
import xarray as xr


def extract_data_along_tracks(dataset, fieldnames, tracks):
    """Extract data from a given field along one or more ship tracks.

    Parameters
    ----------
    dataset : :class:`xarray.Dataset`
        Dataset containing data to extract.
    fieldnames : str or list
        Name(s) of the field(s) (i.e., data variables) to use.
    tracks : dict-like
        One or more ship tracks in the GeoJSON format (must be a
        `FeatureCollection` with `LineString` features only).

    Returns
    -------
    tracks_data : list of dict
        Data extracted along ship tracks. Each dict has the following
        format:
        ``{'track_id': <id>, '<field1>': [<data>], '<field2>': [<data>], ...}``.

    """
    if isinstance(fieldnames, str):
        fieldnames = [fieldnames]

    tracks_data = []

    for feature in tracks["features"]:
        points_lat, points_lon = [
            xr.DataArray(list(points), dims="track")
            for points in zip(*feature["geometry"]["coordinates"])
        ]

        ds_extract = dataset.sel(
            lat=points_lat, lon=points_lon, method="nearest"
        )

        tdata = {"track_id": feature["properties"]["track_id"]}
        tdata.update({fn: ds_extract[fn].values for fn in fieldnames})

        tracks_data.append(tdata)

    return tracks_data
