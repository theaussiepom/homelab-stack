[Documentation](../../README.md) / [Reference](../README.md)

# InfluxDB

Configure the supported native InfluxDB package service and its declared existing data path.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: influxdb` |
| Adapter | `influxdb` |
| Owned containers | None; native package service |
| Fresh / update | The supported package/configuration and ordinary retained path are documented; new database initialization/tenant bootstrap is not qualified here. |
| Multiple instances | One native InfluxDB unit per guest. PostgreSQL + InfluxDB numeric-group namespace conflicts refuse. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [influxdb.yaml](../../../apps/influxdb.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The typed data role drives the existing native configuration. Organization, token and bucket setup are not inferred from a listener or profile name.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `influxdb` / `host` | `interface` via `service` | `8086/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `service` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/influxdb` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Software and resource policy

Software selections: `influxdb`. Runtime selections: `native-influxdb`.

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 1792 | Guest allocation | Native service |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
