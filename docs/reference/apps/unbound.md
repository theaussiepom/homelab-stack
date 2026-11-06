[Documentation](../../README.md) / [Reference](../README.md)

# Unbound

Provide a recursive resolver with a private container listener and explicit guest-loopback TCP/UDP publications.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

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

Software selections: `docker`, `curl`, `unbound-images`. Runtime selections: `container-host`, `unbound`.

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

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#unbound) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
