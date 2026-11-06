[Documentation](../../README.md) / [Reference](../README.md)

# CloudBeaver

Provide the CloudBeaver database UI behind its owned OIDC gateway. Users can enter their own database credentials; managed administration is a separate explicit capability.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: cloudbeaver` |
| Adapter | `cloudbeaver` |
| Owned containers | `cloudbeaver`, `auth_gateway` |
| Multiple instances | Namespace-aware helper tests cover independent instances. Distinct project, services, private network, published address/port, storage, runtime and custody directories are required. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [cloudbeaver.yaml](../../../apps/cloudbeaver.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The profile marks `public` optional, but a usable current packet requires its explicit HTTPS connection and canonical origin: the owned sign-in health check uses both. Profile structural optionality does not waive that packet/health requirement.

Only the OIDC gateway is published; the Community service remains private. Authentication is required through the named cloudbeaver-oidc policy, including its client-secret source and canonical HTTPS app origin. At least one managed datasource is required by the current canonical-account binder. Unmanaged metadata may be added alongside it; an unmanaged-only selection currently refuses. Managed PostgreSQL administration is SUPERUSER; managed MariaDB administration is global ALL with GRANT. Dedicated create-once accounts are deliberate privileges, never inferred. Saved managed datasource passwords are plaintext at rest in the private workspace.

## First installation

Can create an empty owned workspace beneath a declared provider volume. A configured OIDC provider/client and at least one explicitly managed database-administration connection are prerequisites; this does not create the identity provider or import a foreign workspace.

Complete creation-policy source: [examples/catalogue/new-database-guis.yaml](../../../examples/catalogue/new-database-guis.yaml), app `cloud`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/database-guis.yaml).

```yaml
apps:
  cloud:
    profile: cloudbeaver
    guest: cloud
    lifecycle: retained
