# ESM-VFC API demo

## Build and run

```shell
git clone https://github.com/ESM-VFC/esm-vfc-api-demo.git
cd esm-vfc-api-demo/
docker-compose up
```

This will build and run two containers with the following services:

- `xpublish`: serves a demo dataset (internal)
- `app`: main backend application (development mode)
- `jupyter`: Juypyter Scipy notebook instance for easy testing 

## Docs

The backend application is running at `http://127.0.0.1:5000` (this is the
default port used by Flask's development server). Note: the Docker daemon host
could be different.

API usage is shown in the `examples` folder.

See also:

- [xpublish docs](https://xpublish.readthedocs.io/)
