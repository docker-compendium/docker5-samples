FROM node:24
WORKDIR /src
COPY ./src/package.json /src/
RUN npm i --omit=dev
COPY /src/ /src/
EXPOSE 3000
USER node
CMD [ "node", "/src/bin/www" ]

