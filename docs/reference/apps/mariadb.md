[Documentation](../../README.md) / [Reference](../README.md)

# MariaDB

Configure the supported native MariaDB package service and conventional existing database directory.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: mariadb` |
| Adapter | `mariadb` |
| Owned containers | None; native package service |
| Multiple instances | One native MariaDB unit per guest. Compatible distinct native adapters still require resource and account-namespace checks. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [mariadb.yaml](../../../apps/mariadb.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The native data path is the supported conventional database directory. TLS/admin/monitoring hooks retain their separate guarded owners; a profile does not initialize users or grant privileges.

## First installation

The native package/configuration creation path can be selected with `lifecycle: fresh` on a supported new guest. Application schema/user setup and data import are separate explicit requirements. The example is source/controller qualification, not a live new-database acceptance test.

Complete creation-policy source: [examples/catalogue/new-native-databases.yaml](../../../examples/catalogue/new-native-databases.yaml), app `mariadb`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/native-databases.yaml).

```yaml
apps:
  mariadb:
    profile: mariadb
    guest: mariadb
    lifecycle: retained
```

### Practical complete example

Use app `mariadb` in [examples/catalogue/native-databases.yaml](../../../examples/catalogue/native-databases.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/native-databases.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `database` | `mariadb` / `host` | `interface` via `service` | `3306/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `backend` | `tcp` | `database` via `service` |

Listeners bind their declared interface or namespace. An endpoint advertises a value; it does not grant traffic or add a readiness wait.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/mysql` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use an arbitrary relocated data path | Refuses the conventional native data-path contract. |
| Select two MariaDB instances on one guest | Refuses the fixed native service/config namespace collision. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`mariadb`](../software-and-runtime.md#registration-software-mariadb). Runtime selections: [`native-mariadb`](../software-and-runtime.md#registration-runtime-profiles-native-mariadb).

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 768 | Guest allocation | Native service |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates native package/configuration while preserving the conventional data directory, database identities and existing TLS/account owners. Application grants change only through their explicit supported capability. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [mariadb.yaml](../../../apps/mariadb.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"mariadb"` |
| <a id="declaration-display-name"></a>`display_name` | `"MariaDB"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service"></a>`interfaces.service` | `object` |
| <a id="declaration-interfaces-service-required"></a>`interfaces.service.required` | `true` |
| <a id="declaration-interfaces-service-accepts"></a>`interfaces.service.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-database"></a>`listeners.database` | `object` |
| <a id="declaration-listeners-database-service"></a>`listeners.database.service` | `"mariadb"` |
| <a id="declaration-listeners-database-namespace"></a>`listeners.database.namespace` | `"host"` |
| <a id="declaration-listeners-database-interface"></a>`listeners.database.interface` | `"service"` |
| <a id="declaration-listeners-database-bind"></a>`listeners.database.bind` | `"interface"` |
| <a id="declaration-listeners-database-protocol"></a>`listeners.database.protocol` | `"tcp"` |
| <a id="declaration-listeners-database-port"></a>`listeners.database.port` | `3306` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-backend"></a>`endpoints.backend` | `object` |
| <a id="declaration-endpoints-backend-listener"></a>`endpoints.backend.listener` | `"database"` |
| <a id="declaration-endpoints-backend-protocol"></a>`endpoints.backend.protocol` | `"tcp"` |
| <a id="declaration-endpoints-backend-via"></a>`endpoints.backend.via` | `"service"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/var/lib/mysql"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `{}` |
| <a id="declaration-software"></a>`software` | `["mariadb"]` |
| <a id="declaration-runtime"></a>`runtime` | `["native-mariadb"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"mariadb-agent"` |
