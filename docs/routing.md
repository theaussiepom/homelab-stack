# HTTP routes

Applications declare named HTTP endpoints. The stack's top-level `routes` map
selects which endpoints have hostnames. The private site can add or override routes
and central values. The same endpoint contract applies to native services and
Docker applications; Docker labels are not another routing authority.

A native or Docker app profile exposes an endpoint:

```json
{
  "app": {
    "endpoints": {
      "influxdb": {"web": "http://${addresses.influxdb_backend}:8086"}
    }
  }
}
```

The separate route map references it:

```json
{
  "influxdb": {
    "host": "influx.${domains.secondary}",
    "target": {"endpoint": "influxdb.influxdb.web"},
    "middlewares": ["security-headers"]
  },
  "nas": {
    "host": "nas.${domains.secondary}",
    "aliases": ["nas.${domains.primary}"],
    "target": {"url": "https://${addresses.nas}:31764"},
    "middlewares": ["security-headers", "management-clients"],
    "transport": "nas"
  }
}
```

A reference is `guest.application.endpoint`. Apps own their endpoint URLs; routes
own hostnames, aliases and middleware selection. External URLs select private
literal IPv4 addresses and an optional port. Backend paths, credentials, queries
and fragments are rejected. Managed guest addresses must use endpoint references,
so an external URL cannot bypass the guest's inbound firewall validation.

Managed routes become `traefik.*: value` lines in the owning guest's Proxmox
Description/Notes. External routes become routers and services in ingress's
file-provider configuration. Both use HTTPS on `websecure`, the `letsencrypt`
resolver, priority 10 and `security-headers@file` by default. Traefik forwards
WebSocket upgrades without a separate route type. App authentication stays with
the app: Node-RED retains native Authentik OIDC.

`middlewares` is an ordered list of names. Its default is `["security-headers"]`;
an explicit empty list selects no middleware. Definitions live centrally in
`guests/ingress/profile.json` under `stack.routing.middlewares`, with private
changes under `guests.ingress.stack.routing.middlewares`. Each name contains one
native Traefik middleware object, including types added later; there is no Python
enumeration of middleware types. Names are validated and references must exist.
The framework owns the default security headers. Custom plugin middleware also
needs its plugin installed and qualified separately.

TLS `transports` live beside middleware definitions. A transport may select
`server_name`, `ca_file`, or both. Its public CA file is a controller input, copied
read-only into ingress and referenced by its generated ServersTransport. TLS
verification stays enabled. Public CA trust and backend hostname matching must be
reviewed before accepting `external-tls-trust-reviewed`; a downloaded certificate
alone is not independent trust. Never place private keys or passwords in routes,
Notes, middleware definitions or Git.

PegaProx serves HTTPS on port 5000. Its managed endpoint uses that protocol, and
the route selects the central `pegaprox` transport. The transport verifies
`prox.${domains.secondary}` using the public trust bundle at
`/usr/local/share/ca-certificates/homelab-pegaprox.crt` on the controller. Ingress
stages this as `route-pegaprox.pem`, mounts it read-only, and references it from
`pegaprox@file` in the guest's Notes. Include this backend in the existing
state-and-trust review: independently verify the certificate/issuer and matching
DNS SAN before adoption. A default self-signed certificate without a matching
SAN needs separate certificate preparation; ordinary CD does not issue or replace
the application's retained certificate. Missing trust input prevents staging.

Compilation rejects global hostname/alias collisions, unknown endpoints or policy
references, public or foreign-interface backends, conflicting DNS records and
missing firewall permissions. It creates local Pi-hole records for all route names
and aliases pointing to ingress's frontend, while MQTT keeps its own published
service address. Public DNS, the external Pi-hole instance, upstream network policy
and real client resolution remain separate rollout checks.

Ingress egress and managed app ingress rules remain explicit. External host
firewalls are outside this stack's ownership. InfluxDB's isolated bridge therefore
has an explicit ingress NIC; cross-bridge reachability is not assumed. Management
UI routes currently select `management-clients`, limited to the declared policy15
and management25 networks. Review that policy with the private site before rollout.

This is stack schema `homelab-stack-v2` and site schema `homelab-site-v3`. Old
per-app discovery routes and the application-specific browser-route contract are
removed. There is no compatibility translation.
