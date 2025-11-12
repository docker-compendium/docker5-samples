FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends\
  composer \
  php8.4 \
  php8.4-dom \
  php8.4-zip \
  unzip \
  && rm -rf /var/lib/apt/lists/*
RUN useradd -ms /bin/bash php8
WORKDIR /home/php8
USER php8
RUN composer require zendframework/zend-feed \
  zendframework/zend-http
COPY printheadlines.php ./
CMD ["php", "printheadlines.php"]
