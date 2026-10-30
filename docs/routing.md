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
    "target": {"url": "http://${addresses.nas}:31763"},
    "middlewares": ["security-headers", "management-clients"]
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

The `udm` transport retains `server_name: ${domains.udm_backend}` and deliberately
omits `ca_file`. It renders only `serverName`, leaving trust to the Traefik
process's default root store while retaining hostname and certificate verification.
No UDM-specific CA input, staged `route-udm.pem` or transport CA mount is required.
The host route's hostname, aliases and middleware remain separate and unchanged;
the private site retains its existing backend-name binding. Proxmox keeps its
explicit CA input, and the existing verified PVE provider trust is unchanged.

This source change neither deletes a controller trust file nor activates a route.
Renderer tests use synthetic inputs and do not establish an actual Traefik-to-UDM
TLS handshake or accept `external-tls-trust-reviewed`. Route activation and native
trust/identity acceptance still require their separate reviewed qualification.

Traefik owns browser-facing HTTPS for NAS and PegaProx. Their routers keep
`websecure`, the automatic `letsencrypt` resolver, existing hostnames/aliases and
middleware. Internal NAS traffic uses HTTP on port 31763; PegaProx's managed
`pegaprox.web` endpoint uses HTTP on port 5000. The PegaProx route still references
that endpoint rather than declaring a second backend URL. Neither backend selects
a TLS transport, so their unused transport CA definitions, staged CA files and
mounts are absent. There is no manual NAS/PegaProx backend certificate lifecycle.
UDM and PVE remain verified HTTPS connections.

The internal HTTP hops provide no transport encryption. Browser-facing HTTPS
protects the browser-to-Traefik hop only; it does not protect credentials or session
data sent onward over HTTP. This is an explicit internal-network routing choice,
not a claim of an encrypted tunnel. Review the internal path, effective firewall
isolation and complete login/session behavior before native acceptance or activation.

PegaProx's closed runtime contract selects behind-proxy HTTP with
`PEGAPROX_BEHIND_PROXY=true`, `PEGAPROX_HOST=0.0.0.0` inside the container, and
`PEGAPROX_TRUSTED_PROXIES` set to the centrally selected ingress management address
as one exact `/32`. The published listener remains bound to the existing PegaProx
management address on port 5000, with only the exact ingress management `/32`
admitted by its TCP 5000 rule. Direct home-network access is removed so browser
clients reach the application through Traefik HTTPS. Data, key, account, resource and restart settings
are retained. The guest remains started and boots with the host at order 60,
independently of the container's `restart: always` policy. Its read-only loopback
health probe must use HTTP without following
redirects or calling setup/login, and still require an initialized closed setup.

Existing deployments must adopt matching stack/site route inputs: the managed
PegaProx endpoint uses HTTP on port 5000 and its route omits the optional TLS
transport. Route validation rejects HTTP with a TLS transport. Frontend readiness
checks the separately prepared address/gateway/MAC reply-routing settings; it does
not update backend URLs or TLS transport selections. An authorized normal
application reconcile replaces the container to apply the HTTP proxy environment
while retaining its image, key, account and data. A restart alone does not change
that environment; no backend certificate preparation or application database
configuration migration is needed.

Source compilation and synthetic renderer/health tests do not activate this mode.
The NAS HTTP response and proxy-header behavior support this source selection; a
complete browser login, automatic frontend certificate issuance and native service
acceptance remain separate checks. No prerequisite acceptance is granted by this
source change.

Compilation rejects global hostname/alias collisions, unknown endpoints or policy
references, public or foreign-interface backends, conflicting DNS records and
missing firewall permissions. It creates local Pi-hole records for all route names
and aliases pointing to ingress's frontend, while MQTT keeps its own published
service address. Public DNS, the external Pi-hole instance, upstream network policy
and real client resolution remain separate rollout checks.

Ingress egress and managed app ingress rules remain explicit. External host
firewalls are outside this stack's ownership. InfluxDB's isolated bridge therefore
has an explicit ingress NIC; cross-bridge reachability is not assumed. The `host`,
`nas` and `proxmox` routes select `management-clients`, limited to policy15 and
management25. The `pegaprox` route selects only `security-headers`; ingress also
admits `http_backend`, `frontend` and `policy_50` clients, which can reach PegaProx
through that route. Its backend port accepts only the exact ingress management
endpoint; browser clients use the Traefik route. Any
private-site restriction must be explicit, and an operator must review allowlist
changes before rollout.

This is stack schema `homelab-stack-v2` and site schema `homelab-site-v3`. Old
per-app discovery routes and the application-specific browser-route contract are
removed. There is no compatibility translation.
