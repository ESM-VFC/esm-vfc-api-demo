# Backend demo

## Build and run

```shell
git clone https://github.com/ESM-VFC/xpublish-standalone-demo.git
cd xpublish-standalone-demo/
docker-compose up
```

This will build and run two containers with the following services:

- `xpublish`: serves a demo dataset (internal)
- `app`: main backend application (development mode)

## Docs

The backend application is running at `http://127.0.0.1:5000` (this is the
default port used by Flask's development server). Note: the Docker daemon host
could be different.

API usage is shown in the `examples` folder.

See also:

- [xpublish docs](https://xpublish.readthedocs.io/)