```

### Practical complete example

Use app `cloud` in [examples/catalogue/database-guis.yaml](../../../examples/catalogue/database-guis.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/database-guis.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

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

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

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
| `mariadb-admin` | `mariadb` | No | None | `mariadb-admin` |
| `public` | `https` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Authentication requirement: `cloudbeaver-oidc` (required), selected by a named site authentication policy.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update. Saved GUI credentials, where used, are plaintext at rest in their protected workspace.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| server_name | Required string | Nonempty single line, at most 100 characters. |
| recovery_admin | Required string | Existing recovery identity matching `[a-z][a-z0-9_-]{2,63}`; this does not bootstrap or reset it. |
| heap_mib | Required integer | 256..16384; must also fit the selected application resource budget. |
| auth_headers | Required mapping | Exactly user and team, distinct safe X-* header names; forwarded-address/protocol/host headers are forbidden. |
| connections | Required mapping | 1..24 metadata records keyed by a selected connection role; each has name (nonempty <=100) and database (<=128, may be empty). `sslmode` is required only for unmanaged PostgreSQL and must be `disable`, `prefer` or `require`; it is forbidden for managed PostgreSQL and all MariaDB connections. Managed transport is enforced by the selected account contract. |
| mariadb_jdbc | Variant-owned conditional capability | The MariaDB-admin variant pins version, SHA-256 and compatibility filename. Do not introduce a site-owned driver version. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Keep only unmanaged metadata connections | Current canonical-account binder refuses the empty managed set; at least one managed connection is required. |
| Omit public connection or origin, or give sslmode to a managed connection | Packet/health or property validation refuses. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`cloudbeaver-images`](../software-and-runtime.md#registration-software-cloudbeaver-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`cloudbeaver`](../software-and-runtime.md#registration-runtime-profiles-cloudbeaver).

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

Maintains the owned workspace, gateway and dedicated selected SQL account records. Existing user connections and workspace identity remain protected; changing public connection metadata does not rotate their saved material. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [cloudbeaver.yaml](../../../apps/cloudbeaver.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"cloudbeaver"` |
| <a id="declaration-display-name"></a>`display_name` | `"CloudBeaver"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-interfaces-postgresql"></a>`interfaces.postgresql` | `object` |
| <a id="declaration-interfaces-postgresql-required"></a>`interfaces.postgresql.required` | `false` |
| <a id="declaration-interfaces-postgresql-accepts"></a>`interfaces.postgresql.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-mariadb"></a>`interfaces.mariadb` | `object` |
| <a id="declaration-interfaces-mariadb-required"></a>`interfaces.mariadb.required` | `false` |
| <a id="declaration-interfaces-mariadb-accepts"></a>`interfaces.mariadb.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management"></a>`interfaces.management` | `object` |
| <a id="declaration-interfaces-management-required"></a>`interfaces.management.required` | `false` |
| <a id="declaration-interfaces-management-accepts"></a>`interfaces.management.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"auth_gateway"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"private"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `4180` |
| <a id="declaration-listeners-web-publish"></a>`listeners.web.publish` | `object` |
| <a id="declaration-listeners-web-publish-scope"></a>`listeners.web.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-publish-interface"></a>`listeners.web.publish.interface` | `"web"` |
| <a id="declaration-listeners-web-publish-port"></a>`listeners.web.publish.port` | `80` |
| <a id="declaration-listeners-community"></a>`listeners.community` | `object` |
| <a id="declaration-listeners-community-service"></a>`listeners.community.service` | `"cloudbeaver"` |
| <a id="declaration-listeners-community-namespace"></a>`listeners.community.namespace` | `"app-network"` |
| <a id="declaration-listeners-community-interface"></a>`listeners.community.interface` | `"private"` |
| <a id="declaration-listeners-community-bind"></a>`listeners.community.bind` | `"wildcard"` |
| <a id="declaration-listeners-community-protocol"></a>`listeners.community.protocol` | `"tcp"` |
| <a id="declaration-listeners-community-port"></a>`listeners.community.port` | `8978` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-workspace"></a>`storage.workspace` | `object` |
| <a id="declaration-storage-workspace-target"></a>`storage.workspace.target` | `"/opt/cloudbeaver/workspace"` |
| <a id="declaration-storage-workspace-read-only"></a>`storage.workspace.read_only` | `false` |
| <a id="declaration-storage-workspace-required"></a>`storage.workspace.required` | `true` |
| <a id="declaration-storage-workspace-kind"></a>`storage.workspace.kind` | `"directory"` |
| <a id="declaration-storage-workspace-initialize"></a>`storage.workspace.initialize` | `object` |
| <a id="declaration-storage-workspace-initialize-type"></a>`storage.workspace.initialize.type` | `"directory"` |
| <a id="declaration-storage-workspace-initialize-uid"></a>`storage.workspace.initialize.uid` | `8978` |
| <a id="declaration-storage-workspace-initialize-gid"></a>`storage.workspace.initialize.gid` | `8978` |
| <a id="declaration-storage-workspace-initialize-mode"></a>`storage.workspace.initialize.mode` | `"0700"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-postgresql"></a>`connections.postgresql` | `object` |
| <a id="declaration-connections-postgresql-type"></a>`connections.postgresql.type` | `"postgresql"` |
| <a id="declaration-connections-postgresql-required"></a>`connections.postgresql.required` | `false` |
| <a id="declaration-connections-postgresql-readiness"></a>`connections.postgresql.readiness` | `["start"]` |
| <a id="declaration-connections-mariadb"></a>`connections.mariadb` | `object` |
| <a id="declaration-connections-mariadb-type"></a>`connections.mariadb.type` | `"mariadb"` |
| <a id="declaration-connections-mariadb-required"></a>`connections.mariadb.required` | `false` |
| <a id="declaration-connections-mariadb-readiness"></a>`connections.mariadb.readiness` | `["start"]` |
| <a id="declaration-connections-postgresql-admin"></a>`connections.postgresql-admin` | `object` |
| <a id="declaration-connections-postgresql-admin-type"></a>`connections.postgresql-admin.type` | `"postgresql"` |
| <a id="declaration-connections-postgresql-admin-required"></a>`connections.postgresql-admin.required` | `false` |
| <a id="declaration-connections-postgresql-admin-accounts"></a>`connections.postgresql-admin.accounts` | `["postgresql-admin"]` |
| <a id="declaration-connections-mariadb-admin"></a>`connections.mariadb-admin` | `object` |
| <a id="declaration-connections-mariadb-admin-type"></a>`connections.mariadb-admin.type` | `"mariadb"` |
| <a id="declaration-connections-mariadb-admin-required"></a>`connections.mariadb-admin.required` | `false` |
| <a id="declaration-connections-mariadb-admin-accounts"></a>`connections.mariadb-admin.accounts` | `["mariadb-admin"]` |
| <a id="declaration-connections-public"></a>`connections.public` | `object` |
| <a id="declaration-connections-public-type"></a>`connections.public.type` | `"https"` |
| <a id="declaration-connections-public-required"></a>`connections.public.required` | `false` |
| <a id="declaration-connections-public-readiness"></a>`connections.public.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "cloudbeaver-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "cloudbeaver"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-authentication"></a>`authentication` | `"cloudbeaver-oidc"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
