ARG BASE_IMAGE="python:3.12.9-alpine3.21"

FROM ${BASE_IMAGE}

WORKDIR /usr/src/app
COPY . .

RUN ./build_environment.sh

ENV PYTHON_ENTRYPOINT = ""

ENTRYPOINT [ "./run.sh" ]