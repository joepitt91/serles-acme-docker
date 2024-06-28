# SPDX-FileCopyrightText: 2024 Joe Pitt
#
# SPDX-License-Identifier: GPL-3.0-only

FROM python:3.12
ENV ALLOWED_IPS=0.0.0.0/0,::/0 BLOCKED_IPS=0.0.0.0/32 CA_NAME=ManagementCA \
    CERT_PROFILE=SERVER EJBCA_API_VERIFY=false \
    EJBCA_API=https://ejbca:8443/ejbca/ejbcaws/ejbcaws?wsdl ENTITY_PROFILE=EMPTY \
    MYSQL_DATABASE=serles MYSQL_HOST=mysql MYSQL_PASSWORD=changeme MYSQL_PORT=3306 \
    MYSQL_USERNAME=serles USE_MYSQL=false VERIFY_PTR=false
EXPOSE 8000
LABEL org.opencontainers.image.authors="Joe Pitt <Joe.Pitt@joepitt.co.uk>" \
    org.opencontainers.image.base.name="hub.docker.com/_/python:3.12" \
    org.opencontainers.image.description="Docker wrapper of serles-acme ACME server for EJBCA." \
    org.opencontainers.image.licenses="GPL-3.0-only" \
    org.opencontainers.image.ref.name="serles-acme" \
    org.opencontainers.image.source="https://github.com/joepitt91/serles-acme-docker" \
    org.opencontainers.image.title="serles-acme" \
    org.opencontainers.image.version="1.1.0" \
    org.opencontainers.image.url="https://github.com/joepitt91/serles-acme-docker"

VOLUME [ "/etc/serles" ]
COPY configure.py /usr/local/sbin/configure.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY gunicorn_config.py /opt/serles/gunicorn_config.py
ENTRYPOINT [ "sh", "/usr/local/bin/entrypoint.sh" ]
HEALTHCHECK --timeout=3s CMD [ "curl", "-f", "http://localhost:8000/" ]
RUN python3 -m venv /opt/serles &&\
    . /opt/serles/bin/activate &&\
    python3 -m pip install --quiet --no-cache-dir --upgrade pip setuptools &&\
    python3 -m pip install --quiet --no-cache-dir pymysql serles-acme==1.1.0
