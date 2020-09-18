#!/usr/bin/env python3

# Usage (for development):
#
# From the root directory, run
#
# $ uvicorn app.main:app --reload
#
import datetime
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import xarray as xr
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from xpublish.routers import base_router, zarr_router
from xpublish.dependencies import get_dataset


from .pydantic_covjson import (
    Axis,
    Coverage,
    GridDomain,
    MultiPointDomain,
    NdArray,
    NdArrayDataType,
    ObservedProperty,
    Parameter,
    PointSeriesDomain,
    SpatialReference2D,
    TemporalReference,
    TrajectoryDomain,
    Unit
)
from .utils import DatasetTransform, extract_data_along_tracks, TrackCollection


extend_base_router = APIRouter()


@extend_base_router.get('/fieldnames')
def field_names(dataset: xr.Dataset = Depends(get_dataset)) -> List[str]:
    """Returns field names (data variables) in dataset."""

    return [str(k) for k in dataset.data_vars.keys()]


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
        fieldnames = [str(k) for k in dataset.data_vars.keys()]

    if transform.aggregation == "mean":
        dataset = dataset.mean(dim=transform.dim)

    return extract_data_along_tracks(dataset, fieldnames, tracks)


def _get_covjson_params_ranges(dataset, include_axis_names=True):
    dim2axis = {"lon": "x", "lat": "y", "time": "t"}

    parameters = {}
    ranges = {}

    for k, v in dataset.data_vars.items():
        parameters[k] = Parameter(
            description={"en": v.attrs["long_name"]},
            observed_property=ObservedProperty(label={"en": v.attrs["var_desc"]}),
            unit=Unit(label={"en": v.attrs["units"]})
        )

        if include_axis_names:
            axis_names = [dim2axis[d] for d in v.dims]
        else:
            axis_names = None

        ranges[k] = NdArray(
            datatype=NdArrayDataType.FLOAT.value,
            shape=v.shape,
            axis_names=axis_names,
            values=v.values.ravel().tolist()
        )

    return parameters, ranges


covjson_router = APIRouter()


@covjson_router.get(
    "/grid",
    response_model=Coverage,
    response_model_exclude_none=True
)
def get_grid_coverage(dataset: xr.Dataset = Depends(get_dataset)):
    """Return the published dataset (just a subset) formatted as ConverageJSON (Grid domain)."""

    ds = dataset.isel(time=slice(-5, -1)).fillna(None)

    axes = {
        "x": Axis(values=ds.lon.values.tolist()),
        "y": Axis(values=ds.lat.values.tolist()),
        "t": Axis(values=ds.time.astype(str).values.tolist())
    }

    domain = GridDomain(
        axes=axes,
        referencing=[SpatialReference2D(), TemporalReference()]
    )

    parameters, ranges = _get_covjson_params_ranges(ds)

    return Coverage(domain=domain, parameters=parameters, ranges=ranges)


@covjson_router.get(
    "/series/{lat}/{lon}",
    response_model=Coverage,
    response_model_exclude_none=True
)
def get_time_series_at_point(
        lat: float,
        lon: float,
        dataset: xr.Dataset = Depends(get_dataset)
):
    """Return model time-series (just a subset) at a given lat/lon location (nearest
    point), formatted as converageJSON (PointSeries domain).

    """
    ds = dataset.isel(time=slice(-500, -1)).sel(lat=lat, lon=lon, method="nearest")

    axes = {
        "x": Axis(values=[ds.lon.values.item()]),
        "y": Axis(values=[ds.lat.values.item()]),
        "t": Axis(values=ds.time.astype(str).values.tolist())
    }

    domain = PointSeriesDomain(
        axes=axes,
        referencing=[SpatialReference2D(), TemporalReference()]
    )

    parameters, ranges = _get_covjson_params_ranges(ds)

    return Coverage(domain=domain, parameters=parameters, ranges=ranges)


class Trajectory(BaseModel):
    points: List[Tuple[str, float, float]] = Field(..., description="(time, lat, lon) points")
    id: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "points": [
                    ["2014-06-01T01:22:00.0", 72, 270],
                    ["2014-07-01T06:22:00.0", 74, 280],
                    ["2014-08-01T10:26:00.0", 73, 290]
                ]
            }
        }


@covjson_router.post(
    "/trajectory",
    response_model=Coverage,
    response_model_exclude_none=True
)
def extract_trajectory(
        trajectory: Trajectory,
        dataset: xr.Dataset = Depends(get_dataset)
):
    """Extract model data (nearest points) along a given trajectory. """

    time, lat, lon = zip(*trajectory.points)

    da_lat = xr.DataArray(list(lat), dims="trajectory")
    da_lon = xr.DataArray(list(lon), dims="trajectory")
    da_time = xr.DataArray(pd.to_datetime(time), dims="trajectory")

    ds = dataset.sel(lat=da_lat, lon=da_lon, time=da_time, method="nearest")

    new_lat = ds.lat.values.tolist()
    new_lon = ds.lon.values.tolist()
    new_time = ds.time.astype(str).values.tolist()

    axes = {
        "composite": Axis(
            coordinates=["t", "x", "y"],
            values=list(zip(new_time, new_lon, new_lat))
        )
    }

    domain = TrajectoryDomain(
        axes=axes,
        referencing=[SpatialReference2D(), TemporalReference()]
    )

    parameters, ranges = _get_covjson_params_ranges(ds, include_axis_names=False)

    return Coverage(domain=domain, parameters=parameters, ranges=ranges)


class Points(BaseModel):
    date: datetime.datetime
    values: List[Tuple[float, float]] = Field(..., description="(lat, lon) points")
    id: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "date": datetime.datetime(2014, 8, 8, 17, 45),
                "values": np.dstack(
                    [np.random.uniform(20, 70, 50), np.random.uniform(200, 330, 50)]
                )[0].tolist()
            }
        }


@covjson_router.post(
    "/points",
    response_model=Coverage,
    response_model_exclude_none=True
)
def extract_points(
        points: Points,
        dataset: xr.Dataset = Depends(get_dataset)
):
    """Extract model data (nearest points) at given lat/lon points at a given
    time.

    """
    lat, lon = zip(*points.values)
    da_lat = xr.DataArray(list(lat), dims="points")
    da_lon = xr.DataArray(list(lon), dims="points")

    ds = dataset.sel(lat=da_lat, lon=da_lon, time=points.date, method="nearest")

    new_lat = ds.lat.values.tolist()
    new_lon = ds.lon.values.tolist()
    new_time = ds.time.astype(str).values.item()

    axes = {
        "t": Axis(values=[new_time]),
        "composite": Axis(
            coordinates=["x", "y"],
            values=list(zip(new_lon, new_lat))
        )
    }

    domain = MultiPointDomain(
        axes=axes,
        referencing=[SpatialReference2D(), TemporalReference()]
    )

    parameters, ranges = _get_covjson_params_ranges(ds, include_axis_names=False)

    return Coverage(domain=domain, parameters=parameters, ranges=ranges)


demo_dataset = xr.tutorial.open_dataset("air_temperature")

demo_dataset.rest(
    routers=[
        (base_router, {'tags': ['info']}),
        (extend_base_router, {'tags': ['info']}),
        (zarr_router, {'tags': ['zarr'], 'prefix': '/zarr'}),
        (esm_router, {'tags': ['esm'], 'prefix': '/esm'}),
        (covjson_router, {'tags': ['covjson (experimental)'], 'prefix': '/covjson'})
    ]
)

app = demo_dataset.rest.app
