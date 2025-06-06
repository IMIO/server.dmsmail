FROM harbor.imio.be/common/plone-base:6.1.1 AS builder

LABEL maintainer="iMio <devops@imio.be>"
ENV WHEEL=0.45.1 \
  PLONE_MAJOR=6.1 \
  PLONE_VERSION=6.1.1

# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  git \
  graphviz \
  graphviz-dev \
  libbz2-dev \
  libc6-dev \
  libffi-dev \
  libjpeg62-dev \
  libmemcached-dev \
  libopenjp2-7-dev \
  libpcre3-dev \
  libpq-dev \
  libreadline-dev \
  libssl-dev \
  libxml2-dev \
  libxslt1-dev \
  python3-dev \
  python3-pip \
  wget \
  zlib1g-dev

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

WORKDIR /plone

COPY --chown=imio *.cfg /plone/
COPY --chown=imio scripts /plone/scripts

RUN mkdir /plone/bin && chown imio:imio /plone/bin
RUN ln -s /usr/bin/pip3 /plone/bin/pip

RUN su -c "buildout -c docker.cfg -t 30 -N" -s /bin/sh imio


FROM harbor.imio.be/common/plone-base:6.1.1
ENV PIP=25.0.1 \
  WHEEL=0.45.1 \
  PLONE_MAJOR=6.1 \
  PLONE_VERSION=6.1.1 \
  HOSTNAME_HOST=local \
  PROJECT_ID=smartweb \
  PLONE_EXTENSION_IDS=plone.app.caching:default,plonetheme.barceloneta:default \
  DEFAULT_LANGUAGE=fr

VOLUME /data/blobstorage
WORKDIR /plone

# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  libjpeg62 \
  libmemcached11 \
  libopenjp2-7 \
  libpq5 \
  libtiff5-dev \
  libxml2 \
  libxslt1.1 \
  lynx \
  poppler-utils \
  rsync \
  wget \
  wv \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_amd64.deb > /tmp/dumb-init.deb && dpkg -i /tmp/dumb-init.deb && rm /tmp/dumb-init.deb
# COPY --from=builder /usr/local/bin/py-spy /usr/local/bin/py-spy
COPY --from=builder --chown=imio /plone .
COPY --from=builder /usr/local/lib/python3.12/dist-packages /usr/local/lib/python3.12/dist-packages
COPY --chown=imio zope_add_zeo.conf zope_add_async.conf zeo_add.conf zeo_async.conf /plone/
COPY --chown=imio docker-initialize.py docker-entrypoint.sh /

USER imio
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=10s --start-period=20s --retries=5 \
  CMD wget -q http://127.0.0.1:8081/ok -O - | grep OK || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["console"]