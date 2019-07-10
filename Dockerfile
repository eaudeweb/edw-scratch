FROM python:2.7-slim

ARG REQFILE=requirements-dep.txt

ENV PROJ_DIR=/var/local/scratch/

RUN runDeps="gcc vim netcat libpq-dev mysql-client default-libmysqlclient-dev" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*

RUN mkdir -p $PROJ_DIR/instance
COPY requirements.txt requirements-dep.txt requirements-dev.txt $PROJ_DIR
WORKDIR $PROJ_DIR

RUN pip install -r $REQFILE

COPY . $PROJ_DIR

ENTRYPOINT ["./docker-entrypoint.sh"]
