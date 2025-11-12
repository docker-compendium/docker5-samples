docker build -t docbuc/python-legacy .
docker run -v "$(pwd)":/src/out -u "$(id -u):$(id -g)" docbuc/python-legacy
