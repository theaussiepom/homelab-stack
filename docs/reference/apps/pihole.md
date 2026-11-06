[Documentation](../../README.md) / [Reference](../README.md)

# Pi-hole

Provide DNS filtering and a web UI. Select an upstream resolver explicitly; Unbound is one possible independent upstream.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: pihole` |
| Adapter | `pihole` |
| Owned containers | `pihole` |
| Multiple instances | One Pi-hole per guest: the managed-record sidecar is a fixed owned leaf, and DNS/web host sockets must not collide. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [pihole.yaml](../../../apps/pihole.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The optional upstream interface role becomes necessary when binding the required upstream connection. A same-guest Unbound target uses guest-loopback; a remote target uses a physical role. Context DNS is a value and does not create that connection or a wait.

## First installation

Requires a prepared Pi-hole configuration directory and explicit upstream. This profile does not generate a complete new Pi-hole configuration or adopt arbitrary existing data. The practical example therefore uses an already HomeLab-managed installation.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/local-dns/site.yaml).

```yaml
apps:
  filtering:
    profile: pihole
    guest: resolver
    lifecycle: retained
```

### Practical complete example

Use app `filtering` in [examples/catalogue/local-dns/site.yaml](../../../examples/catalogue/local-dns/site.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/local-dns/site.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-interface` |
| `upstream` | No; selected capability can require it | `guest-interface`, `guest-loopback` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `dns_udp` | `pihole` / `host` | `wildcard` via `service` | `53/udp` | None; listener remains in its declared namespace |
| `dns_tcp` | `pihole` / `host` | `wildcard` via `service` | `53/tcp` | None; listener remains in its declared namespace |
| `web` | `pihole` / `host` | `wildcard` via `service` | `80/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `dns_udp` | `udp` | `dns_udp` via `service` |
| `dns_tcp` | `tcp` | `dns_tcp` via `service` |
| `web` | `http` | `web` via `service` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/etc/pihole` | directory / writable | None |
| `database` | Conditional / optional | `/ftl-db` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `upstream` | `dns` | Yes | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit the upstream connection | Refuses the required connection. |
| Use a physical source role for a same-guest loopback upstream | Refuses the connection-scope relationship. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`pihole-images`](../software-and-runtime.md#registration-software-pihole-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`pihole`](../software-and-runtime.md#registration-runtime-profiles-pihole).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `pihole` | `pihole` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `pihole` | 256 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates the explicit upstream and owned managed DNS records while preserving the configuration and unrelated records. Record retirement is limited to names proved by the prior owned payload, not general DNS cleanup. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [pihole.yaml](../../../apps/pihole.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"pihole"` |
| <a id="declaration-display-name"></a>`display_name` | `"Pi-hole"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service"></a>`interfaces.service` | `object` |
| <a id="declaration-interfaces-service-required"></a>`interfaces.service.required` | `true` |
| <a id="declaration-interfaces-service-accepts"></a>`interfaces.service.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-upstream"></a>`interfaces.upstream` | `object` |
| <a id="declaration-interfaces-upstream-required"></a>`interfaces.upstream.required` | `false` |
| <a id="declaration-interfaces-upstream-accepts"></a>`interfaces.upstream.accepts` | `["guest-interface", "guest-loopback"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-dns-udp"></a>`listeners.dns_udp` | `object` |
| <a id="declaration-listeners-dns-udp-service"></a>`listeners.dns_udp.service` | `"pihole"` |
| <a id="declaration-listeners-dns-udp-namespace"></a>`listeners.dns_udp.namespace` | `"host"` |
| <a id="declaration-listeners-dns-udp-interface"></a>`listeners.dns_udp.interface` | `"service"` |
| <a id="declaration-listeners-dns-udp-bind"></a>`listeners.dns_udp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-udp-protocol"></a>`listeners.dns_udp.protocol` | `"udp"` |
| <a id="declaration-listeners-dns-udp-port"></a>`listeners.dns_udp.port` | `53` |
| <a id="declaration-listeners-dns-tcp"></a>`listeners.dns_tcp` | `object` |
| <a id="declaration-listeners-dns-tcp-service"></a>`listeners.dns_tcp.service` | `"pihole"` |
| <a id="declaration-listeners-dns-tcp-namespace"></a>`listeners.dns_tcp.namespace` | `"host"` |
| <a id="declaration-listeners-dns-tcp-interface"></a>`listeners.dns_tcp.interface` | `"service"` |
| <a id="declaration-listeners-dns-tcp-bind"></a>`listeners.dns_tcp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-tcp-protocol"></a>`listeners.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-listeners-dns-tcp-port"></a>`listeners.dns_tcp.port` | `53` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"pihole"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"host"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"service"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `80` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-dns-udp"></a>`endpoints.dns_udp` | `object` |
| <a id="declaration-endpoints-dns-udp-listener"></a>`endpoints.dns_udp.listener` | `"dns_udp"` |
| <a id="declaration-endpoints-dns-udp-protocol"></a>`endpoints.dns_udp.protocol` | `"udp"` |
| <a id="declaration-endpoints-dns-udp-via"></a>`endpoints.dns_udp.via` | `"service"` |
| <a id="declaration-endpoints-dns-tcp"></a>`endpoints.dns_tcp` | `object` |
| <a id="declaration-endpoints-dns-tcp-listener"></a>`endpoints.dns_tcp.listener` | `"dns_tcp"` |
| <a id="declaration-endpoints-dns-tcp-protocol"></a>`endpoints.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-endpoints-dns-tcp-via"></a>`endpoints.dns_tcp.via` | `"service"` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"service"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/etc/pihole"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `true` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-database"></a>`storage.database` | `object` |
| <a id="declaration-storage-database-target"></a>`storage.database.target` | `"/ftl-db"` |
| <a id="declaration-storage-database-read-only"></a>`storage.database.read_only` | `false` |
| <a id="declaration-storage-database-required"></a>`storage.database.required` | `false` |
| <a id="declaration-storage-database-kind"></a>`storage.database.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-upstream"></a>`connections.upstream` | `object` |
| <a id="declaration-connections-upstream-type"></a>`connections.upstream.type` | `"dns"` |
| <a id="declaration-connections-upstream-required"></a>`connections.upstream.required` | `true` |
| <a id="declaration-connections-upstream-readiness"></a>`connections.upstream.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "pihole-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "pihole"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
