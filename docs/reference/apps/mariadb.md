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

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [mariadb.yaml](../../../apps/mariadb.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The native data path is the supported conventional database directory. TLS, administration and monitoring use their own procedures and ownership checks. Selecting this profile does not create users or grant privileges.

## First installation

On a supported new guest, select `lifecycle: fresh` to install and configure the native package. Setting up application schemas and users and importing data are separate explicit requirements. The example checks source and controller behavior. It does not verify a newly installed database on a running target.

For a complete example using the creation policy, see [examples/catalogue/new-native-databases.yaml](../../../examples/catalogue/new-native-databases.yaml), app `mariadb`. The example must resolve and generate deployment files successfully. These checks do not prove that the service has been deployed.

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

Use app `mariadb` in [examples/catalogue/native-databases.yaml](../../../examples/catalogue/native-databases.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/native-databases.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

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

Listeners use the declared interface or network namespace. Endpoints tell consumers where to connect; they do not permit traffic or make consumers wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/67ece252410027df38e2a82d5293149a018fce67/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/mysql` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/67ece252410027df38e2a82d5293149a018fce67/docs/reference/app-properties.md).

This adapter accepts no application property keys. It rejects unknown keys and provides no way to pass arbitrary commands, environment variables or mounts.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use an arbitrary relocated data path | Validation rejects the relocation: MariaDB must use the supported /var/lib/mysql directory. |
| Select two MariaDB instances on one guest | Validation rejects the placement because both instances would use the same fixed service and configuration names. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`mariadb`](../software-and-runtime.md#registration-software-mariadb). Runtime selections: [`native-mariadb`](../software-and-runtime.md#registration-runtime-profiles-native-mariadb).

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 768 | Guest allocation | Native service |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab updates the native package and configuration while preserving the conventional data directory, database identities and the existing owners of TLS files and accounts. Application grants change only through their explicit supported capability.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/67ece252410027df38e2a82d5293149a018fce67/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/67ece252410027df38e2a82d5293149a018fce67/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/67ece252410027df38e2a82d5293149a018fce67/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/67ece252410027df38e2a82d5293149a018fce67/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/67ece252410027df38e2a82d5293149a018fce67/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#mariadb) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [mariadb.yaml](../../../apps/mariadb.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

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
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"database"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"database-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
