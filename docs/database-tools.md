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

The database-tools guest declares management, web-backend and PostgreSQL interfaces in their
existing order. A fourth interface reaches the existing MariaDB bridge. Its
address and MAC come from `addresses.db_tools_mariadb` and `mac.db-tools.3`.
Bridge, VLAN and prefix values are shared logical-network bindings supplied by the consumer.
The generic internal service names come from `hostnames.postgresql_database` and
`hostnames.mariadb_database`; private adoption can retain existing canonical names.

The original connection entries contain server and database metadata. Users can
still supply their existing database credentials for those entries. The separate
`managed_connections` entries add dedicated administration accounts without
changing those metadata entries or existing application/root accounts.
The PostgreSQL entry explicitly preserves its selected `sslmode: prefer`; an
internal DNS alias does not establish certificate validity. Retained client
certificate/key references require separate private qualification before claiming
that a new connection has the same transport and authentication behavior.

## Dedicated administration connections

Each native database profile declares a `config.app.database_administrators`
entry with a logical account ID, consumer-bound username and credential ID,
`source_guest: db-tools`, `access: server-administration` and `transport: tls`.
The compiler derives addresses and account linkage from the existing named
database publication and selected guest interfaces. The native database stack
remains null; there is no new database container or deployment engine.

The selected capability is unrestricted PostgreSQL SUPERUSER and MariaDB global
ALL with GRANT, scoped to the selected database-tools source. PostgreSQL
SUPERUSER includes server-file and program powers. These are dedicated
administration credentials; application/root credentials are neither reused nor
rotated. Foreign account collisions, credential drift and changed ownership
refuse. Ordinary input preparation retains one create-once private credential
record per declared account and binds its value into the immutable ordinary
input; no new GitHub secret names are required.

CloudBeaver's new `postgresql-admin` and `mariadb-admin` entries reference those
logical account IDs through named service bindings. The framework writes a native datasource file under the existing closed
workspace. That managed file contains the saved credentials in plaintext at
rest and is private to the service; it is not an encrypted-at-rest guarantee.
The existing resource manager remains enabled (its default is true). It does not invoke a recovery/admin bootstrap or expose saved
database passwords in Git, logs or container environment. Authorized users behind
the existing identity restriction share these administration connections. Their
TLS and exact-source PostgreSQL HBA boundaries cover ordinary and physical
replication connections, followed by local/IPv4/IPv6 rejection for other sources.
This preserves the original HBA tail. The managed datasource transport is
separate from the original metadata-only PostgreSQL
`sslmode: prefer` entry. Source qualification does not establish a successful
target SQL login, grants or browser session.

The managed PostgreSQL connection requires TLS, SCRAM-SHA-256 authentication and
TLS channel binding (`sslmode: require`, `requireAuth: scram-sha-256` and
`channelBinding: require`). Managed MariaDB uses `sslMode: verify-full` with
PARSEC's password-bound verification of the automatically generated server
certificate. This zero-configuration mode does not introduce a CA or manual
certificate lifecycle. Readiness checks the selected packaged PostgreSQL 42.7
driver has patch 13 or later and refuses conflicting driver overrides or caches.
Dedicated accounts require an already commissioned, running, TLS-enabled
database; this capability does not commission or recover a database server.

The CloudBeaver profile declares one official MariaDB Connector/J artifact in
`cloudbeaver.mariadb_jdbc`: its version, SHA-256 and the selected image's loader
filename. Ordinary application deployment downloads the checksum-verified vendor
artifact and mounts that single file read-only at the declared compatibility
path. The source filename follows the selected driver version; the image loader
filename can retain the image's older basename. This does not replace the image
or add a second driver to its classpath. The selected 3.5.11 correction prevents
the Properties-based connection password from appearing in the JDBC metadata
URL. It is required for managed MariaDB connections; metadata-only and
PostgreSQL-only compositions add no MariaDB override. Local
driver qualification does not establish the target application's loaded driver
or a successful browser connection; runtime health verifies the selected artifact
and the managed database connection separately.

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
it depends on both database guests and ingress. Identity availability is required
for interactive sign-in, not for deploying the guest. The profile supplies explicit
consumer-bound authorization, token, userinfo and JWKS URLs with RS256, avoiding
startup discovery. Issuer, audience, signature/JWKS, nonce, PKCE and verified-email
checks remain enforced; no account or authentication policy is changed.

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
a guarantee that every initial installation fits that budget. CloudBeaver retains
its local closed-setup/gateway readiness and the canonical HTTPS redirect check; it
does not wait for a live identity-discovery request. Music health and other guest
checks retain their existing limits. Source tests
remain separate from certificate and application acceptance after deployment.
