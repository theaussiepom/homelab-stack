# Secrets, data and configuration

Keep secrets outside every Git repository, including private Git. Ordinary runtime
bindings reuse existing GitHub Environment Secrets: `PROXMOX_APP_TOKEN`,
`APPLICATION_SSH_KEY`, `AUTOMATION_NODE_RED_API_TOKEN`, the existing
`FOUNDATION_AUTHENTIK_*` names, `FOUNDATION_PGADMIN_OAUTH_SECRET` and
`FOUNDATION_CLOUDFLARE_DNS_TOKEN` where their applications require them. The phase
runner compares existing private credential files and never rotates a mismatch.
Environment secret availability and exact existing names require adoption review.

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
