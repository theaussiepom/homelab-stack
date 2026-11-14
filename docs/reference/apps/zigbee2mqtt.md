[Documentation](../../README.md) / [Reference](../README.md)

# Zigbee2MQTT

Run the existing Zigbee network through its registered serial coordinator without commissioning or restoring a network.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: zigbee2mqtt` |
| Adapter | `zigbee2mqtt` |
| Owned containers | `zigbee2mqtt` |
| Multiple instances | Use one selected serial coordinator per guest. The helper uses fixed files at /opt/homelab-app/zigbee-settings.json and /opt/homelab-app/zigbee-network.json for its settings and network identity record. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [zigbee2mqtt.yaml](../../../apps/zigbee2mqtt.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Register the serial coordinator explicitly so that HomeLab can check the device against its host and provider. The helper reads its settings from /opt/homelab-app/zigbee-settings.json and preserves the coordinator path and Zigbee network identity recorded in /opt/homelab-app/zigbee-network.json. It checks the network key, PAN ID, extended PAN ID and channel without freezing mutable device databases or counters. Changing an app label does not initialize or rename the Zigbee network.

## First installation

This profile cannot set up a new coordinator or Zigbee network. The example requires an already registered coordinator and a Zigbee network and data directory that HomeLab already manages; it does not reset or initialize the radio.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/messaging-radio.yaml).

```yaml
apps:
  radio:
    profile: zigbee2mqtt
    guest: radio
    lifecycle: retained
```

### Practical complete example

Use app `radio` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web_interface` | Yes | `guest-interface` |
| `broker_interface` | Yes | `guest-interface` |
| `private_interface` | Yes | `app-network` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web_listener` | `zigbee2mqtt` / `app-network` | `wildcard` via `private_interface` | `8099/tcp` | `guest-interface` 8099 via `web_interface` |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |

The web listener accepts connections inside the private app network. Its explicit publication makes TCP port 8099 available through the guest interface bound to `web_interface`. The endpoint advertises the resulting address and port; it does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/app/data` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | Yes | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

| Device role | Type | Required |
| --- | --- | --- |
| `coordinator` | `serial` | Yes |

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| adapter | Required string | Lowercase safe adapter ID `[a-z][a-z0-9_-]{0,62}`. |
| mqtt_base_topic | Required string | Use 1..128 characters. The first must be a letter or digit; later characters may also be a slash, underscore or hyphen. |
| watchdog | Optional string; omitted by this profile | Only `default` is supported. Sets `Z2M_WATCHDOG=default`; omission leaves it unset. Null, Booleans and custom delays are rejected. |

The complete radio example selects `watchdog: default`. The [built-in watchdog](https://www.zigbee2mqtt.io/guide/installation/15_watchdog.html) retries recognized soft failures after 1, 5, 15, 30 and 60 minutes and eventually exits after repeated failed recovery. It requires an initial successful start and respects deliberate stops and configuration errors. A protected CD update can recreate the service to apply this environment setting while preserving its image, coordinator, data, Zigbee identity and MQTT configuration. Enabling it does not establish that a serial fault is fixed; compilation does not test runtime recovery.

## Invalid cases

Start from the complete [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml), app `radio`, using the [source-only setup](../../guides/first-configuration.md). Change only the input described; retain the rest of that composition. Diagnostics below are emitted results, not inferred field paths. Where no `at` context appears, no field path was emitted.

| Invalid variation | Actual refusal and enforcing layer | Cause and supported correction |
| --- | --- | --- |
| <a id="invalid-fresh-lifecycle"></a>Set this app’s `lifecycle` to `fresh`. | `component.initialization-unsupported at apps.radio.properties` — Adapter initialization binding during resolution. | This retained-only selection cannot commission a new installation. Use the genuinely HomeLab-managed retained instance; the label cannot import or initialize it. |
| <a id="invalid-omit-coordinator"></a>Remove the app’s `devices.coordinator` binding. | `component.invalid` — Required device binding during app resolution. | Restore the registered stable USB by-id coordinator for the existing network. Source validation does not verify the live character device or radio identity. |

After repair, resolve the same complete source and generate every guest’s deployment packet; expect both to pass as the unchanged baseline does. Source checks neither inspect credential contents nor establish installation, routing, socket isolation or service recovery on a target.

The existing [complete-profile integrations](../../../tests/test_profile_examples.py) and [composition cases](../../../tests/test_component_composition.py) exercise the real selected framework. Its validators, binding checks and packet/file builders enforce these boundaries; the [testing guide](../../testing.md#documentation-conformance) explains the evidence limits.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`zigbee2mqtt-images`](../software-and-runtime.md#registration-software-zigbee2mqtt-images), [`yaml-parser`](../software-and-runtime.md#registration-software-yaml-parser). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`zigbee2mqtt`](../software-and-runtime.md#registration-runtime-profiles-zigbee2mqtt).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `zigbee2mqtt` | `zigbee2mqtt` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `zigbee2mqtt` | 512 | 2 | 128 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the existing coordinator, network identity and data. Preserve the registered by-id device, adapter, network receipt and broker relationship; ordinary deployment never commissions a new radio. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#zigbee2mqtt) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [zigbee2mqtt.yaml](../../../apps/zigbee2mqtt.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"zigbee2mqtt"` |
| <a id="declaration-display-name"></a>`display_name` | `"Zigbee2MQTT"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-broker-interface"></a>`interfaces.broker_interface` | `object` |
| <a id="declaration-interfaces-broker-interface-required"></a>`interfaces.broker_interface.required` | `true` |
| <a id="declaration-interfaces-broker-interface-accepts"></a>`interfaces.broker_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private-interface"></a>`interfaces.private_interface` | `object` |
| <a id="declaration-interfaces-private-interface-required"></a>`interfaces.private_interface.required` | `true` |
| <a id="declaration-interfaces-private-interface-accepts"></a>`interfaces.private_interface.accepts` | `["app-network"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"zigbee2mqtt"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `8099` |
| <a id="declaration-listeners-web-listener-publish"></a>`listeners.web_listener.publish` | `object` |
| <a id="declaration-listeners-web-listener-publish-scope"></a>`listeners.web_listener.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-listener-publish-interface"></a>`listeners.web_listener.publish.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-publish-port"></a>`listeners.web_listener.publish.port` | `8099` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/app/data"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-broker"></a>`connections.broker` | `object` |
| <a id="declaration-connections-broker-type"></a>`connections.broker.type` | `"mqtt"` |
| <a id="declaration-connections-broker-required"></a>`connections.broker.required` | `true` |
| <a id="declaration-connections-broker-readiness"></a>`connections.broker.readiness` | `["start"]` |
| <a id="declaration-devices"></a>`devices` | `object` |
| <a id="declaration-devices-coordinator"></a>`devices.coordinator` | `object` |
| <a id="declaration-devices-coordinator-type"></a>`devices.coordinator.type` | `"serial"` |
| <a id="declaration-devices-coordinator-required"></a>`devices.coordinator.required` | `true` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "zigbee2mqtt-images", "yaml-parser"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "zigbee2mqtt"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"state"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
