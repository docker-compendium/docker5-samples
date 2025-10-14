# hello-world-python

## Fixed port mapping

```bash
$ docker build -t hello-world-python .
$ docker run -d --name hello-world-python -p 8080:8080 hello-world-python
$ open http://0.0.0.0:8080/
```

## Dynamic port mapping

```bash
$ docker build -t hello-world-python .
$ docker run -d -P --name hello-world hello-world-python
$ docker port hello-world

  8080/tcp -> 0.0.0.0:32772
```

open http://0.0.0.0:32772/ 
