# xpublish standalone demo

## Build and run

```shell
git clone https://github.com/ESM-VFC/xpublish-standalone-demo.git
cd xpublish-standalone/
docker build -t xpublish-standalone-demo
docker run -p 9000:9000 xpublish-standalone-demo
```

This will start serving an Xarray example dataset on `http://0.0.0.0:9000`.
See [start_xpublish_standalone.py](start_xpublish_standalone.py) for details.
