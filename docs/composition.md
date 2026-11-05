# Use and extend the library

The site chooses instances and placement. The library supplies profiles and
supported defaults; the framework owns validation, resolution and deployment.
Read [the source layout](../README.md) and start with an explicitly synthetic
example rather than copying a guest bundle.

## Use a profile

An instance names its profile, guest and lifecycle. Roles bind to named guest
interfaces, guest loopback or an owned app network. Storage binds to an explicit
guest volume or root-filesystem data declaration.

The site's `guests` and `apps` maps may reference complete typed documents:

```yaml
guests:
  resolver: {source: guests/resolver.yaml}
apps:
  recursive_dns: {source: apps/recursive_dns.yaml}
```

The guest document starts with `schema: homelab-components-v1` and `kind: guest`;
the app-instance document uses `kind: app`. Each contains the same complete body
as its inline form. Paths are relative to the site file's directory, including
when the referenced document is in a nested directory. There are no partial
overlays, recursive includes or defaults merged into a reference. The library's
`apps/` directory contains reusable profiles; these site documents select actual
instances of those profiles. Every consumed file is pinned by the framework.

The [minimal example](../site.example.yaml) selects Unbound independently of
Pi-hole. The
[alternate layout](../examples/site.second.yaml) selects several resolver
instances and HA without Node-RED, databases, MQTT, identity or ingress.

To add a second resolver on the same guest, choose another stable instance ID
and its supported `publish_port`, as the alternate example does. The profile's
container listener stays unchanged. Different labels do not rename state,
services, projects, networks, mounts or credentials.

Fresh Unbound selects no storage bindings and uses the selected image's packaged
config. A retained instance binds its existing config explicitly; named optional
roles cover existing dev/var and control files with fixed writable/read-only
types. Pi-hole similarly has an optional FTL database role. An empty mount is
not a supported substitute for initialization.

## Bind a connection

Connections select explicit app endpoints or declared external targets. They do
not copy addresses from another app or automatically create dependencies.

- A broker's backend and frontend are advertisements of its declared listener.
  A saved hostname can select its DNS exposure while the runtime target selects
  the backend endpoint.
- Pi-hole selects a managed or external upstream. A local Unbound connection uses
  an explicit guest-loopback source role.
- Optional HA recorder, metrics and broker integrations are absent until selected.
- Authentication/login references do not imply startup waits.
- Guest preparation readiness is explicit and uses the guest's control interface;
  context DNS references alone are values, not dependencies.

CloudBeaver's `cloudbeaver-mariadb-admin` variant carries the library's closed
MariaDB JDBC artifact declaration for an explicitly managed MariaDB admin
connection. It uses the same adapter, runtime and authentication requirement as
`cloudbeaver`; the generic profile omits that conditional artifact. The site
selects the profile and connection, rather than declaring another vendor version.
The compatibility filename names the one existing image slot; verified replacement
bytes carry the declared driver version. This source choice does not change an
image or qualify a deployment by itself.

Actual network policy is selected separately. Optional role-bound policy
fragments never install themselves or infer a firewall grant.

Use purpose names such as `http_backend_egress` and `mqtt_backend_ingress` for
shared fragments. The two resolver DNS fragments preserve their explicit UDP-first
or TCP-first order. Package-download fragments describe traffic intent; package
signature verification remains a software requirement.

Sites can name an ordered address group once and bind it to a policy role:

```yaml
address_groups:
  trusted_clients:
    members:
    - network: services
    - 192.0.2.9
policies:
  network:
    admin_web_ingress:
      rules:
      - direction: in
        proto: tcp
        port: '443'
        source: {address_group: clients}
# In the selected guest's network_policy:
# - policy: admin_web_ingress
#   address_groups: {clients: trusted_clients}
```

Members may be literal IPv4 addresses/CIDRs, named site networks or other named
address groups. Expansion preserves order and duplicates. A rule with source and
destination groups expands source first, then destination. An `ip-allow-list`
middleware may reference the same site group directly in its `ranges` list.
Unknown references, cycles, unused role bindings and oversized expansions refuse.
Groups create neither grants nor readiness dependencies. The two examples reuse
their existing internet destination range without changing policy rows or ports.

HTTPS exposures explicitly name an app endpoint and the selected ingress
endpoint, domain and authentication policy. Native broker DNS uses a separate
DNS-only exposure; it does not create a TCP router. An app origin or saved
connection hostname can refer to a named exposure without copying its domain.
Internal dashboard endpoints expose no invented container listener. Selecting a
connection or exposure does not grant network access or infer an identity wait.

Native database profiles declare memory reservations for admission. The current
PostgreSQL and InfluxDB reservations are 1792 MiB each; MariaDB reserves 768 MiB.
These preserve the existing dedicated 2048/1024 MiB guest budgets after the
explicit 256 MiB OS reserve. They are placement policy, not measured consumption
or load qualification. Co-location must fit the combined declared reservations. PegaProx additionally
requires a minimum 512 MiB OS reserve, preserving its existing admission floor;
the effective guest reserve is the maximum of its explicit reserve and selected
runtime requirements.

## Add a reusable profile

1. Choose an existing supported framework adapter. If a capability is missing,
   add its contract, renderer and lifecycle support to the framework first.
2. Author `apps/ID.yaml` with the component schema and `kind: app-profile`.
   Declare roles, real listeners, advertised endpoints, storage, connections and
   capabilities supported by that adapter. Helpers stay owned by the app.
3. Reference named software, runtime and health declarations. Keep image versions
   and policies in `images.json`; use [explicit public variants](public-images.md)
   instead of a silent fallback from a retained archive.
4. Register the profile in `stack.json` with a confined whole-definition source
   reference. Do not add a private parser, template language or Compose escape.
5. Document required and conditional bindings, fresh/update behavior and supported
   dependency declarations. Add definition tests and focused integration coverage
   following [the testing guide](testing.md).

The root Zabbix capability retains its existing owned credential generation and
records. Its optional raw secret role does not introduce a new required file or
environment secret for a site selecting that capability.

Application data and historical records remain consumer-owned. No profile
declares a real VMID, MAC, VLAN, domain, account credential or acceptance result.
Raw public assets keep their exact bytes; native configuration comes from typed framework adapters.
Read [the update checks](adoption.md) and [secret boundaries](secrets.md) before
binding retained state.

## Generate the selected composition

Use the immutable selected framework, with locked dependencies. Both compilation
and workflow generation name the actual site:

```sh
python3 "$FRAMEWORK/blueprints/compile.py" --stack . --site site.example.yaml --check
python3 "$FRAMEWORK/blueprints/workflows.py" --stack . --site site.example.yaml --check
```

The consumer generates from its own site, not this starter's guest graph. There
is one guest job with short app steps, and no global phase barrier. Generated
files are not hand edited. Native deployment uses the consuming site's protected CD
after its required review, authorization and admission checks.
