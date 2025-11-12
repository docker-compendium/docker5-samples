FROM golang:1.25-alpine AS dev
RUN apk add --no-cache tzdata
ENV TZ=Europe/Vienna
WORKDIR /app
RUN go install github.com/air-verse/air@latest
RUN go install github.com/go-delve/delve/cmd/dlv@latest
# cache modules
COPY go.mod go.sum ./
RUN go mod download && go mod verify
COPY . .
RUN go build -o ./api-server
CMD ["air", "-c", ".air.toml"]


FROM alpine:latest AS runner
RUN apk add --no-cache tzdata
ENV TZ=Europe/Vienna
WORKDIR /app
COPY --from=dev /app/api-server .
EXPOSE 8000
ENTRYPOINT ["./api-server"]

