# ESM-VFC API demo

## Build and run

```shell
git clone https://github.com/ESM-VFC/esm-vfc-api-demo.git
cd esm-vfc-api-demo/
docker build -t esm-vfc-api-demo .
docker run -p 8000:8000 esm-vfc-api-demo
```

## Docs

Interactive API documentation is available at `http://127.0.0.1:8000/docs` (this is the
default port used by Uvicorn's development server). Note: the Docker daemon host
could be different.

