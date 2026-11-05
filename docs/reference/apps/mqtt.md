[Documentation](../../README.md) / [Reference](../README.md)

# MQTT

Run the Mosquitto broker using the explicitly bound existing configuration, persistence and log directories.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: mqtt` |
| Adapter | `mqtt` |
| Owned containers | `mqtt` |
| Fresh / update | Bind a valid existing Mosquitto configuration. The adapter does not invent broker config, ACLs or accounts. Explicit managed account creation is a separate selected capability. |
| Multiple instances | Fixed host MQTT 1883 conflicts with another identical broker on the same guest. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [mqtt.yaml](../../../apps/mqtt.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The profile marks `probe` as optional metadata, but the current MQTT adapter requires it to select an existing controller MQTT probe record through a file secret source. A source without that binding refuses with `component.secret-required`. The record is distinct from GUI, application and identity credentials. Ordinary account changes use the guarded parent-mounted password-file/HUP path and do not recreate peer clients.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `backend` | Yes | `guest-interface` |
| `frontend` | Yes | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `mqtt` | `mqtt` / `host` | `wildcard` via `backend` | `1883/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `backend` | `tcp` | `mqtt` via `backend` |
| `frontend` | `tcp` | `mqtt` via `frontend` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/mosquitto/config` | directory / writable | None |
| `data` | Yes | `/mosquitto/data` | directory / writable | None |
| `log` | Yes | `/mosquitto/log` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `probe` | Required by the current adapter; bind a file secret source |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| password_file | Conditional string | Only /mosquitto/config/<safe-basename>; needed for an explicitly managed MQTT account. Does not create config/ACL implicitly. |

## Software and resource policy

Software selections: `docker`, `curl`, `mqtt-images`. Runtime selections: `container-host`, `mqtt`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `mqtt` | `mqtt` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `mqtt` | 256 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
