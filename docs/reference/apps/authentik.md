[Documentation](../../README.md) / [Reference](../README.md)

# Authentik

Run the identity application, worker and dedicated Redis together. PostgreSQL remains a separately selected application or external endpoint.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: authentik` |
| Adapter | `authentik` |
| Owned containers | `server`, `worker`, `redis` |
| Multiple instances | Supporting server/worker/Redis belong to one app. Same-guest independent identity installations are not qualified by this page. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [authentik.yaml](../../../apps/authentik.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Supply separate private inputs for `secret_key` and `postgresql_password`. Supply `smtp_password` when the SMTP configuration requires it. This app manages its own supporting Redis container; you do not need to place a separate Redis app.

## First installation

Container configuration is available with a prepared PostgreSQL database/user and supplied application keys. Administrator onboarding, users, providers and client registrations are not created by this profile. The complete example maintains an already configured installation; source compilation is not target onboarding verification.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/identity-monitoring.yaml).

```yaml
apps:
  identity:
    profile: authentik
    guest: identity
    lifecycle: retained
```

### Practical complete example

Use app `identity` in [examples/catalogue/identity-monitoring.yaml](../../../examples/catalogue/identity-monitoring.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/identity-monitoring.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |
| `postgresql` | Yes | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `server` / `app-network` | `wildcard` via `private` | `9000/tcp` | `guest-interface` 9000 via `web` |
| `redis` | `redis` / `app-network` | `wildcard` via `private` | `6379/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard listener accepts connections within the declared app network. A port becomes available on the guest only when explicitly published. Endpoints do not permit network traffic or make another app wait for this service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/b83260bb5dcd427a14e79254fdb144b1b9097b8c/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `media` | Yes | `/media` | directory / writable | None |
| `templates` | Yes | `/templates` | directory / writable | None |
| `certs` | Yes | `/certs` | directory / writable | None |
| `redis` | Yes | `/data` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `postgresql` | Yes | `start` | None |
| `public` | `https` | No | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `secret_key` | Required |
| `postgresql_password` | Required |
| `smtp_password` | Optional until its capability requires it |

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/b83260bb5dcd427a14e79254fdb144b1b9097b8c/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| database | Required mapping | name and user: `[a-z][a-z0-9_]{0,62}`; postgres/template0/template1 are excluded. |
| smtp | Optional mapping | host, port (1..65535), use_tls, use_ssl, from and username; username may be empty. TLS/SSL cannot both be true. Optional timeout:1..300 seconds. |
| callbacks | Optional mapping | evidence references the ongoing identity-callback document; it is not a provider creation request. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit secret_key or postgresql_password | Refuses the required selected roles. |
| Bind database to a non-PostgreSQL/incorrect-port endpoint | Refuses the database binding. |

