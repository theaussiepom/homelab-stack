[Documentation](../../README.md) / [Reference](../README.md)

# Unbound

Provide a recursive resolver with a private container listener and explicit guest-loopback TCP/UDP publications.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: unbound` |
| Adapter | `unbound` |
| Owned containers | `unbound` |
| Multiple instances | Repeated instances are compiler-tested on one guest with different publish_port values and independent service/network identities. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [unbound.yaml](../../../apps/unbound.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

service accepts guest-loopback only. A physical NIC binding is rejected; it does not expose Unbound on the LAN. Fresh config sizing comes from the declared app memory/CPU budget rather than host memory.

## First installation

Can install from empty without a configuration bind. The maintained starter uses `lifecycle: fresh`; keep that value unchanged for later deployments of the same resolver.

Complete creation-policy source: [site.example.yaml](../../../site.example.yaml), app `recursive_dns`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../site.example.yaml).

```yaml
apps:
  recursive_dns:
    profile: unbound
    guest: resolver
    lifecycle: fresh
```

### Practical complete example

Use app `recursive_dns` in [site.example.yaml](../../../site.example.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/site.example.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-loopback` |
| `private` | Yes | `app-network` |

Bind `service` to `{scope: guest-loopback}` and `private` to `{scope: app-network, network: default}`. This profile does not accept a physical NIC for either role. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `dns_udp` | `unbound` / `app-network` | `wildcard` via `private` | `53/udp` | `guest-loopback` 5335 |
| `dns_tcp` | `unbound` / `app-network` | `wildcard` via `private` | `53/tcp` | `guest-loopback` 5335 |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `dns_udp` | `udp` | `dns_udp` via `service` |
| `dns_tcp` | `tcp` | `dns_tcp` via `service` |

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Conditional / optional | `/opt/unbound/etc/unbound` | directory / writable | None |
| `dev` | Conditional / optional | `/opt/unbound/etc/unbound/dev` | directory / writable | None |
| `var` | Conditional / optional | `/opt/unbound/etc/unbound/var` | directory / writable | None |
| `control_key` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_control.key` | file / read-only | None |
| `control_cert` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_control.pem` | file / read-only | None |
| `server_key` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_server.key` | file / read-only | None |
| `server_cert` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_server.pem` | file / read-only | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| publish_port | Optional integer, default 5335 | 1..65535; changes both guest-loopback publications, not container port 53. A duplicate instance can select 5336. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Bind service to a physical NIC | Refuses: this profile publishes only guest-loopback sockets. |
| Give two same-guest instances the same publication port | Refuses the listener/publication conflict; choose distinct explicit ports. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`unbound-images`](../software-and-runtime.md#registration-software-unbound-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`unbound`](../software-and-runtime.md#registration-runtime-profiles-unbound).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `unbound` | `unbound` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `unbound` | 256 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the same resolver and selected loopback publications. With no config bind, startup generates the bounded configuration from the selected app budget; a retained config bind remains separately protected. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [unbound.yaml](../../../apps/unbound.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"unbound"` |
| <a id="declaration-display-name"></a>`display_name` | `"Unbound"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service"></a>`interfaces.service` | `object` |
| <a id="declaration-interfaces-service-required"></a>`interfaces.service.required` | `true` |
| <a id="declaration-interfaces-service-accepts"></a>`interfaces.service.accepts` | `["guest-loopback"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-dns-udp"></a>`listeners.dns_udp` | `object` |
| <a id="declaration-listeners-dns-udp-service"></a>`listeners.dns_udp.service` | `"unbound"` |
| <a id="declaration-listeners-dns-udp-namespace"></a>`listeners.dns_udp.namespace` | `"app-network"` |
| <a id="declaration-listeners-dns-udp-interface"></a>`listeners.dns_udp.interface` | `"private"` |
| <a id="declaration-listeners-dns-udp-bind"></a>`listeners.dns_udp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-udp-protocol"></a>`listeners.dns_udp.protocol` | `"udp"` |
| <a id="declaration-listeners-dns-udp-port"></a>`listeners.dns_udp.port` | `53` |
| <a id="declaration-listeners-dns-udp-publish"></a>`listeners.dns_udp.publish` | `object` |
| <a id="declaration-listeners-dns-udp-publish-scope"></a>`listeners.dns_udp.publish.scope` | `"guest-loopback"` |
| <a id="declaration-listeners-dns-udp-publish-port"></a>`listeners.dns_udp.publish.port` | `5335` |
| <a id="declaration-listeners-dns-tcp"></a>`listeners.dns_tcp` | `object` |
| <a id="declaration-listeners-dns-tcp-service"></a>`listeners.dns_tcp.service` | `"unbound"` |
| <a id="declaration-listeners-dns-tcp-namespace"></a>`listeners.dns_tcp.namespace` | `"app-network"` |
| <a id="declaration-listeners-dns-tcp-interface"></a>`listeners.dns_tcp.interface` | `"private"` |
| <a id="declaration-listeners-dns-tcp-bind"></a>`listeners.dns_tcp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-tcp-protocol"></a>`listeners.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-listeners-dns-tcp-port"></a>`listeners.dns_tcp.port` | `53` |
| <a id="declaration-listeners-dns-tcp-publish"></a>`listeners.dns_tcp.publish` | `object` |
| <a id="declaration-listeners-dns-tcp-publish-scope"></a>`listeners.dns_tcp.publish.scope` | `"guest-loopback"` |
| <a id="declaration-listeners-dns-tcp-publish-port"></a>`listeners.dns_tcp.publish.port` | `5335` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-dns-udp"></a>`endpoints.dns_udp` | `object` |
| <a id="declaration-endpoints-dns-udp-listener"></a>`endpoints.dns_udp.listener` | `"dns_udp"` |
| <a id="declaration-endpoints-dns-udp-protocol"></a>`endpoints.dns_udp.protocol` | `"udp"` |
| <a id="declaration-endpoints-dns-udp-via"></a>`endpoints.dns_udp.via` | `"service"` |
| <a id="declaration-endpoints-dns-tcp"></a>`endpoints.dns_tcp` | `object` |
| <a id="declaration-endpoints-dns-tcp-listener"></a>`endpoints.dns_tcp.listener` | `"dns_tcp"` |
| <a id="declaration-endpoints-dns-tcp-protocol"></a>`endpoints.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-endpoints-dns-tcp-via"></a>`endpoints.dns_tcp.via` | `"service"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/opt/unbound/etc/unbound"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `false` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-dev"></a>`storage.dev` | `object` |
| <a id="declaration-storage-dev-target"></a>`storage.dev.target` | `"/opt/unbound/etc/unbound/dev"` |
| <a id="declaration-storage-dev-read-only"></a>`storage.dev.read_only` | `false` |
| <a id="declaration-storage-dev-required"></a>`storage.dev.required` | `false` |
| <a id="declaration-storage-dev-kind"></a>`storage.dev.kind` | `"directory"` |
| <a id="declaration-storage-var"></a>`storage.var` | `object` |
| <a id="declaration-storage-var-target"></a>`storage.var.target` | `"/opt/unbound/etc/unbound/var"` |
| <a id="declaration-storage-var-read-only"></a>`storage.var.read_only` | `false` |
| <a id="declaration-storage-var-required"></a>`storage.var.required` | `false` |
| <a id="declaration-storage-var-kind"></a>`storage.var.kind` | `"directory"` |
| <a id="declaration-storage-control-key"></a>`storage.control_key` | `object` |
| <a id="declaration-storage-control-key-target"></a>`storage.control_key.target` | `"/opt/unbound/etc/unbound/unbound_control.key"` |
| <a id="declaration-storage-control-key-read-only"></a>`storage.control_key.read_only` | `true` |
| <a id="declaration-storage-control-key-required"></a>`storage.control_key.required` | `false` |
| <a id="declaration-storage-control-key-kind"></a>`storage.control_key.kind` | `"file"` |
| <a id="declaration-storage-control-cert"></a>`storage.control_cert` | `object` |
| <a id="declaration-storage-control-cert-target"></a>`storage.control_cert.target` | `"/opt/unbound/etc/unbound/unbound_control.pem"` |
| <a id="declaration-storage-control-cert-read-only"></a>`storage.control_cert.read_only` | `true` |
| <a id="declaration-storage-control-cert-required"></a>`storage.control_cert.required` | `false` |
| <a id="declaration-storage-control-cert-kind"></a>`storage.control_cert.kind` | `"file"` |
| <a id="declaration-storage-server-key"></a>`storage.server_key` | `object` |
| <a id="declaration-storage-server-key-target"></a>`storage.server_key.target` | `"/opt/unbound/etc/unbound/unbound_server.key"` |
| <a id="declaration-storage-server-key-read-only"></a>`storage.server_key.read_only` | `true` |
| <a id="declaration-storage-server-key-required"></a>`storage.server_key.required` | `false` |
| <a id="declaration-storage-server-key-kind"></a>`storage.server_key.kind` | `"file"` |
| <a id="declaration-storage-server-cert"></a>`storage.server_cert` | `object` |
| <a id="declaration-storage-server-cert-target"></a>`storage.server_cert.target` | `"/opt/unbound/etc/unbound/unbound_server.pem"` |
| <a id="declaration-storage-server-cert-read-only"></a>`storage.server_cert.read_only` | `true` |
| <a id="declaration-storage-server-cert-required"></a>`storage.server_cert.required` | `false` |
| <a id="declaration-storage-server-cert-kind"></a>`storage.server_cert.kind` | `"file"` |
| <a id="declaration-connections"></a>`connections` | `{}` |
| <a id="declaration-properties"></a>`properties` | `object` |
| <a id="declaration-properties-publish-port"></a>`properties.publish_port` | `5335` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "unbound-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "unbound"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
