[Documentation](../../README.md) / [Reference](../README.md)

# Authentik

Run the identity application, worker and dedicated Redis together. PostgreSQL remains a separately selected application or external endpoint.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: authentik` |
| Adapter | `authentik` |
| Owned containers | `server`, `worker`, `redis` |
| Fresh / update | Existing database, storage and private material must be supplied and owned. Source/render support does not claim provider/application bootstrap or user migration. |
| Multiple instances | Supporting server/worker/Redis belong to one app. Same-guest independent identity installations are not qualified by this page. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [authentik.yaml](../../../apps/authentik.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

secret_key and postgresql_password are required distinct private roles. smtp_password is conditional on SMTP configuration. Redis is supporting infrastructure owned by this app, not a mandatory separately placed app.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |
| `postgresql` | Yes | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `server` / `app-network` | `wildcard` via `private` | `9000/tcp` | `guest-interface` 9000 via `web` |
| `redis` | `redis` / `app-network` | `wildcard` via `private` | `6379/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `media` | Yes | `/media` | directory / writable | None |
| `templates` | Yes | `/templates` | directory / writable | None |
| `certs` | Yes | `/certs` | directory / writable | None |
| `redis` | Yes | `/data` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `postgresql` | Yes | `start` | None |
| `public` | `https` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `secret_key` | Required |
| `postgresql_password` | Required |
| `smtp_password` | Optional until its capability requires it |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| database | Required mapping | name and user: [a-z][a-z0-9_]{0,62}; postgres/template0/template1 are excluded. |
| smtp | Optional mapping | host, port (1..65535), use_tls, use_ssl, from and username; username may be empty. TLS/SSL cannot both be true. Optional timeout:1..300 seconds. |
| callbacks | Optional mapping | evidence references the ongoing identity-callback document; it is not a provider creation request. |

## Software and resource policy

Software selections: `docker`, `curl`, `authentik-images`. Runtime selections: `container-host`, `authentik`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `server` | `authentik` | Immutable registry digest |
| `worker` | `authentik` | Immutable registry digest |
| `redis` | `redis` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `server` | 768 | 1 | 256 |
| `worker` | 768 | 1 | 256 |
| `redis` | 128 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
