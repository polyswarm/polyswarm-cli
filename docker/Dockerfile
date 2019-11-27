FROM python:3.6-stretch
LABEL maintainer="PolySwarm Developers <info@polyswarm.io>"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN set -x && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN set -x && python setup.py install

ENTRYPOINT ["polyswarm"]

CMD ["-h"]

