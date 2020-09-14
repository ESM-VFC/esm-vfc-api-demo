FROM continuumio/miniconda3:4.8.2

RUN conda install -c conda-forge xarray==0.15 dask zarr fsspec flask && conda clean -tipsy

RUN python -m pip install aiohttp

COPY . .

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0

CMD [ "python", "-m" , "flask" , "run" ]
