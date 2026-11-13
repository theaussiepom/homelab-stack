[Documentation](../../README.md) / [Reference](../README.md)

# InfluxDB: separate application web frontend

Configure the supported native InfluxDB package service and its declared existing data path.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: influxdb-web` |
| Adapter | `influxdb` |
| Owned containers | None; native package service |
| Multiple instances | One native InfluxDB unit per guest. HomeLab rejects placing PostgreSQL and InfluxDB together when their required numeric group identities conflict. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [influxdb-web.yaml](../../../apps/influxdb-web.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The data role selects the directory used by the native service configuration. Organization, token and bucket setup are not inferred from a listener or profile name.

## Separate listener behaviour

InfluxDB serves its UI and API on one port. This variant keeps the native database on `service:8086` and adds a local systemd socket proxy on `web:8086`. Both remain the same authenticated server: the frontend is not a read-only API or a second database. Bind existing metrics clients to endpoint `backend`, and only web publication to `web`. The two addresses must differ. The existing systemd-socket-proxyd executable and the HomeLab network-ready gate are required; no Docker engine is added. The frontend owns only the fixed homelab-influxdb-web.socket/service units, refuses foreign files and starts the socket after networking/database startup. HomeLab also generates `/etc/influxdb/config.toml` from the selected `service` address and data path; changing those bindings changes the native configuration. It preserves database data and credentials. Switching back to the ordinary profile removes only those owned frontend units. Linux traffic forwarded to the same host database address stays local; it is not a new inter-guest database grant.

## First installation

On a supported new guest, select `lifecycle: fresh` to install and configure the native package. It does not infer an organization, bucket, token or data import. You must separately verify the running installation and its application credentials.

For a complete example using the creation policy, see [examples/catalogue/new-influxdb-web.yaml](../../../examples/catalogue/new-influxdb-web.yaml), app `influxdb`. The example must resolve and generate deployment files successfully. These checks do not prove that the service has been deployed.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/native-databases-web.yaml).

```yaml
apps:
  influxdb:
    profile: influxdb-web
    guest: influxdb
    lifecycle: retained
```

### Practical complete example

Use app `influxdb` in [examples/catalogue/native-databases-web.yaml](../../../examples/catalogue/native-databases-web.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/native-databases-web.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service_interface` | Yes | `guest-interface` |
| `web_interface` | Yes | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `backend_listener` | `influxdb` / `host` | `interface` via `service_interface` | `8086/tcp` | Native database socket |
| `web_listener` | `influxdb` / `host` | `interface` via `web_interface` | `8086/tcp` | Owned systemd TCP frontend |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `backend_endpoint` | `http` | `backend_listener` via `service_interface` |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |

Listeners use the declared interface or network namespace. Endpoints tell consumers where to connect; they do not permit traffic or make consumers wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/influxdb` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/app-properties.md).

This adapter accepts no application property keys. It rejects unknown keys and provides no way to pass arbitrary commands, environment variables or mounts.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Co-locate with conflicting native group ownership | HomeLab rejects the placement because the services require conflicting numeric group identities. |
| Supply arbitrary raw native config text as app properties | Property validation rejects arbitrary native configuration text; this adapter accepts no application property keys. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`influxdb`](../software-and-runtime.md#registration-software-influxdb). Runtime selections: [`native-influxdb`](../software-and-runtime.md#registration-runtime-profiles-native-influxdb).

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 1792 | Guest allocation | Native service |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab updates the declared native package and configuration while preserving the selected data directory. Existing organization, bucket and token ownership remains separate; a public configuration edit does not recreate them.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#influxdb-web) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

Complete values from [influxdb-web.yaml](../../../apps/influxdb-web.yaml). [Reading declaration records](../declaration-records.md) explains binding and ownership.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"influxdb"` |
| <a id="declaration-display-name"></a>`display_name` | `"InfluxDB with a separate application web frontend"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service-interface"></a>`interfaces.service_interface` | `object` |
| <a id="declaration-interfaces-service-interface-required"></a>`interfaces.service_interface.required` | `true` |
| <a id="declaration-interfaces-service-interface-accepts"></a>`interfaces.service_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-backend-listener"></a>`listeners.backend_listener` | `object` |
| <a id="declaration-listeners-backend-listener-service"></a>`listeners.backend_listener.service` | `"influxdb"` |
| <a id="declaration-listeners-backend-listener-namespace"></a>`listeners.backend_listener.namespace` | `"host"` |
| <a id="declaration-listeners-backend-listener-interface"></a>`listeners.backend_listener.interface` | `"service_interface"` |
| <a id="declaration-listeners-backend-listener-bind"></a>`listeners.backend_listener.bind` | `"interface"` |
| <a id="declaration-listeners-backend-listener-protocol"></a>`listeners.backend_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-backend-listener-port"></a>`listeners.backend_listener.port` | `8086` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"influxdb"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"host"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"interface"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `8086` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-backend-endpoint"></a>`endpoints.backend_endpoint` | `object` |
| <a id="declaration-endpoints-backend-endpoint-listener"></a>`endpoints.backend_endpoint.listener` | `"backend_listener"` |
| <a id="declaration-endpoints-backend-endpoint-protocol"></a>`endpoints.backend_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-backend-endpoint-via"></a>`endpoints.backend_endpoint.via` | `"service_interface"` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/var/lib/influxdb"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `{}` |
| <a id="declaration-software"></a>`software` | `["influxdb"]` |
| <a id="declaration-runtime"></a>`runtime` | `["native-influxdb"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"influxdb-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"database"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"database-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
