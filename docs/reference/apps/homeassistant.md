[Documentation](../../README.md) / [Reference](../README.md)

# Home Assistant

Run Home Assistant with an explicitly supplied custom image archive and existing configuration. Recorder, metrics and MQTT are independent optional integrations.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: homeassistant` |
| Adapter | `homeassistant` |
| Owned containers | `homeassistant` |
| Multiple instances | Fixed host TCP 8123 prevents two identical listeners on one guest. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [homeassistant.yaml](../../../apps/homeassistant.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The site must supply `local_id`, `archive` and `archive_sha256` for the custom image. Zero values in the public catalogue are placeholders, not usable image identities. Select the retained multicast DNS (mDNS) startup capability explicitly when required; it does not imply hardware access.

## First installation

This selection requires the declared custom archive and prepared Home Assistant configuration. It does not build that archive or provide a brand-new custom installation. For the supported public-image creation path, choose [homeassistant-public](homeassistant-public.md).

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/existing-automation.yaml).

```yaml
apps:
  homeassistant:
    profile: homeassistant
    guest: homeassistant
    lifecycle: retained
```

### Practical complete example

Use app `homeassistant` in [examples/catalogue/existing-automation.yaml](../../../examples/catalogue/existing-automation.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/existing-automation.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `home` | No; selected capability can require it | `guest-interface` |
| `database` | No; selected capability can require it | `guest-interface` |
| `metrics` | No; selected capability can require it | `guest-interface` |
| `broker` | No; selected capability can require it | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `homeassistant` / `host` | `wildcard` via `web` | `8123/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can accept connections through interfaces other than the advertised NIC. An endpoint gives consumers an address and port. It does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/config` | directory / writable | None |
| `media` | Conditional / optional | `/media` | directory / writable | None |
| `community` | Conditional / optional | `/hacsfiles` | directory / writable | None |
| `startup` | Conditional / optional | `/startup` | directory / read-only | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `recorder` | `mariadb` | No | `start` | None |
| `metrics` | `influxdb` | No | `start` | None |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| mdns | Optional mapping | `interface` and `startup` name declared roles. The interface role must bind to a physical guest interface, and the storage role must be read-only at `/startup`. This capability requires `lifecycle: retained` and the explicitly selected `homeassistant-mdns` runtime. The base runtime does not grant `NET_ADMIN`. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Select mDNS without its physical interface role, startup binding or explicit runtime requirement | Compilation requires a physical interface, a read-only `/startup` binding and the `homeassistant-mdns` runtime. The app must also use `lifecycle: retained`. |
| Replace the retained archive with the public variant silently | Changes software authority; no fallback is implemented. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`homeassistant-images`](../software-and-runtime.md#registration-software-homeassistant-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`homeassistant`](../software-and-runtime.md#registration-runtime-profiles-homeassistant).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `homeassistant` | `homeassistant` | Versioned local archive; concrete site binding required |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `homeassistant` | 2048 | 2 | 512 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the existing configuration and explicit custom archive binding. Preserve selected integrations and the optional mDNS capability’s startup requirements; a profile update does not rebuild the archive or replace private configuration.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#homeassistant) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [homeassistant.yaml](../../../apps/homeassistant.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"homeassistant"` |
| <a id="declaration-display-name"></a>`display_name` | `"Home Assistant"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-home"></a>`interfaces.home` | `object` |
| <a id="declaration-interfaces-home-required"></a>`interfaces.home.required` | `false` |
| <a id="declaration-interfaces-home-accepts"></a>`interfaces.home.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-database"></a>`interfaces.database` | `object` |
| <a id="declaration-interfaces-database-required"></a>`interfaces.database.required` | `false` |
| <a id="declaration-interfaces-database-accepts"></a>`interfaces.database.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-metrics"></a>`interfaces.metrics` | `object` |
| <a id="declaration-interfaces-metrics-required"></a>`interfaces.metrics.required` | `false` |
| <a id="declaration-interfaces-metrics-accepts"></a>`interfaces.metrics.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-broker"></a>`interfaces.broker` | `object` |
| <a id="declaration-interfaces-broker-required"></a>`interfaces.broker.required` | `false` |
| <a id="declaration-interfaces-broker-accepts"></a>`interfaces.broker.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"homeassistant"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"host"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"web"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `8123` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/config"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `true` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-media"></a>`storage.media` | `object` |
| <a id="declaration-storage-media-target"></a>`storage.media.target` | `"/media"` |
| <a id="declaration-storage-media-read-only"></a>`storage.media.read_only` | `false` |
| <a id="declaration-storage-media-required"></a>`storage.media.required` | `false` |
| <a id="declaration-storage-media-kind"></a>`storage.media.kind` | `"directory"` |
| <a id="declaration-storage-community"></a>`storage.community` | `object` |
| <a id="declaration-storage-community-target"></a>`storage.community.target` | `"/hacsfiles"` |
| <a id="declaration-storage-community-read-only"></a>`storage.community.read_only` | `false` |
| <a id="declaration-storage-community-required"></a>`storage.community.required` | `false` |
| <a id="declaration-storage-community-kind"></a>`storage.community.kind` | `"directory"` |
| <a id="declaration-storage-startup"></a>`storage.startup` | `object` |
| <a id="declaration-storage-startup-target"></a>`storage.startup.target` | `"/startup"` |
| <a id="declaration-storage-startup-read-only"></a>`storage.startup.read_only` | `true` |
| <a id="declaration-storage-startup-required"></a>`storage.startup.required` | `false` |
| <a id="declaration-storage-startup-kind"></a>`storage.startup.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-recorder"></a>`connections.recorder` | `object` |
| <a id="declaration-connections-recorder-type"></a>`connections.recorder.type` | `"mariadb"` |
| <a id="declaration-connections-recorder-required"></a>`connections.recorder.required` | `false` |
| <a id="declaration-connections-recorder-readiness"></a>`connections.recorder.readiness` | `["start"]` |
| <a id="declaration-connections-metrics"></a>`connections.metrics` | `object` |
| <a id="declaration-connections-metrics-type"></a>`connections.metrics.type` | `"influxdb"` |
| <a id="declaration-connections-metrics-required"></a>`connections.metrics.required` | `false` |
| <a id="declaration-connections-metrics-readiness"></a>`connections.metrics.readiness` | `["start"]` |
| <a id="declaration-connections-broker"></a>`connections.broker` | `object` |
| <a id="declaration-connections-broker-type"></a>`connections.broker.type` | `"mqtt"` |
| <a id="declaration-connections-broker-required"></a>`connections.broker.required` | `false` |
| <a id="declaration-connections-broker-readiness"></a>`connections.broker.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "homeassistant-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "homeassistant"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-config"></a>`backup.include.config` | `object` |
| <a id="declaration-backup-include-config-category"></a>`backup.include.config.category` | `"state"` |
| <a id="declaration-backup-include-config-capture"></a>`backup.include.config.capture` | `"application-export"` |
| <a id="declaration-backup-include-media"></a>`backup.include.media` | `object` |
| <a id="declaration-backup-include-media-category"></a>`backup.include.media.category` | `"state"` |
| <a id="declaration-backup-include-media-capture"></a>`backup.include.media.capture` | `"application-export"` |
| <a id="declaration-backup-include-community"></a>`backup.include.community` | `object` |
| <a id="declaration-backup-include-community-category"></a>`backup.include.community.category` | `"state"` |
| <a id="declaration-backup-include-community-capture"></a>`backup.include.community.capture` | `"application-export"` |
| <a id="declaration-backup-include-startup"></a>`backup.include.startup` | `object` |
| <a id="declaration-backup-include-startup-category"></a>`backup.include.startup.category` | `"configuration"` |
| <a id="declaration-backup-include-startup-capture"></a>`backup.include.startup.capture` | `"files"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
