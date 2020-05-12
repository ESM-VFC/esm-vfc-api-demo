FROM continuumio/miniconda3:4.8.2

RUN conda install -c conda-forge xpublish netCDF4 scipy && conda clean -tipsy

COPY start_xpublish_standalone.py .

EXPOSE 9000

CMD [ "python",  "start_xpublish_standalone.py" ]
