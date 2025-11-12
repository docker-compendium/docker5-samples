FROM eclipse-temurin:25
RUN useradd -r java
WORKDIR /src
RUN chown java /src
USER java
ENV JSOUP_VER=1.21.2

ADD --chown=java:java https://jsoup.org/packages/jsoup-$JSOUP_VER.jar /src
COPY printheadlines.java /src/
RUN javac -cp /src/jsoup-$JSOUP_VER.jar:. \
  printheadlines.java
SHELL ["/bin/bash", "-c"]
CMD java -cp jsoup-$JSOUP_VER.jar:. printheadlines

