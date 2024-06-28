#!/usr/bin/env python3

"""Check if serles-acme is up"""

from sys import exit as sys_exit

from requests import get

if not get("http://127.0.0.1:8000/", timeout=3).ok:
    # signal unhealthy to the Docker Engine
    sys_exit(1)
