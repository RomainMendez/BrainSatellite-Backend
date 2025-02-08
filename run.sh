#!/bin/sh

if [ -z "$PYTHON_ENTRYPOINT" ]; then
  echo "Error: PYTHON_ENTRYPOINT is not set or is empty."
  exit 1
fi

python $PYTHON_ENTRYPOINT