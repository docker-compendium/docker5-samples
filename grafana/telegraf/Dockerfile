# Datei: grafana/telegraf/Dockerfile (docbuc/telegraf)
FROM telegraf:1.36
COPY telegraf.conf /etc/telegraf
COPY entrypoint.sh /
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
CMD ["telegraf"]

