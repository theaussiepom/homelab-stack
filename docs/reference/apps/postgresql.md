[Documentation](../../README.md) / [Reference](../README.md)

# PostgreSQL

Configure the supported native PostgreSQL package service and conventional existing cluster data directory.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: postgresql` |
| Adapter | `postgresql` |
| Owned containers | None; native package service |
| Multiple instances | Use one native PostgreSQL cluster and service unit per guest. HomeLab rejects placing PostgreSQL and InfluxDB together when their required numeric group identities conflict. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [postgresql.yaml](../../../apps/postgresql.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The native data path is the supported conventional cluster path; arbitrary relocation refuses. Explicit `client_access` rows configure PostgreSQL’s host-based authentication (HBA). They are separate from the procedures for managed administration and monitoring. Do not add SUPERUSER through a connection reference.

## First installation

On a supported new guest, select `lifecycle: fresh` to install and configure the native package. It does not infer application databases, user grants or data import. The creation source compiles; no live database commissioning was performed for this example.

For a complete example using the creation policy, see [examples/catalogue/new-native-databases.yaml](../../../examples/catalogue/new-native-databases.yaml), app `postgresql`. The example must resolve and generate deployment files successfully. These checks do not prove that the service has been deployed.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/native-databases.yaml).

```yaml
apps:
  postgresql:
    profile: postgresql
    guest: postgresql
    lifecycle: retained
```

### Practical complete example

Use app `postgresql` in [examples/catalogue/native-databases.yaml](../../../examples/catalogue/native-databases.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/native-databases.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service_interface` | Yes | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `database_listener` | `postgresql` / `host` | `interface` via `service_interface` | `5432/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `backend_endpoint` | `tcp` | `database_listener` via `service_interface` |

Listeners use the declared interface or network namespace. Endpoints tell consumers where to connect; they do not permit traffic or make consumers wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/postgresql` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| client_access | Optional list, default empty | Supply at most 128 explicit rows. Each source is {app,interface}, selecting a named app and its interface role. The only supported values are database:all, user:all and method:scram-sha-256. Rows retain their authored order; a connection does not create an access grant. |

## Invalid cases

Start from the complete [examples/catalogue/native-databases.yaml](../../../examples/catalogue/native-databases.yaml), app `postgresql`, using the [source-only setup](../../guides/first-configuration.md). Change only the input described; retain the rest of that composition. Diagnostics below are emitted results, not inferred field paths. Where no `at` context appears, no field path was emitted.

| Invalid variation | Actual refusal and enforcing layer | Cause and supported correction |
| --- | --- | --- |
| <a id="invalid-relocated-native-data"></a>Change the native `storage.data.subpath` from the empty string to `relocated`. | `Native PostgreSQL and MariaDB data relocation is not implemented` — Deployment-file generation: native data-path renderer. | The selected PostgreSQL/MariaDB path must remain its conventional native location. Restore the empty subpath on the existing native root. This plain `ValueError` has no structured diagnostic code or field path; it does not authorize moving data. |
| <a id="invalid-raw-native-config"></a>Add `properties.config: unrestricted native config text`. | `component.fields at apps.postgresql.properties` — Closed app-property validation. | The native adapter accepts no arbitrary application configuration keys. Remove it and use only the typed profile bindings; accepted YAML does not permit a raw config override. |

After repair, resolve the same complete source and generate every guest’s deployment packet; expect both to pass as the unchanged baseline does. Source checks neither inspect credential contents nor establish installation, routing, socket isolation or service recovery on a target.

The existing [complete-profile integrations](../../../tests/test_profile_examples.py) and [composition cases](../../../tests/test_component_composition.py) exercise the real selected framework. Its validators, binding checks and packet/file builders enforce these boundaries; the [testing guide](../../testing.md#documentation-conformance) explains the evidence limits.

## Software and resource policy

Software selections: [`postgresql`](../software-and-runtime.md#registration-software-postgresql). Runtime selections: [`native-postgresql`](../software-and-runtime.md#registration-runtime-profiles-native-postgresql).

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 1792 | Guest allocation | Native service |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab updates the native package and configuration while preserving the conventional cluster data and account owners. Explicit base client-access rows keep their authored order; managed administration and monitoring remain separate selected capabilities.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#postgresql) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [postgresql.yaml](../../../apps/postgresql.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"postgresql"` |
| <a id="declaration-display-name"></a>`display_name` | `"PostgreSQL"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service-interface"></a>`interfaces.service_interface` | `object` |
| <a id="declaration-interfaces-service-interface-required"></a>`interfaces.service_interface.required` | `true` |
| <a id="declaration-interfaces-service-interface-accepts"></a>`interfaces.service_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-database-listener"></a>`listeners.database_listener` | `object` |
| <a id="declaration-listeners-database-listener-service"></a>`listeners.database_listener.service` | `"postgresql"` |
| <a id="declaration-listeners-database-listener-namespace"></a>`listeners.database_listener.namespace` | `"host"` |
| <a id="declaration-listeners-database-listener-interface"></a>`listeners.database_listener.interface` | `"service_interface"` |
| <a id="declaration-listeners-database-listener-bind"></a>`listeners.database_listener.bind` | `"interface"` |
| <a id="declaration-listeners-database-listener-protocol"></a>`listeners.database_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-database-listener-port"></a>`listeners.database_listener.port` | `5432` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-backend-endpoint"></a>`endpoints.backend_endpoint` | `object` |
| <a id="declaration-endpoints-backend-endpoint-listener"></a>`endpoints.backend_endpoint.listener` | `"database_listener"` |
| <a id="declaration-endpoints-backend-endpoint-protocol"></a>`endpoints.backend_endpoint.protocol` | `"tcp"` |
| <a id="declaration-endpoints-backend-endpoint-via"></a>`endpoints.backend_endpoint.via` | `"service_interface"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/var/lib/postgresql"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `{}` |
| <a id="declaration-software"></a>`software` | `["postgresql"]` |
| <a id="declaration-runtime"></a>`runtime` | `["native-postgresql"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"postgresql-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"database"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"database-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
