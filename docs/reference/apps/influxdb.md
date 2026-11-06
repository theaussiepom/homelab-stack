[Documentation](../../README.md) / [Reference](../README.md)

# InfluxDB

Configure the supported native InfluxDB package service and its declared existing data path.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: influxdb` |
| Adapter | `influxdb` |
| Owned containers | None; native package service |
| Multiple instances | One native InfluxDB unit per guest. PostgreSQL + InfluxDB numeric-group namespace conflicts refuse. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [influxdb.yaml](../../../apps/influxdb.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The typed data role drives the existing native configuration. Organization, token and bucket setup are not inferred from a listener or profile name.

## First installation

The native package/configuration creation path can be selected with `lifecycle: fresh` on a supported new guest. It does not infer an organization, bucket, token or data import. Target commissioning and usable application credentials need their own verification.

Complete creation-policy source: [examples/catalogue/new-native-databases.yaml](../../../examples/catalogue/new-native-databases.yaml), app `influxdb`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/native-databases.yaml).

```yaml
apps:
  influxdb:
    profile: influxdb
    guest: influxdb
    lifecycle: retained
```

### Practical complete example

Use app `influxdb` in [examples/catalogue/native-databases.yaml](../../../examples/catalogue/native-databases.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

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
| `web` | `influxdb` / `host` | `interface` via `service` | `8086/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `service` |

Listeners bind their declared interface or namespace. An endpoint advertises a value; it does not grant traffic or add a readiness wait.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/influxdb` | directory / writable | None |

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
| Co-locate with conflicting native group ownership | Refuses native namespace collision. |
| Supply arbitrary raw native config text as app properties | Refuses the closed typed property contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`influxdb`](../software-and-runtime.md#registration-software-influxdb). Runtime selections: [`native-influxdb`](../software-and-runtime.md#registration-runtime-profiles-native-influxdb).

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 1792 | Guest allocation | Native service |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates the declared native package/configuration while preserving the selected data directory. Existing organization, bucket and token ownership remains separate; a public configuration edit does not recreate them. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [influxdb.yaml](../../../apps/influxdb.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"influxdb"` |
| <a id="declaration-display-name"></a>`display_name` | `"InfluxDB"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service"></a>`interfaces.service` | `object` |
| <a id="declaration-interfaces-service-required"></a>`interfaces.service.required` | `true` |
| <a id="declaration-interfaces-service-accepts"></a>`interfaces.service.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"influxdb"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"host"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"service"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"interface"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `8086` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"service"` |
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
