# Secrets, data and configuration

Keep secrets outside every Git repository, including private Git. Ordinary runtime
bindings reuse existing GitHub Environment Secrets: `PROXMOX_APP_TOKEN`,
`APPLICATION_SSH_KEY`, `AUTOMATION_NODE_RED_API_TOKEN`, the existing
`FOUNDATION_AUTHENTIK_*` names, `FOUNDATION_PGADMIN_OAUTH_SECRET` and
`FOUNDATION_CLOUDFLARE_DNS_TOKEN` where their applications require them. The phase
runner compares existing private credential files and never rotates a mismatch.
Environment secret availability and exact existing names require adoption review.

The CloudBeaver database-tools variant keeps the existing
`FOUNDATION_PGADMIN_OAUTH_SECRET` binding and private `oauth-client-secret` input.
Its value must still match the selected OIDC client. Application recovery and
gateway cookie material are derived privately with separate purposes; this adds
no GitHub secret names and publishes no database password or client key.

All reusable-workflow edges declare and forward existing names explicitly. Deploy
and generic phase wrappers admit the two required common names and six optional
application names. Each guest requires only its own application names alongside
the common pair; Authentik SMTP remains optional. Retained PegaProx bootstrap names
are outside this ordinary runtime contract. The selected framework's final job
keeps its private Environment and guest-scoped application bindings. Caller name
presence does not prove a nonempty value; existing runtime validators remain the
value checks before target operations. These source declarations create no Secrets
and do not establish Environment value availability or native execution authority.

The retained Traefik service-discovery token stays in its existing private bootstrap
file. PegaProx's database key stays in its existing mode-600 private controller file;
its service-owned copy must match. Bitwarden's mode-600 runtime JSON file stays
external, with a private hash and final already-prepared database settings. No
initial account passwords are required by ordinary PegaProx CD.

Custom images, application data, database contents, HA/Node-RED credentials, Zigbee
network keys and radio backups are private runtime material. The stack neither
imports nor restores them. Before enabling a guest, complete its named prerequisites
and record acceptance in the private overlay. Existing restored applications need
their preserved paths and correct ownership before package or service changes.
Never accept a prerequisite merely to get past an error.

HA HTTP/listener/trusted-proxy conversion, Node-RED settings conversion and frontend
routing migration belong to separate prepared SSH work. Zigbee configuration and
radio identity must be preserved. Central IP/domain substitutions and narrow runtime
Secret delivery are the explicit exceptions, within their reviewed contracts.
Do not remove HA sensors or generate broad application configuration rewrites.

The MQTT guest selects `paths.mqtt_probe`, a controller-private mode0600 JSON file
containing one existing `username` and `password`. It is a read-only probe account
binding, not account creation or rotation. The framework hashes it as an input and
copies it privately for authenticated CONNECT plus anonymous-refusal verification.
The source file and retained broker password file must never enter Git.

Music Assistant uses the previously selected upstream `:latest` image. Preserve
its original data/provider credentials and the original pre-upgrade data copy
before any application schema upgrade; record the resolved image at deployment.
The ordinary deployment neither retrieves old data nor resets providers/accounts.
