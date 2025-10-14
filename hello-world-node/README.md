# hello-world-node

## Fixed port mapping

```
$ docker build -t hello-world-node .
$ docker run -d -p 8080:8080 hello-world-node
$ open http://0.0.0.0:8080/
```

## Dynamic port mapping

```bash
$ docker build -t hello-world-node .
$ docker run -d -P --name hello-world hello-world-node
$ docker port hello-world

  8080/tcp -> 0.0.0.0:32772 
```

now open http://0.0.0.0:32772/ 
