[Documentation](../../README.md) / [Reference](../README.md)

# Pi-hole

Provide DNS filtering and a web UI. Select an upstream resolver explicitly; Unbound is one possible independent upstream.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: pihole` |
| Adapter | `pihole` |
| Owned containers | `pihole` |
| Fresh / update | Fresh and owned-repeat controller/helper paths are tested. Supply the supported config directory; declaring a path is not a data restoration operation. The optional database role preserves an existing FTL database location. |
| Multiple instances | One Pi-hole per guest: the managed-record sidecar is a fixed owned leaf, and DNS/web host sockets must not collide. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [pihole.yaml](../../../apps/pihole.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The optional upstream interface role becomes necessary when binding the required upstream connection. A same-guest Unbound target uses guest-loopback; a remote target uses a physical role. Context DNS is a value and does not create that connection or a wait.

## Interfaces

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

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Software and resource policy

Software selections: `docker`, `curl`, `pihole-images`. Runtime selections: `container-host`, `pihole`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `pihole` | `pihole` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `pihole` | 256 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
