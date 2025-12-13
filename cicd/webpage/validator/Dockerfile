# Datei: cicd/webpage/validator/Dockerfile (docbuc/validator)
FROM eclipse-temurin:25-jre

WORKDIR /src
RUN apt-get update; \
  apt-get install -y --no-install-recommends wget; \
  wget -O /src/vnu.jar \
    "https://github.com/validator/validator/releases/download/latest/vnu.jar";\
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false;\
  rm -rf /var/lib/apt/lists/*; \
  adduser --system validator
USER validator
WORKDIR /home/validator
EXPOSE 8888
ENTRYPOINT ["java", "-jar", "/src/vnu.jar" ]
CMD ["--help"]
