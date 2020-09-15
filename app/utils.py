from typing import Any, Dict, List, Optional, Union, Tuple

import xarray as xr
from pydantic import BaseModel, Field


class DatasetTransform(BaseModel):
    """Apply some transformation on the dataset, e.g., extract mean values
    along a given dimension)

    """
    aggregation: Optional[str] = None
    dim: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {"aggregation": "mean", "dim": "time"}
        }


# taken or inspired from https://github.com/developmentseed/geojson-pydantic (MIT License)

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]
Coordinate = Union[Tuple[NumType, NumType], Tuple[NumType, NumType, NumType]]


class LineString(BaseModel):
    """LineString Model"""

    type: str = Field("LineString", const=True)
    coordinates: List[Coordinate] = Field(..., min_items=2)


class MultiLineString(BaseModel):
    """MultiLineString Model"""

    type: str = Field("MultiLineString", const=True)
    coordinates: List[List[Coordinate]]


class Track(BaseModel):
    type: str = Field("Feature", const=True)
    geometry: Union[LineString, MultiLineString]
    properties: Optional[Dict[Any, Any]]
    id: Optional[str]
    bbox: Optional[BBox]


class TrackCollection(BaseModel):
    """One or more ship tracks encoded as GeoJSON."""

    type: str = Field("FeatureCollection", const=True)
    features: List[Track]
    bbox: Optional[BBox]

    def __iter__(self):
        """iterate over features"""
        return iter(self.features)

    def __len__(self):
        """return features length"""
        return len(self.features)

    def __getitem__(self, index):
        """get feature at a given index"""
        return self.features[index]

    class Config:
        schema_extra = {
            "example": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [71.591269, 27.809646],
                            [74.112343, 34.536865],
                            [77.23488, 60.95901],
                            [81.77730, 80.55286]
                        ]
                    },
                    "id": "track-1"
                }]
            }
        }


def extract_data_along_tracks(
        dataset: xr.Dataset,
        fieldnames: Union[str, List[str]],
        tracks: TrackCollection
) -> TrackCollection:
    """Extract data from a given field along one or more ship tracks. """

    if isinstance(fieldnames, str):
        fieldnames = [fieldnames]

    model_tracks = []

    for feature in tracks:
        if isinstance(feature.geometry, MultiLineString):
            raise ValueError("MultiLineString not yet supported")

        points_lat, points_lon = [
            xr.DataArray(list(points), dims="track")
            for points in zip(*feature.geometry.coordinates)
        ]

        ds_extract = dataset.sel(
            lat=points_lat, lon=points_lon, method="nearest"
        )

        geom = LineString(coordinates=list(zip(ds_extract.lat, ds_extract.lon)))
        props = {fn: ds_extract[fn].values.tolist() for fn in fieldnames}

        model_tracks.append(Track(geometry=geom, id=feature.id, properties=props))

    return TrackCollection(features=model_tracks)
