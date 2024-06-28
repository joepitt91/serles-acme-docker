<!--
SPDX-FileCopyrightText: 2024 Joe Pitt

SPDX-License-Identifier: GPL-3.0-only
-->

# serles-acme Docker Image

Docker wrapper of [serles-acme](https://github.com/dvtirol/serles-acme) ACME server for EJBCA.

To get started:

1. Create an EJBCA client certificate:
    1. `mkdir -p ejbca/csr ebjca/cert` (assuming `./ejbca` is mapped to `/mnt/persistent/` within
        the EJBCA container).
    2. `chown -R 10001:10001 ejbca/csr`.
    3. `chown -R 10001:10001 ejbca/cert`.
    4. `docker compose exec -it ejbca ejbca.sh gencsr --destination /mnt/persistent/csr/ --keyalg RSA --keyspec 3072 --subjectdn "CN=ACME Server"`.
    5. In the EJBCA RA WebUI create an end entity for the client certificate to issue against,
        replacing `acmeserver` and `strong-Pa55w0rd_here` below with the end entity's details.
    6. `docker compose exec -it ejbca ejbca.sh createcert --username acmeserver --password strong-Pa55w0rd_here -c /mnt/persistent/csr/certificateSigningRequest.csr -f /mnt/persistent/cert/acme.crt`
2. Authorise the client certificate to issue certificates:
    1. `openssl x509 -text -noout -in ejbca/cert/acme.crt` copy the certificate serial number.
    2. In the EJBCA WebUI, go to **System Functions** > **Roles and Access Rules**.
    3. Click **Add**, and give the new role a name, e.g. `ACME`, and click **Add**.
    4. Click **Members** next to the new role, paste the serial number into the **Match Value** box,
        and click **Add**.
    5. Click **Edit Access Rules** and set **Role Template** to **RA Administrators**, select the
        appropriate **Authorized CAs** and **End Entity Profiles**, and click **Save**.
3. Save the client certificate to `./serles-acme/client.pem`:
    1. `mkdir -p ./serles-acme`
    2. `cat ejbca/cert/acme.crt ejbca/csr/privkey.pem > serles-acme/client.pem`
4. Add the `serles-acme` service as shown in
    [docker-compose.yml](https://github.com/joepitt91/serles-acme-docker/blob/main/docker-compose.yml),
    overriding any Environment Variables (see below).
5. Bring the `serles-acme` server up: `docker compose up -d serles-acme`.
6. Check the logs to ensure everything is OK: `docker compose logs serles-acme -f`.
7. Stand up an HTTPS reverse proxy in front of `serles-acme` with a trusted certificate.
8. Issue certificates using `certbot --server https://reverse.proxy.tld/directory ...`.
    * After initial setup, the reverse proxy can use the same to maintain its own certificate.
    * If the reverse proxy is using an internal certificate then the snapd and Docker versions of
        `certbot` may fail to validate it as these use bundled CA Trust Lists.

## Environment Variables

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `ALLOWED_IPS` | Subnets to allow requests from (comma-separated). | `0.0.0.0/0,::/0` (unrestricted) |
| `BLOCKED_IPS` | Any exclusions to to `ALLOWED_IPS` (comma-separated). | `0.0.0.0/32` (invalid IP) |
| `CA_NAME` | The name of the CA to use for signing issued certificates. | `ManagementCA` |
| `CERT_PROFILE` | The EJBCA Certificate Profile to use for issued certificates. | `SERVER` |
| `EJBCA_API_VERIFY` | Whether to do TLS verification when speaking to the EJBCA API. | `false` |
| `EJBCA_API` | The EJBCA Web Service endpoint URL (must include `https://` and `/ejbca/ejbcaws/ejbcaws?wsdl`). | `https://ejbca:8443/ejbca/ejbcaws/ejbcaws?wsdl` |
| `ENTITY_PROFILE` | The EJBCA End Entity Profile to use when issuing certificates. | `EMPTY` |
| `MYSQL_DATABASE` | When MySQL is enabled, the database to connect to. | `serles` |
| `MYSQL_HOST` | When MySQL is enabled, the hostname to connect to. | `mysql` |
| `MYSQL_PASSWORD` | When MySQL is enabled, the password to authenticate with. | `changeme` |
| `MYSQL_PORT` | When MySQL is enabled, the TCP port to connect to. | `3306` |
| `MYSQL_USERNAME` | When MySQL is enabled, the username to authenticate as. | `serles` |
| `USE_MYSQL` | Whether to use MySQL for Serles' database, otherwise a SQLite3 database file is used. | `false` |
| `VERIFY_PTR` | Whether to verify that a correct PTR record exists during validation.: | `false` |

## EJBCA API TLS Verification

It is recommended to verify the EJBCA certificate when Serles talks to the EJBCA API, to do this:

1. Save the PEM-encoded CA Certificate (including any required chain certificates) for the EJBCA API
    (`ManagementCA` by default) to `./serles-acme/ca.bundle`.
2. Set the `EJBCA_API_VERIFY` Environment Variable to `true`.
3. Recreate the container with `docker compose up -d --force-recreate serles-acme`.
