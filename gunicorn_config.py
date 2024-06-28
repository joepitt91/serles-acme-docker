#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Joe Pitt
#
# SPDX-License-Identifier: GPL-3.0-only

# pylint: disable=invalid-name

"""Gunicorn configuration for Serles"""

accesslog = "-"
bind = "0.0.0.0:8000"
disable_redirect_access_to_syslog = True
forwarded_allow_ips = "*"
workers = 1
