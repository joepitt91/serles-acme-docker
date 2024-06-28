#!/bin/bash

# SPDX-FileCopyrightText: 2024 Joe Pitt
#
# SPDX-License-Identifier: GPL-3.0-only

set -e
python3 /usr/local/sbin/configure.py
mkdir -p /etc/serles/db/
chmod 775 /etc/serles/db/
chown -R nobody:nogroup /etc/serles/*
runuser -u nobody -- /opt/serles/bin/gunicorn -c /opt/serles/gunicorn_config.py "serles:create_app()"
