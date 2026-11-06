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

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [authentik.yaml](../../../apps/authentik.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

secret_key and postgresql_password are required distinct private roles. smtp_password is conditional on SMTP configuration. Redis is supporting infrastructure owned by this app, not a mandatory separately placed app.

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

Use app `identity` in [examples/catalogue/identity-monitoring.yaml](../../../examples/catalogue/identity-monitoring.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/identity-monitoring.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

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

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

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

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

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

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

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

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Reconciles the owned server, worker and dedicated Redis configuration while preserving the PostgreSQL data and selected application keys. Existing users/provider/client registrations are not rebuilt from the profile. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [authentik.yaml](../../../apps/authentik.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

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
