[Documentation](../../README.md) / [Reference](../README.md)

# CloudBeaver

Provide the CloudBeaver database UI behind a gateway that signs users in through OpenID Connect (OIDC). Users can enter their own database credentials; managed administration is a separate explicit capability.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: cloudbeaver` |
| Adapter | `cloudbeaver` |
| Owned containers | `cloudbeaver`, `auth_gateway` |
| Multiple instances | Namespace-aware helper tests cover independent instances. Each instance needs its own project, services, private network, published address and port, storage, runtime directory and protected credential directory. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [cloudbeaver.yaml](../../../apps/cloudbeaver.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The profile marks `public` optional, but generating a usable deployment packet currently requires an explicit HTTPS connection and the app’s canonical origin (its public base URL). The sign-in health check uses both, so supply them even though the profile metadata marks the field optional.

Only the OpenID Connect (OIDC) sign-in gateway is published; the Community service remains private. Authentication is required through the named cloudbeaver-oidc policy, including its client-secret source and canonical HTTPS app origin. The current account-binding code requires at least one managed datasource, a saved connection using an account that HomeLab manages. You can add unmanaged connection metadata alongside it, but a configuration containing only unmanaged connections is rejected. Managed PostgreSQL administration is SUPERUSER; managed MariaDB administration is global ALL with GRANT. These dedicated accounts are created once and reused. You must explicitly select their privileges; a connection reference does not grant them. Saved managed datasource passwords are plaintext at rest in the private workspace.

## First installation

This profile can create an empty HomeLab-managed workspace beneath a declared provider volume. A configured OIDC provider and client and at least one explicitly managed database-administration connection are prerequisites; this does not create the identity provider or import a foreign workspace.

For a complete example using the creation policy, see [examples/catalogue/new-database-guis.yaml](../../../examples/catalogue/new-database-guis.yaml), app `cloud`. The example must resolve and generate deployment files successfully. These checks do not prove that the service has been deployed.

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

Use app `cloud` in [examples/catalogue/database-guis.yaml](../../../examples/catalogue/database-guis.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/database-guis.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |
| `postgresql` | No; selected capability can require it | `guest-interface` |
| `mariadb` | No; selected capability can require it | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `auth_gateway` / `app-network` | `wildcard` via `private` | `4180/tcp` | `guest-interface` 80 via `web` |
| `community` | `cloudbeaver` / `app-network` | `wildcard` via `private` | `8978/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard listener accepts connections within the declared app network. A port becomes available on the guest only when explicitly published. Endpoints do not permit network traffic or make another app wait for this service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `workspace` | Yes | `/opt/cloudbeaver/workspace` | directory / writable | Create-only 8978:8978 mode 0700 |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `postgresql` | `postgresql` | No | `start` | None |
| `mariadb` | `mariadb` | No | `start` | None |
| `postgresql-admin` | `postgresql` | No | None | `postgresql-admin` |
| `mariadb-admin` | `mariadb` | No | None | `mariadb-admin` |
| `public` | `https` | No | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Authentication requirement: `cloudbeaver-oidc` (required), selected by a named site authentication policy.

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret. Saved GUI credentials, where used, are plaintext at rest in their protected workspace.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| server_name | Required string | Nonempty single line, at most 100 characters. |
| recovery_admin | Required string | Existing recovery identity matching `[a-z][a-z0-9_-]{2,63}`; this does not bootstrap or reset it. |
| heap_mib | Required integer | 256..16384; must also fit the selected application resource budget. |
| auth_headers | Required mapping | Supply exactly user and team as distinct safe X-* header names. Headers that forward the address, protocol or host are forbidden. |
| connections | Required mapping | 1..24 metadata records keyed by a selected connection role; each has name (nonempty <=100) and database (<=128, may be empty). `sslmode` is required only for unmanaged PostgreSQL and must be `disable`, `prefer` or `require`; it is forbidden for managed PostgreSQL and all MariaDB connections. Managed transport is enforced by the selected account contract. |
| mariadb_jdbc | Variant-owned conditional capability | The MariaDB-admin variant pins version, SHA-256 and compatibility filename. Do not introduce a site-owned driver version. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Keep only unmanaged metadata connections | Account binding fails because at least one HomeLab-managed database connection is required. |
| Omit public connection or origin, or give sslmode to a managed connection | Generating the health check fails without the HTTPS connection and canonical origin. Property validation rejects sslmode on a managed connection because its account contract determines transport. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

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

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Gateway and saved-connection behavior

The OIDC gateway checks the issuer, audience, signature using the JSON Web Key Set (JWKS), nonce, Proof Key for Code Exchange (PKCE) and verified email, then supplies only the selected identity headers. Explicit provider endpoints avoid startup discovery. The Community service remains private; the resource manager stays enabled. Your site must already have registered the provider and client and configured its authorization policy.

Managed connections save their settings in a private native datasource file in the HomeLab-managed workspace. Passwords are stored as plaintext and are shared by the selected authorized users. They do not enter Git, the application environment or normal logs. This mode does not run recovery or initial setup, or replace unrelated user connections. PostgreSQL SUPERUSER can access server files and run programs on the server; select that privilege deliberately rather than treating it as ordinary connection metadata.

## Later deployments

HomeLab maintains its existing workspace, gateway and dedicated selected SQL account records. Existing user connections and workspace identity remain protected; changing public connection metadata does not rotate their saved material.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#cloudbeaver) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [cloudbeaver.yaml](../../../apps/cloudbeaver.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

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
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-workspace"></a>`backup.include.workspace` | `object` |
| <a id="declaration-backup-include-workspace-category"></a>`backup.include.workspace.category` | `"state"` |
| <a id="declaration-backup-include-workspace-capture"></a>`backup.include.workspace.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
