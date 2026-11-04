# CloudBeaver profiles

`cloudbeaver` is an independent app profile owning CloudBeaver Community and its
OIDC gateway. The site places it on a guest, binds its web/private/database roles,
workspace, canonical HTTPS origin and authentication policy, and selects named
database endpoints. There is no fixed database-tools guest or mandatory peer app
name. Deployment waits are explicit connection/readiness choices; interactive
identity-provider availability is not inferred as a startup dependency.

Only the authentication gateway is published. Community stays on the owned private
network. The gateway validates issuer, audience, signatures/JWKS, nonce, PKCE and
verified email, then supplies the closed identity headers. Explicit OIDC endpoints
avoid discovery at startup. The framework owns generated gateway configuration;
a profile cannot supply arbitrary environment, commands, auth headers or mounts.
External authorization policy and the canonical hostname belong to the site.

The application health contract retains local closed setup, private gateway
readiness and selected normal HTTPS redirect checks. A source fixture is not
actual browser sign-in, certificate issuance or SQL acceptance. Configured bounded
certificate readiness preserves normal TLS and propagation checks; it is not an
installation-time guarantee.

## Connections and dedicated administration

Metadata connections and managed administration connections are separate named
roles. Metadata entries retain their explicitly selected database/transport values
and let users supply credentials. Managed connections select an explicit account
and named server endpoint; their source address is resolved from a declared
physical role. A hostname does not establish certificate identity or authorize a
grant. Connections do not create firewall policy.

The optional managed capability is unrestricted PostgreSQL SUPERUSER or MariaDB
global ALL with GRANT. PostgreSQL SUPERUSER includes server-file and program
powers. Sites must deliberately select that capability and its access policy.
Accounts are dedicated create-once selections; app/root credentials are neither
reused nor rotated. Foreign account collisions, changed identity or credential
drift refuse. This capability requires an already commissioned, running,
TLS-enabled database; it does not initialize or recover a database server.

Managed PostgreSQL uses TLS, SCRAM-SHA-256 and required channel binding. Its
exact-source TLS HBA boundary covers ordinary and physical replication, followed
by local/IPv4/IPv6 rejection for other sources, while preserving the authored base
HBA tail. Managed MariaDB uses PARSEC and `sslMode: verify-full` with the vendor's
password-bound verification of its automatically generated certificate. These
capabilities introduce no manual certificate/CA lifecycle.

`cloudbeaver-mariadb-admin` is the explicit profile variant for managed MariaDB.
It carries the library-owned closed Connector/J 3.5.11 declaration: version,
SHA-256 and the pinned image's compatibility filename. Application CD verifies the
official artifact and mounts one replacement file read-only; it does not change
the image or add a second jar. The generic profile omits this artifact, and a site
cannot replace the vendor version policy. Runtime health verifies the loaded
driver and selected connection separately. See [the profile selection guide](composition.md).

## Saved credentials and retained state

The framework writes a native managed datasource file in the explicitly bound
workspace. It contains saved passwords in **plaintext at rest**, private to the
service; this is not encrypted storage. The resource manager remains enabled.
The selected mode does not invoke recovery/admin bootstrap or place database
passwords in Git, container environment or application logs. Authorized users
share the selected administration connections.

Retained transitions require the exact old owned runtime identity and preserve
its data. Fresh instances do not require a retired pgAdmin image. Existing
workspace, credential and receipt drift is refused rather than silently adopted.
Use [adoption checks](adoption.md) before a retained update; record actual browser,
SQL, TLS and grant acceptance after authorized deployment.
