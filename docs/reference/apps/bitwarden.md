[Documentation](../../README.md) / [Reference](../README.md)

# Bitwarden

Run the existing Bitwarden Lite vault against its selected MariaDB database, preserving installation material and numeric data ownership.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: bitwarden` |
| Adapter | `bitwarden` |
| Owned containers | `bitwarden` |
| Multiple instances | Distinct storage/project/service identities are required; same-guest multi-instance operation is not qualified here. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [bitwarden.yaml](../../../apps/bitwarden.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## First installation

Not implemented by this profile: it cannot create a brand-new vault. The example requires an already HomeLab-managed vault, database, installation keys and data.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/vault.yaml).

```yaml
apps:
  vault:
    profile: bitwarden
    guest: vault
    lifecycle: retained
```

### Practical complete example

Use app `vault` in [examples/catalogue/vault.yaml](../../../examples/catalogue/vault.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/vault.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `database` | Yes | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |
| `private` | Yes | `app-network` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `bitwarden` / `app-network` | `wildcard` via `private` | `8080/tcp` | `guest-interface` 8080 via `web` |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/etc/bitwarden` | directory / writable | None |
| `logs` | Yes | `/var/log/bitwarden` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `mariadb` | Yes | `configure`, `start` | None |
| `public` | `https` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `runtime_environment` | Required |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| issuer | Required mapping | protocol is http or https; domain names a site domains entry. This metadata is separate from the HTTPS app origin. |
| database_name | Required string | Nonempty letters/digits/underscore, matching the sealed runtime environment and selected MariaDB database. |
| data_uid / data_gid | Required positive integers | 1..2147483647, matching existing numeric data ownership and private environment values. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Select lifecycle fresh | Refuses: new-vault creation is unsupported. |
| Supply a floating/local image or an authored environment checksum | Refuses the immutable-image/closed-property contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`bitwarden-images`](../software-and-runtime.md#registration-software-bitwarden-images), [`mariadb-client`](../software-and-runtime.md#registration-software-mariadb-client). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`bitwarden`](../software-and-runtime.md#registration-runtime-profiles-bitwarden).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `bitwarden` | `bitwarden` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `bitwarden` | 1536 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains an already HomeLab-managed vault, preserving its database, installation keys, data and selected protected runtime environment. Software/image changes follow the normal immutable manifest policy; no vault upgrade or credential rotation is implied. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [bitwarden.yaml](../../../apps/bitwarden.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"bitwarden"` |
| <a id="declaration-display-name"></a>`display_name` | `"Bitwarden"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-database"></a>`interfaces.database` | `object` |
| <a id="declaration-interfaces-database-required"></a>`interfaces.database.required` | `true` |
| <a id="declaration-interfaces-database-accepts"></a>`interfaces.database.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management"></a>`interfaces.management` | `object` |
| <a id="declaration-interfaces-management-required"></a>`interfaces.management.required` | `false` |
| <a id="declaration-interfaces-management-accepts"></a>`interfaces.management.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"bitwarden"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"private"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `8080` |
| <a id="declaration-listeners-web-publish"></a>`listeners.web.publish` | `object` |
| <a id="declaration-listeners-web-publish-scope"></a>`listeners.web.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-publish-interface"></a>`listeners.web.publish.interface` | `"web"` |
| <a id="declaration-listeners-web-publish-port"></a>`listeners.web.publish.port` | `8080` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/etc/bitwarden"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-storage-logs"></a>`storage.logs` | `object` |
| <a id="declaration-storage-logs-target"></a>`storage.logs.target` | `"/var/log/bitwarden"` |
| <a id="declaration-storage-logs-read-only"></a>`storage.logs.read_only` | `false` |
| <a id="declaration-storage-logs-required"></a>`storage.logs.required` | `true` |
| <a id="declaration-storage-logs-kind"></a>`storage.logs.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-database"></a>`connections.database` | `object` |
| <a id="declaration-connections-database-type"></a>`connections.database.type` | `"mariadb"` |
| <a id="declaration-connections-database-required"></a>`connections.database.required` | `true` |
| <a id="declaration-connections-database-readiness"></a>`connections.database.readiness` | `["configure", "start"]` |
| <a id="declaration-connections-public"></a>`connections.public` | `object` |
| <a id="declaration-connections-public-type"></a>`connections.public.type` | `"https"` |
| <a id="declaration-connections-public-required"></a>`connections.public.required` | `false` |
| <a id="declaration-connections-public-readiness"></a>`connections.public.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "bitwarden-images", "mariadb-client"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "bitwarden"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-runtime-environment"></a>`secrets.runtime_environment` | `object` |
| <a id="declaration-secrets-runtime-environment-required"></a>`secrets.runtime_environment.required` | `true` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
