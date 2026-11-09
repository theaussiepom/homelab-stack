[Documentation](../../README.md) / [Reference](../README.md)

# WiNet

Run the independent WiNet poller with explicit inverter, MQTT and private options bindings. It does not require Zigbee2MQTT.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: winet` |
| Adapter | `winet` |
| Owned containers | `winet` |
| Multiple instances | WiNet runs independently of Zigbee. This page does not establish that two WiNet instances can operate on the same guest. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [winet.yaml](../../../apps/winet.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Private options are supplied by the selected options role and validated against the inverter and MQTT metadata. Existing inverter and broker credentials stay inside that protected record; neither is copied into Git.

## First installation

You need an already configured inverter and valid vendor options and credentials stored in the protected record. The profile can update its container, but does not configure the inverter or generate those credentials. The example uses a service that HomeLab already manages.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/messaging-radio.yaml).

```yaml
apps:
  telemetry:
    profile: winet
    guest: telemetry
    lifecycle: retained
```

### Practical complete example

Use app `telemetry` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `broker` | Yes | `guest-interface` |
| `inverter` | Yes | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

No listener is declared by this profile.

No endpoint is advertised.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/6f5e40f50f33c3c3d0e6b06eadb7aa81e78572c7/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

No app storage role is declared. HomeLab keeps generated private runtime files in their separately managed paths.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | Yes | `start` | None |
| `inverter` | `https` | Yes | None | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `options` | Required |

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/6f5e40f50f33c3c3d0e6b06eadb7aa81e78572c7/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| mqtt_prefix | Required string | Use 1..128 characters. The first must be a letter or digit; later characters may also be a slash, underscore or hyphen. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit the protected options role | Refuses the selected private input. |
| Use a non-443/non-HTTPS inverter or malformed discovery prefix | Validation rejects an inverter endpoint unless it uses HTTPS on port 443, and rejects a discovery prefix that does not meet the mqtt_prefix character rules. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`winet-images`](../software-and-runtime.md#registration-software-winet-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`winet`](../software-and-runtime.md#registration-runtime-profiles-winet).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `winet` | `winet` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `winet` | 256 | 1 | 128 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab updates the same service while preserving the existing inverter, private options record and broker connection. It does not reconfigure the physical inverter, replace vendor credentials or commission another device.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/6f5e40f50f33c3c3d0e6b06eadb7aa81e78572c7/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/6f5e40f50f33c3c3d0e6b06eadb7aa81e78572c7/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/6f5e40f50f33c3c3d0e6b06eadb7aa81e78572c7/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/6f5e40f50f33c3c3d0e6b06eadb7aa81e78572c7/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/6f5e40f50f33c3c3d0e6b06eadb7aa81e78572c7/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#winet) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [winet.yaml](../../../apps/winet.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"winet"` |
| <a id="declaration-display-name"></a>`display_name` | `"WiNet"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-broker"></a>`interfaces.broker` | `object` |
| <a id="declaration-interfaces-broker-required"></a>`interfaces.broker.required` | `true` |
| <a id="declaration-interfaces-broker-accepts"></a>`interfaces.broker.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-inverter"></a>`interfaces.inverter` | `object` |
| <a id="declaration-interfaces-inverter-required"></a>`interfaces.inverter.required` | `true` |
| <a id="declaration-interfaces-inverter-accepts"></a>`interfaces.inverter.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `{}` |
| <a id="declaration-endpoints"></a>`endpoints` | `{}` |
| <a id="declaration-storage"></a>`storage` | `{}` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-broker"></a>`connections.broker` | `object` |
| <a id="declaration-connections-broker-type"></a>`connections.broker.type` | `"mqtt"` |
| <a id="declaration-connections-broker-required"></a>`connections.broker.required` | `true` |
| <a id="declaration-connections-broker-readiness"></a>`connections.broker.readiness` | `["start"]` |
| <a id="declaration-connections-inverter"></a>`connections.inverter` | `object` |
| <a id="declaration-connections-inverter-type"></a>`connections.inverter.type` | `"https"` |
| <a id="declaration-connections-inverter-required"></a>`connections.inverter.required` | `true` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "winet-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "winet"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-options"></a>`secrets.options` | `object` |
| <a id="declaration-secrets-options-required"></a>`secrets.options.required` | `true` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `{}` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
