FROM python:3.6-slim

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get -y upgrade &&  \
    apt-get install -qq -y \
    build-essential libpq-dev --no-install-recommends \
    python3-dev python3-pip python3-setuptools python3-wheel python3-cffi \
    && pip install --upgrade pip

WORKDIR /package

COPY package/ /package

RUN /usr/local/bin/pip install --editable .[dev]

# CMD tail -f /dev/null
CMD /usr/local/bin/pserve development.ini --reload
