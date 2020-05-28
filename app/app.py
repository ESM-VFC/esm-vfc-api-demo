#!/usr/bin/env python3

# Usage (for development):
#
# $ export FLASK_APP=api_demo.py
# $ python -m flask run --host=0.0.0.0 --port=9000

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from fsspec.implementations.http import HTTPFileSystem
import numpy as np
import requests
import xarray as xr

from utils import extract_data_along_tracks


# https://stackoverflow.com/a/47626762
class NumpyEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.json_encoder = NumpyEncoder

# url and port of xpublish server running for the demo dataset
demo_dataset_server_url = "http://xpublish:9000"

# http map of demo dataset
fs = HTTPFileSystem()
demo_dataset_http_map = fs.get_mapper(demo_dataset_server_url)


@app.route('/datasets/demo')
def get_demo_dataset_html_repr():
    return requests.get(demo_dataset_server_url + "/").text


@app.route('/api/v1.0/datasets/demo/fieldnames')
def get_demo_dataset_field_names():
    """Returns variable names in demo dataset."""

    # TODO: fix this upstream
    dataset = xr.open_zarr(demo_dataset_http_map, consolidated=True)
    fieldnames = dataset.data_vars.keys()

    return {"fieldnames": list(fieldnames)}


@app.route('/api/v1.0/datasets/demo/info')
def get_demo_dataset_info():
    """Returns demo dataset info."""

    info = requests.get(demo_dataset_server_url + "/info").json()

    return {"info": info}


@app.route("/api/v1.0/datasets/demo/extract_tracks", methods=["POST"])
def extract_demo_data_along_tracks():
    """Extract data along given ship tracks."""

    request_data = request.get_json()
    dataset = xr.open_zarr(demo_dataset_http_map, consolidated=True)

    transform = request_data.get("transform")

    if transform is not None:
        if transform.get("aggregation") == "mean":
            dataset = dataset.mean(dim=transform.get("dim"))

    extract_data = extract_data_along_tracks(
        dataset, request_data["fieldnames"], request_data["tracks"]
    )

    return jsonify(data=extract_data)
