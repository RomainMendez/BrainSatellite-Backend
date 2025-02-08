ARG BASE_IMAGE="python:3.12.9-alpine3.21"

FROM ${BASE_IMAGE}

WORKDIR /usr/src/app
COPY . .

RUN pip install -r requirements.txt

ENV PYTHON_ENTRYPOINT=""

ENTRYPOINT [ "./run.sh" ]
CMD []