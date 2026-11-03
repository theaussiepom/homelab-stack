# Database tools

The `db-tools` profile selects CloudBeaver Community with
`config.app.variant: cloudbeaver` and `stack.variant: cloudbeaver`. The logical
guest, infrastructure state, VMID, existing interfaces and completed PostgreSQL
custody relationship stay in place. Its application phase is `cloudbeaver`.
The framework retains the pgAdmin variant for previously selected profiles.

## Web access and sign-in

Only the OIDC authentication gateway is published on the guest's selected backend
address. CloudBeaver listens inside the private Compose network. The gateway
authenticates browser users through the selected identity provider, then supplies
the configured reverse-proxy identity headers. Browser traffic uses the existing
Traefik HTTPS route and automatic certificate resolver.

Use the canonical database-tools hostname for normal access. The previous pgAdmin
hostname has a separate compatibility route that temporarily redirects to the
canonical CloudBeaver home page before sign-in. It drops old paths and query
strings because pgAdmin bookmarks and OAuth callbacks do not belong to the new
application. Native acceptance includes an
unauthenticated redirect to the identity provider, rejection of forged identity
headers and a successful authenticated browser session.

CloudBeaver Community supports reverse-proxy header authentication. Its native
OpenID and SAML integrations belong to other editions; this composition uses the
separate gateway. See the upstream [authentication methods](https://github.com/dbeaver/cloudbeaver/wiki/Authentication-methods)
and [reverse-proxy authentication](https://github.com/dbeaver/cloudbeaver/wiki/Reverse-proxy-header-authentication)
documentation.

## Database connections

PostgreSQL and MariaDB publish their existing database listeners through the
ordinary named-service mechanism. The backend-only publications use TCP 5432 on
the PostgreSQL bridge and TCP 3306 on the MariaDB bridge. The compiler derives the
connection destinations and verifies both sides of the corresponding firewall
rules. The database listeners have no web routers.

Guest 202 retains its management, web-backend and PostgreSQL interfaces in their
existing order. A fourth interface reaches the existing MariaDB bridge. Its
address and MAC come from `addresses.db_tools_mariadb` and `mac.db-tools.3`.
The generic internal service names come from `hostnames.postgresql_database` and
`hostnames.mariadb_database`; private adoption can retain existing canonical names.

The initial connection entries contain server and database metadata. Users supply
their existing database credentials when connecting. The composition does not
create database users or change passwords, grants or application databases.
The PostgreSQL entry explicitly preserves its selected `sslmode: prefer`; an
internal DNS alias does not establish certificate validity. Retained client
certificate/key references require separate private qualification before claiming
that a new connection has the same transport and authentication behavior.

## Retained data and adoption

CloudBeaver uses its own workspace at `/srv/homelab/data/cloudbeaver`. The retained
`/srv/homelab/data/pgadmin` directory and existing database data remain intact.
Before adoption, qualify the new workspace, authentication inputs, capacity and
the exact old managed pgAdmin container's transition through the ordinary
deployment pipeline. Keep historical installation and custody evidence.

The private site supplies genuine prerequisites and reviewed input bindings.
Public compilation, synthetic tests and a successful source review establish the
source contract; target deployment and browser/database acceptance are recorded
separately. `db-tools` remains an independently disableable leaf. When selected,
it depends on both database guests, ingress and identity.

The profile increases guest memory to 2048 MiB and retains its one CPU, 4 GiB root
and 2 GiB data volume. CloudBeaver's 1536 MiB container limit includes a 1024 MiB
maximum Java heap; the gateway has a 128 MiB limit. Private adoption qualifies
actual free space and runtime behavior for the selected immutable images.

## Bounded certificate readiness

The ingress foundation selects `acme_dns_propagation_timeout_seconds: 2100` for
the Cloudflare DNS challenge. The pinned provider accepts integer seconds. This
allows a bounded period for a new hostname's cached negative DNS answers to
expire; it does not establish that caching caused a particular earlier failure.
Recursive propagation checks, normal browser TLS and the certificate store remain
unchanged. See the pinned [provider timeout implementation](https://github.com/go-acme/lego/blob/v5.5.2/providers/dns/cloudflare/cloudflare.go#L67).

Only the canonical CloudBeaver HTTPS check waits up to 2250 seconds for retries,
with 1200 retries, a 2 second delay and a 15 second per-request limit. The count is
large enough that immediate certificate failures do not exhaust it before the
timer. Curl can finish an already started request after its retry timer expires,
so the final transfer/backoff can extend that window slightly. It must still
validate the certificate and receive 302 without following redirects. The
existing 45 minute application-step cap remains; this is bounded tolerance, not
a guarantee that every initial installation fits that budget. Identity discovery,
Music health and other guest checks retain their existing limits. Source tests
remain separate from certificate and application acceptance after deployment.
