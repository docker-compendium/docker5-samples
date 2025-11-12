FROM golang:1.25

ENV TZ=Europe/Vienna
WORKDIR /app

# cache modules
COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY printheadlines.go .
RUN go build -v -o printheadlines ./printheadlines.go

CMD ["/app/printheadlines"]