The framework validates these requirements. [Tests](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`authentik-images`](../software-and-runtime.md#registration-software-authentik-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`authentik`](../software-and-runtime.md#registration-runtime-profiles-authentik).

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

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab updates the server, worker and dedicated Redis configuration that it manages while preserving the PostgreSQL data and selected application keys. The profile does not recreate existing users, providers or client registrations.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/b83260bb5dcd427a14e79254fdb144b1b9097b8c/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/b83260bb5dcd427a14e79254fdb144b1b9097b8c/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/b83260bb5dcd427a14e79254fdb144b1b9097b8c/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/b83260bb5dcd427a14e79254fdb144b1b9097b8c/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/b83260bb5dcd427a14e79254fdb144b1b9097b8c/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#authentik) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [authentik.yaml](../../../apps/authentik.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"authentik"` |
| <a id="declaration-display-name"></a>`display_name` | `"Authentik"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-interfaces-postgresql"></a>`interfaces.postgresql` | `object` |
| <a id="declaration-interfaces-postgresql-required"></a>`interfaces.postgresql.required` | `true` |
| <a id="declaration-interfaces-postgresql-accepts"></a>`interfaces.postgresql.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management"></a>`interfaces.management` | `object` |
| <a id="declaration-interfaces-management-required"></a>`interfaces.management.required` | `false` |
| <a id="declaration-interfaces-management-accepts"></a>`interfaces.management.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"server"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"private"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `9000` |
| <a id="declaration-listeners-web-publish"></a>`listeners.web.publish` | `object` |
| <a id="declaration-listeners-web-publish-scope"></a>`listeners.web.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-publish-interface"></a>`listeners.web.publish.interface` | `"web"` |
| <a id="declaration-listeners-web-publish-port"></a>`listeners.web.publish.port` | `9000` |
| <a id="declaration-listeners-redis"></a>`listeners.redis` | `object` |
| <a id="declaration-listeners-redis-service"></a>`listeners.redis.service` | `"redis"` |
| <a id="declaration-listeners-redis-namespace"></a>`listeners.redis.namespace` | `"app-network"` |
| <a id="declaration-listeners-redis-interface"></a>`listeners.redis.interface` | `"private"` |
| <a id="declaration-listeners-redis-bind"></a>`listeners.redis.bind` | `"wildcard"` |
| <a id="declaration-listeners-redis-protocol"></a>`listeners.redis.protocol` | `"tcp"` |
| <a id="declaration-listeners-redis-port"></a>`listeners.redis.port` | `6379` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-media"></a>`storage.media` | `object` |
| <a id="declaration-storage-media-target"></a>`storage.media.target` | `"/media"` |
| <a id="declaration-storage-media-read-only"></a>`storage.media.read_only` | `false` |
| <a id="declaration-storage-media-required"></a>`storage.media.required` | `true` |
| <a id="declaration-storage-media-kind"></a>`storage.media.kind` | `"directory"` |
| <a id="declaration-storage-templates"></a>`storage.templates` | `object` |
| <a id="declaration-storage-templates-target"></a>`storage.templates.target` | `"/templates"` |
| <a id="declaration-storage-templates-read-only"></a>`storage.templates.read_only` | `false` |
| <a id="declaration-storage-templates-required"></a>`storage.templates.required` | `true` |
| <a id="declaration-storage-templates-kind"></a>`storage.templates.kind` | `"directory"` |
| <a id="declaration-storage-certs"></a>`storage.certs` | `object` |
| <a id="declaration-storage-certs-target"></a>`storage.certs.target` | `"/certs"` |
| <a id="declaration-storage-certs-read-only"></a>`storage.certs.read_only` | `false` |
| <a id="declaration-storage-certs-required"></a>`storage.certs.required` | `true` |
| <a id="declaration-storage-certs-kind"></a>`storage.certs.kind` | `"directory"` |
| <a id="declaration-storage-redis"></a>`storage.redis` | `object` |
| <a id="declaration-storage-redis-target"></a>`storage.redis.target` | `"/data"` |
| <a id="declaration-storage-redis-read-only"></a>`storage.redis.read_only` | `false` |
| <a id="declaration-storage-redis-required"></a>`storage.redis.required` | `true` |
| <a id="declaration-storage-redis-kind"></a>`storage.redis.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-database"></a>`connections.database` | `object` |
| <a id="declaration-connections-database-type"></a>`connections.database.type` | `"postgresql"` |
| <a id="declaration-connections-database-required"></a>`connections.database.required` | `true` |
| <a id="declaration-connections-database-readiness"></a>`connections.database.readiness` | `["start"]` |
| <a id="declaration-connections-public"></a>`connections.public` | `object` |
| <a id="declaration-connections-public-type"></a>`connections.public.type` | `"https"` |
| <a id="declaration-connections-public-required"></a>`connections.public.required` | `false` |
| <a id="declaration-connections-public-readiness"></a>`connections.public.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "authentik-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "authentik"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-secret-key"></a>`secrets.secret_key` | `object` |
| <a id="declaration-secrets-secret-key-required"></a>`secrets.secret_key.required` | `true` |
| <a id="declaration-secrets-postgresql-password"></a>`secrets.postgresql_password` | `object` |
| <a id="declaration-secrets-postgresql-password-required"></a>`secrets.postgresql_password.required` | `true` |
| <a id="declaration-secrets-smtp-password"></a>`secrets.smtp_password` | `object` |
| <a id="declaration-secrets-smtp-password-required"></a>`secrets.smtp_password.required` | `false` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-media"></a>`backup.include.media` | `object` |
| <a id="declaration-backup-include-media-category"></a>`backup.include.media.category` | `"state"` |
| <a id="declaration-backup-include-media-capture"></a>`backup.include.media.capture` | `"application-export"` |
| <a id="declaration-backup-include-templates"></a>`backup.include.templates` | `object` |
| <a id="declaration-backup-include-templates-category"></a>`backup.include.templates.category` | `"configuration"` |
| <a id="declaration-backup-include-templates-capture"></a>`backup.include.templates.capture` | `"files"` |
| <a id="declaration-backup-include-certs"></a>`backup.include.certs` | `object` |
| <a id="declaration-backup-include-certs-category"></a>`backup.include.certs.category` | `"configuration"` |
| <a id="declaration-backup-include-certs-capture"></a>`backup.include.certs.capture` | `"files"` |
| <a id="declaration-backup-include-redis"></a>`backup.include.redis` | `object` |
| <a id="declaration-backup-include-redis-category"></a>`backup.include.redis.category` | `"state"` |
| <a id="declaration-backup-include-redis-capture"></a>`backup.include.redis.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
