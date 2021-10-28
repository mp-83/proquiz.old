FROM python:3.6-slim

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get -y upgrade &&  \
    apt-get install -qq -y \
    build-essential libpq-dev --no-install-recommends \
    python3-dev python3-pip python3-setuptools python3-wheel python3-cffi \
# libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info 
# iputils-ping curl procps postgresql-client-common wget curl npm \
    && pip install --upgrade pip

WORKDIR /package

# COPY server/requirements.txt requirements.txt
# RUN pip install -r requirements.txt


COPY package/ /package

RUN pip install --editable ".[dev]"

# CMD tail -f /dev/null
CMD python /package/server/app.py
# CMD /usr/local/bin/pserve development.ini --reload
