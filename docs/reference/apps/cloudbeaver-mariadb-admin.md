[Documentation](../../README.md) / [Reference](../README.md)

# CloudBeaver — `cloudbeaver-mariadb-admin`

Select CloudBeaver with the additional library-owned MariaDB Connector/J capability required by an explicitly managed MariaDB administration connection.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: cloudbeaver-mariadb-admin` |
| Adapter | `cloudbeaver` |
| Owned containers | `cloudbeaver`, `auth_gateway` |
| Fresh / update | Same workspace lifecycle as the generic profile. Managed administration requires an already initialized, running, TLS-enabled database; it does not initialize that database. |
| Multiple instances | Same namespace rules as CloudBeaver; never share a workspace or account identity between instances. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [cloudbeaver-mariadb-admin.yaml](../../../apps/cloudbeaver-mariadb-admin.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

This variant makes mariadb-admin mandatory and selects the library-owned Connector/J 3.5.11 replacement. Its compatibility filename targets the pinned image's existing single jar slot; replacement bytes are verified separately. PostgreSQL uses required TLS/SCRAM/channel binding; MariaDB uses PARSEC with verify-full. No manual CA lifecycle is introduced.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |
| `postgresql` | No; selected capability can require it | `guest-interface` |
| `mariadb` | No; selected capability can require it | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `auth_gateway` / `app-network` | `wildcard` via `private` | `4180/tcp` | `guest-interface` 80 via `web` |
| `community` | `cloudbeaver` / `app-network` | `wildcard` via `private` | `8978/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `workspace` | Yes | `/opt/cloudbeaver/workspace` | directory / writable | Create-only 8978:8978 mode 0700 |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `postgresql` | `postgresql` | No | `start` | None |
| `mariadb` | `mariadb` | No | `start` | None |
| `postgresql-admin` | `postgresql` | No | None | `postgresql-admin` |
| `mariadb-admin` | `mariadb` | Yes | None | `mariadb-admin` |
| `public` | `https` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Authentication requirement: `cloudbeaver-oidc` (required), selected by a named site authentication policy.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update. Saved GUI credentials, where used, are plaintext at rest in their protected workspace.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| server_name | Required string | Nonempty single line, at most 100 characters. |
| recovery_admin | Required string | Existing recovery identity matching [a-z][a-z0-9_-]{2,63}; this does not bootstrap or reset it. |
| heap_mib | Required integer | 256..16384; must also fit the selected application resource budget. |
| auth_headers | Required mapping | Exactly user and team, distinct safe X-* header names; forwarded-address/protocol/host headers are forbidden. |
| connections | Required mapping | 1..24 metadata records keyed by a selected connection role; each has name (nonempty <=100) and database (<=128, may be empty). `sslmode` is required only for unmanaged PostgreSQL and must be `disable`, `prefer` or `require`; it is forbidden for managed PostgreSQL and all MariaDB connections. Managed transport is enforced by the selected account contract. |
| mariadb_jdbc | Variant-owned conditional capability | The MariaDB-admin variant pins version, SHA-256 and compatibility filename. Do not introduce a site-owned driver version. |

This variant already supplies `mariadb_jdbc`; its exact values belong to the [profile source](../../../apps/cloudbeaver-mariadb-admin.yaml), not another site version declaration.

## Software and resource policy

Software selections: `docker`, `curl`, `cloudbeaver-images`. Runtime selections: `container-host`, `cloudbeaver`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `cloudbeaver` | `cloudbeaver` | Immutable registry digest |
| `auth_gateway` | `auth_gateway` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `cloudbeaver` | 1536 | 1 | 512 |
| `auth_gateway` | 128 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Gateway and saved-connection behavior

The OIDC gateway validates issuer, audience, signature/JWKS, nonce, PKCE and verified email, then supplies only the selected identity headers. Explicit provider endpoints avoid startup discovery. The Community service remains private; the resource manager stays enabled. Provider/client registration and authorization policy already exist on the consuming site.

Managed connections write a private native datasource file in the owned workspace. Passwords are plaintext at rest and shared by the authorized selected users. They do not enter Git, the application environment or normal logs. The mode does not invoke recovery/bootstrap or replace unrelated user connections. PostgreSQL SUPERUSER includes server-file/program powers; treat that deliberate privilege separately from metadata-only connection entries.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
