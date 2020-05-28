FROM continuumio/miniconda3:4.8.2

RUN conda install -c conda-forge xarray dask zarr fsspec flask && conda clean -tipsy

COPY . .

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0

CMD [ "python", "-m" , "flask" , "run" ]
