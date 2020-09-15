#!/usr/bin/env python3

# Usage (for development):
#
# From the root directory, run
#
# $ uvicorn app.main:app --reload
#
from typing import List, Optional, Union

import xarray as xr
from fastapi import APIRouter, Depends
from xpublish.routers import base_router, common_router, zarr_router
from xpublish.dependencies import get_dataset


from .utils import DatasetTransform, extract_data_along_tracks, TrackCollection


extend_base_router = APIRouter()


@extend_base_router.get('/fieldnames')
def field_names(dataset: xr.Dataset = Depends(get_dataset)) -> List[str]:
    """Returns field names (data variables) in dataset."""

    fieldnames = dataset.data_vars.keys()

    return list(fieldnames)


esm_router = APIRouter()


@esm_router.post("/extract_tracks")
def extract_tracks(
        transform: DatasetTransform,
        tracks: TrackCollection,
        fieldnames: Optional[Union[str, List[str]]] = None,
        dataset: xr.Dataset = Depends(get_dataset),
) -> TrackCollection:
    """Extract data along given ship tracks.

    The ship tracks must be given in the GeoJSON format (i.e., a
    FeatureCollection of LineString or MultiLineString geometries).

    Some transformation can be applied on the dataset first, e.g., take
    time-averaged values.

    By default extracts data for all fields (data variables) in dataset.
    One or more specific fieldnames could be specified otherwise.

    Returns GeoJSON formatted "model" tracks (coordinates coorespond to model
    points) with extracted values as feature properties.

    """
    if fieldnames is None:
        fieldnames = list(dataset.data_vars)

    if transform.aggregation == "mean":
        dataset = dataset.mean(dim=transform.dim)

    return extract_data_along_tracks(dataset, fieldnames, tracks)


demo_dataset = xr.tutorial.open_dataset("air_temperature")

demo_dataset.rest(
    routers=[
        (base_router, {'tags': ['info']}),
        (extend_base_router, {'tags': ['info']}),
        (zarr_router, {'tags': ['zarr'], 'prefix': '/zarr'}),
        (esm_router, {'tags': ['esm'], 'prefix': '/esm'})
    ]
)

app = demo_dataset.rest.app
