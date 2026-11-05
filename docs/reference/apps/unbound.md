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
| Fresh / update | Fresh mode requires no storage bindings and uses the packaged config with declared resource sizing. Retained mode requires the existing config binding; optional nested state/control files preserve their exact types. |
| Multiple instances | Repeated instances are compiler-tested on one guest with different publish_port values and independent service/network identities. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [unbound.yaml](../../../apps/unbound.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

service accepts guest-loopback only. A physical NIC binding is rejected; it does not expose Unbound on the LAN. Fresh config sizing comes from the declared app memory/CPU budget rather than host memory.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-loopback` |
| `private` | Yes | `app-network` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `dns_udp` | `unbound` / `app-network` | `wildcard` via `private` | `53/udp` | `guest-loopback` 5335 |
| `dns_tcp` | `unbound` / `app-network` | `wildcard` via `private` | `53/tcp` | `guest-loopback` 5335 |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `dns_udp` | `udp` | `dns_udp` via `service` |
| `dns_tcp` | `tcp` | `dns_tcp` via `service` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

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

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| publish_port | Optional integer, default 5335 | 1..65535; changes both guest-loopback publications, not container port 53. A duplicate instance can select 5336. |

## Software and resource policy

Software selections: `docker`, `curl`, `unbound-images`. Runtime selections: `container-host`, `unbound`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `unbound` | `unbound` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `unbound` | 256 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
