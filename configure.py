#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Joe Pitt
#
# SPDX-License-Identifier: GPL-3.0-only

"""Configure serles based on environment variables"""

from configparser import ConfigParser
from os import environ
from os.path import isfile


if __name__ == "__main__":
    config = ConfigParser()
    config.read("/etc/serles/config.ini")

    if "serles" not in config.sections():
        config.add_section("serles")
    if environ.get("USE_MYSQL") in ("1", "yes", "Yes", "y", "true", "True"):
        config.set(
            "serles",
            "database",
            f'mysql+pymysql://{environ.get("MYSQL_USERNAME")}:{environ.get("MYSQL_PASSWORD")}@'
            + f'{environ.get("MYSQL_HOST")}:{environ.get("MYSQL_PORT")}/'
            + environ.get("MYSQL_DATABASE"),
        )
    else:
        config.set("serles", "database", "sqlite:////etc/serles/db/serles.sqlite")
    config.set("serles", "backend", "serles.backends.ejbca:EjbcaBackend")
    config.set(
        "serles",
        "allowedServerIpRanges",
        "\n".join(environ.get("ALLOWED_IPS").split(",")),
    )
    config.set(
        "serles",
        "excludeServerIpRanges",
        "\n".join(environ.get("BLOCKED_IPS").split(",")),
    )
    if environ.get("VERIFY_PTR", "false") in ("1", "yes", "Yes", "y", "true", "True"):
        config.set("serles", "verifyPTR", "true")
    else:
        config.set("serles", "verifyPTR", "false")
    config.set("serles", "subjectNameTemplate", "CN={SAN[0]}")
    config.set("serles", "forceTemplateDN", "true")

    if "ejbca" not in config.sections():
        config.add_section("ejbca")
    config.set("ejbca", "apiUrl", environ.get("EJBCA_API"))
    if environ.get("EJBCA_API_VERIFY") in ("1", "yes", "Yes", "y", "true", "True"):
        config.set("ejbca", "caBundle", "/etc/serles/ca.bundle")
        if not isfile("/etc/serles/ca.bundle"):
            raise FileNotFoundError(
                "EJBCA TLS is verification enabled, but /etc/serles/ca.bundle missing"
            )
    else:
        config.set("ejbca", "caBundle", "none")
    config.set("ejbca", "clientCertificate", "/etc/serles/client.pem")
    if not isfile("/etc/serles/client.pem"):
        raise FileNotFoundError(
            "EJBCA client certificate, /etc/serles/client.pem, is missing"
        )
    config.set("ejbca", "caName", environ.get("CA_NAME"))
    config.set("ejbca", "endEntityProfileName", environ.get("ENTITY_PROFILE"))
    config.set("ejbca", "certificateProfileName", environ.get("CERT_PROFILE"))
    config.set("ejbca", "entityUsernameScheme", "{CN}")
    config.set("ejbca", "entityPasswordScheme", "{random}")

    with open("/etc/serles/config.ini", "w", encoding="utf-8") as f:
        config.write(f)
