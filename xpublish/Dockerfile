FROM continuumio/miniconda3:4.8.2

RUN conda install -c conda-forge xpublish==0.0.2 xarray==0.15 netCDF4 scipy && conda clean -tipsy

COPY run_server.py .

CMD [ "python" , "run_server.py" ]
