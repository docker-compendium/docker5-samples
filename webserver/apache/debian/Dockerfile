# Datei: webserver/apache/debian/Dockerfile (docbuc/apache)
FROM debian:trixie

RUN apt-get update && apt-get install -y \
  apache2 \
  && rm -rf /var/lib/apt/lists/*
RUN a2enmod rewrite headers
COPY default.conf /etc/apache2/sites-enabled/
COPY html /var/www/html
EXPOSE 80
CMD [ "/usr/sbin/apache2ctl", "-DFOREGROUND" ]
