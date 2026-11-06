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
| Multiple instances | Same namespace rules as CloudBeaver; never share a workspace or account identity between instances. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [cloudbeaver-mariadb-admin.yaml](../../../apps/cloudbeaver-mariadb-admin.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The profile marks `public` optional, but a usable current packet requires its explicit HTTPS connection and canonical origin: the owned sign-in health check uses both. Profile structural optionality does not waive that packet/health requirement.

This variant makes mariadb-admin mandatory and selects the library-owned Connector/J 3.5.11 replacement. Its compatibility filename targets the pinned image's existing single jar slot; replacement bytes are verified separately. PostgreSQL uses required TLS/SCRAM/channel binding; MariaDB uses PARSEC with verify-full. No manual CA lifecycle is introduced.

## First installation

Can create an empty owned workspace beneath a declared provider volume. A configured OIDC provider/client and the selected owned MariaDB target/account capability are prerequisites. The variant supplies the declared JDBC artifact, not a new version choice.

Complete creation-policy source: [examples/catalogue/new-database-guis.yaml](../../../examples/catalogue/new-database-guis.yaml), app `administration`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/database-guis.yaml).

```yaml
apps:
  administration:
    profile: cloudbeaver-mariadb-admin
    guest: administration
    lifecycle: retained
```

### Practical complete example

Use app `administration` in [examples/catalogue/database-guis.yaml](../../../examples/catalogue/database-guis.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/database-guis.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

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

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

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

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit the managed MariaDB selection | Refuses the variant-owned driver capability contract. |
| Override the JDBC artifact in site properties or add MariaDB sslmode | Refuses software authority or the connection property contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

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

## Later deployments

Maintains the owned workspace/gateway and its explicit MariaDB administration capability. The authoritative JDBC selection remains in the library; changing instance labels cannot create a second workspace or credential owner. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).
