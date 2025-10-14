# hello-world-php

## Fixed port mapping

```bash
$ docker build -t hello-world-php .
$ docker run -d --name hello-world-php -p 8080:80 hello-world-php
$ open http://0.0.0.0:8080/
```

## Dynamic port mapping

```bash
$ docker build -t hello-world-php .
$ docker run -d -P --name hello-world hello-world-php
$ docker port hello-world

  80/tcp -> 0.0.0.0:32772
```

open http://0.0.0.0:32772/ 
