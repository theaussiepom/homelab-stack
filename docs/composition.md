# Use and extend the library

The site chooses instances and placement. The library supplies profiles and
supported defaults; the framework owns validation, resolution and deployment.
Read [the source layout](../README.md) and start with an explicitly synthetic
example rather than copying a guest bundle.

## Use a profile

An instance names its profile, guest and lifecycle. Roles bind to named guest
interfaces, guest loopback or an owned app network. Storage binds to an explicit
guest volume or root-filesystem data declaration.

The [minimal example](../site.example.yaml) selects Unbound without
Pi-hole or historical commissioning evidence. The
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

Retained data and evidence remain consumer-owned. No profile declares a real
VMID, MAC, VLAN, domain, account credential or admission result. Raw public assets
keep their exact bytes; native configuration comes from typed framework adapters.
Read [the adoption checks](adoption.md) and [secret boundaries](secrets.md) before
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
