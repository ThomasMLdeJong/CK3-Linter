FROM alpine:3.11 AS builder

# Install dependencies
RUN set -eux \
 && apk add --no-cache bash gcc python3 python3-dev py3-pip musl-dev libffi-dev \
 && pip3 install --upgrade pip build

WORKDIR /src

# Copy your local files to the container
COPY . /src/

# Shell and build process
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN set -eux \
 && python3 -m build --wheel \
 && pip3 install dist/*.whl \
 && CK3-Lint --version \
 && find /usr/lib/ -name '__pycache__' -print0 | xargs -0 -n1 rm -rf \
 && find /usr/lib/ -name '*.pyc' -print0 | xargs -0 -n1 rm -rf
