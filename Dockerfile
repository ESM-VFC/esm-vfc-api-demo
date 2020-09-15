FROM continuumio/miniconda3:4.8.2

RUN conda install -c conda-forge xarray dask netCDF4 scipy xpublish>=0.1.0 && conda clean -tipsy

COPY . .

CMD [ "uvicorn" , "--host", "0.0.0.0", "app.main:app" ]
