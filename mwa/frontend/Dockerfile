# Datei: mwa/frontend/Dockerfile (docbuc/mwa-fe)
FROM node:24 AS builder
WORKDIR /src/vue
COPY vue-project/package* /src/vue/
RUN chown -R node:node /src
USER node
RUN npm install
COPY --chown=node:node vue-project/ /src/vue/
RUN npm run-script build
COPY --chown=node:node dev-entrypoint.sh /src/
ENTRYPOINT [ "/src/dev-entrypoint.sh" ]
CMD [ "npm", "run", "dev", "--", "--host"]

FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=builder /src/vue/dist/ .
COPY default.conf /etc/nginx/conf.d/
RUN touch /var/run/nginx.pid && \
  chown -R nginx:nginx /var/run/nginx.pid && \
  apk add --no-cache wget
# USER nginx
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O - \
  http://localhost:8080/ || exit 1

