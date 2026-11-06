[Documentation](../../README.md) / [Reference](../README.md)

# MQTT

Run the Mosquitto broker using the explicitly bound existing configuration, persistence and log directories.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: mqtt` |
| Adapter | `mqtt` |
| Owned containers | `mqtt` |
| Multiple instances | The [selected listener port](#declaration-listeners-mqtt-port) conflicts with another overlapping broker listener on the same guest. |

The platform is Debian 13 LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [mqtt.yaml](../../../apps/mqtt.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The profile marks `probe` as optional metadata, but the current MQTT adapter requires it to select an existing controller MQTT probe record through a file secret source. A source without that binding refuses with `component.secret-required`. The record is distinct from GUI, application and identity credentials. Ordinary account changes use the guarded parent-mounted password-file/HUP path and do not recreate peer clients.

## First installation

Requires valid prepared Mosquitto configuration/data directories and the existing controller probe record. The profile does not invent broker configuration, ACLs or arbitrary accounts. The practical example uses an already HomeLab-managed broker.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/messaging-radio.yaml).

```yaml
apps:
  broker:
    profile: mqtt
    guest: broker
    lifecycle: retained
```

### Practical complete example

Use app `broker` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Complete broker entry

This is a **complete `apps.broker` map entry**, excerpted from [the canonical messaging composition](../../../examples/catalogue/messaging-radio.yaml). Place it under the site's `apps` mapping; the complete source supplies every guest, NIC, root path, project, identity and file-source reference. The documentation check compares this excerpt to that source.

```yaml
broker:
  profile: mqtt
  guest: broker
  lifecycle: retained
  interfaces:
    backend:
      interface: primary
    frontend:
      interface: primary
  storage:
    config:
      root_path: data
      subpath: broker/config
    data:
      root_path: data
      subpath: broker/data
    log:
      root_path: data
      subpath: broker/log
  identity:
    phase: broker
    runtime_id: example-broker
    services:
      mqtt: broker_mqtt
    networks: {}
    runtime_directory: /opt/homelab-app/runtime/broker
    project: broker
  secrets:
    probe: broker_probe
```

The guest's `primary` NIC supplies both endpoint addresses; `backend` and `frontend` advertise one host TCP listener, not two isolated sockets. Root path `data` and its confined subpaths determine the three mounts. The explicit retained identity must match genuine HomeLab ownership at deployment. See [interface binding](../../guides/multiple-interfaces.md), [storage rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md) and [later deployments](#later-deployments).

## Resolved result

The real resolver derives both broker endpoints from the bound guest NIC and TCP port from the listener. It selects host networking, app-scoped image/runtime requirements and all three storage targets; the lowerer emits the owned Compose/runtime configuration and adapter health contract. The integration compares endpoint values with the canonical guest/listener source and requires packet lowering to succeed.

The composition's Explorer, radio and telemetry consumers have explicitly declared targets. Mere co-location in source does not connect them to this broker. [Consumer connections](../../guides/connect-apps.md) distinguish values from readiness, network access, credentials and managed accounts. No device role, inbound HTTP route, OAuth client or consumer connection role is selected by the MQTT profile.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `backend` | [Required flag](#declaration-interfaces-backend-required) | [Allowed scopes](#declaration-interfaces-backend-accepts) |
| `frontend` | [Required flag](#declaration-interfaces-frontend-required) | [Allowed scopes](#declaration-interfaces-frontend-accepts) |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

The summary links to the checked declaration cells so listener values have one maintained location. Use those records with the [binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect).

| Listener | Owned socket | Binding | Port and transport |
| --- | --- | --- | --- |
| [Broker listener](#declaration-listeners-mqtt) | [Service](#declaration-listeners-mqtt-service) and [namespace](#declaration-listeners-mqtt-namespace) | [Bind choice](#declaration-listeners-mqtt-bind) and [interface role](#declaration-listeners-mqtt-interface) | [Port](#declaration-listeners-mqtt-port) and [protocol](#declaration-listeners-mqtt-protocol) |

| Endpoint | Protocol | Address and port derivation |
| --- | --- | --- |
| `backend` | [Selected protocol](#declaration-endpoints-backend-protocol) | [Listener](#declaration-endpoints-backend-listener) supplies the port; [interface role](#declaration-endpoints-backend-via) supplies the address. |
| `frontend` | [Selected protocol](#declaration-endpoints-frontend-protocol) | [Listener](#declaration-endpoints-frontend-listener) supplies the port; [interface role](#declaration-endpoints-frontend-via) supplies the address. |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Presence | Container target | Kind and access |
| --- | --- | --- | --- |
| `config` | [Required flag](#declaration-storage-config-required) | [Target path](#declaration-storage-config-target) | [Kind](#declaration-storage-config-kind) and [read-only flag](#declaration-storage-config-read-only) |
| `data` | [Required flag](#declaration-storage-data-required) | [Target path](#declaration-storage-data-target) | [Kind](#declaration-storage-data-kind) and [read-only flag](#declaration-storage-data-read-only) |
| `log` | [Required flag](#declaration-storage-log-required) | [Target path](#declaration-storage-log-target) | [Kind](#declaration-storage-log-kind) and [read-only flag](#declaration-storage-log-read-only) |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

| App secret role | Requirement |
| --- | --- |
| `probe` | Required by the current adapter; bind a file secret source |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

<a id="mqtt-probe"></a>
## Probe binding

**Type and reference:** a site identifier string selecting `secret_sources.<name>` in the same complete site. For this adapter the selected source MUST be `{type: file, path: ABSOLUTE_PATH}`; file path syntax is defined by the compatible [secret-source contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/identity-and-secrets.md). The source is controller metadata. Resolving it does not read its file or create an account.

**Presence/default:** required by the selected MQTT adapter even though profile metadata marks the role optional. No source/default credential is inserted. Omission reaches `component.secret-required`; a valid environment source also fails this file-only floor. A null/empty identifier is not an omission alternative and does not satisfy reference/type rules. The [diagnostic example](#invalid-cases) demonstrates omission from an otherwise valid source.

**Material and output:** the runtime parser accepts one existing JSON probe record with exactly `username` and `password`, both nonempty strings of at most 65,535 UTF-8 bytes without CR/LF/NUL. It prepares private `mqtt-probe.json` owned by UID/GID 0 with mode 0600 under the app's selected runtime directory. No actual values belong in public documentation or source. See [probe parser](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/mqtt_runtime.py) and [binding floor](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_foundations.py).

**Lifecycle:** supply a genuinely existing probe account and prepared broker that accepts it. This record is distinct from application/GUI/identity credentials. Ordinary private-material continuity rules apply; changing a source name or path does not authorize rotation. Source compilation neither checks credential contents nor proves broker acceptance. The adapter's health definition checks authenticated acceptance and anonymous refusal after actual deployment; this source suite does not perform that target check.

<a id="mqtt-password-file"></a>
## Password file

**Purpose:** names the existing Mosquitto password file for the separately selected managed MQTT-account capability. It does not create `mosquitto.conf`, an ACL or arbitrary broker accounts. A plain broker with an existing explicit credential consumer can omit it, as in the [canonical composition](#complete-broker-entry).

**Type and constraint:** optional string matching `/mosquitto/config/[A-Za-z0-9_.-]{1,100}`; the basename cannot be `.` or `..`. This is a path inside the declared config mount, not a secret-source ID or controller path. Absolute paths elsewhere, nested subdirectories, null and the empty string fail `component.property`. No units, enum or nested object apply.

**Conditional requirement:** when a supported MQTT Explorer connection selects a managed account on this broker, the resolver requires this property and supplies it to that account path; absence then fails `component.broker-binding`. An Explorer connection using an explicit existing credential is a different mode and does not create that managed account. See the compatible [connection/account rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_foundations.py) and [Explorer's choice](mqtt_explorer.md).

**Default/resolution:** no default is declared in this profile; omission leaves it absent. The resolver copies direct profile property keys then replaces them with explicit site property keys. This field is scalar, so no recursive merge applies. The MQTT property object is closed: `password_file` is its only accepted key at this snapshot. `port: 1884` is not an available override and fails `component.fields`.

**Conditional syntax fragment**, to be placed in an otherwise valid broker instance whose separately declared managed-account composition requires it:

```yaml
properties:
  password_file: /mosquitto/config/passwords
```

This fragment passes the property's value rule; it does not by itself select or prove the account operation. That operation uses the supported parent-mounted password-file/HUP path and its continuity checks. HUP is a broker reload interaction; it is not a promise that every broker update avoids a restart. See [lifecycle](#later-deployments) and [invalid property diagnostics](#invalid-cases).


## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| `password_file` | Conditional string | See [Password file](#mqtt-password-file) for the exact basename rule, omitted/null/empty behavior and managed-account condition; no implicit config/ACL creation. |

## Invalid cases

Start from the complete valid messaging composition and change only the input shown. These source-only tests reach the selected resolver/adapter, without reading a credential file or contacting a broker.

| Invalid input | Actual refusal and layer | Correction |
| --- | --- | --- |
| Omit `apps.broker.secrets.probe`, or point it to a valid environment source | `component.secret-required at apps.broker.properties` in the MQTT adapter resolution floor. The diagnostic context is the adapter's properties scope, not the literal secret-source field. | Bind the existing file source described in [Probe binding](#mqtt-probe). |
| Set `properties.password_file: /elsewhere/passwords` | `component.property at apps.broker.properties` in MQTT property validation | Use the supported container config basename from [Password file](#mqtt-password-file). |
| Add `properties.port: 1884` | `component.fields at apps.broker.properties` in the closed property validator | MQTT has no port override; use supported placement with distinct guest sockets. |

After repair, resolve and lower the same complete source. These checks prove the refusal boundary and valid source result; they do not prove credential contents, authentication or listener isolation on a target. [Troubleshooting](../../troubleshooting.md#mqtt-probe-refusal) links back to these inputs.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`mqtt-images`](../software-and-runtime.md#registration-software-mqtt-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`mqtt`](../software-and-runtime.md#registration-runtime-profiles-mqtt).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `mqtt` | `mqtt` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `mqtt` | 256 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

| Change or condition | Supported effect and boundary |
| --- | --- |
| Same owned app/configuration/image selection under ordinary CD | Reconciles the declared broker/runtime. Container configuration or image changes may recreate/restart the broker; uninterrupted clients are not promised. |
| Explicit supported managed MQTT-account operation | Uses the guarded parent-mounted password-file/HUP path and its continuity checks; it is not arbitrary ACL/configuration generation. |
| Existing data/config/log identity | Retained bindings are verified, not silently relocated or chowned. A different source path is not import authority. |
| Probe material or source-name change | Private-material continuity and genuine current receipts still apply; changing metadata does not authorize credential rotation. |
| Foreign broker, missing ownership or unresolved HOLD | Ordinary deployment must refuse; follow the actual diagnostic owner rather than clearing records. |
| Version migration, restore, arbitrary replacement or hardware behavior | Not qualified by this source suite. A vendor image or successful compiler check supplies no service-acceptance evidence. |


Reconciles the owned broker configuration/container and probe binding. Existing broker data and credentials stay owned. The guarded password-file/HUP path applies only when the separate managed-account capability is explicitly selected. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [mqtt.yaml](../../../apps/mqtt.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"mqtt"` |
| <a id="declaration-display-name"></a>`display_name` | `"MQTT"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-backend"></a>`interfaces.backend` | `object` |
| <a id="declaration-interfaces-backend-required"></a>`interfaces.backend.required` | `true` |
| <a id="declaration-interfaces-backend-accepts"></a>`interfaces.backend.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-frontend"></a>`interfaces.frontend` | `object` |
| <a id="declaration-interfaces-frontend-required"></a>`interfaces.frontend.required` | `true` |
| <a id="declaration-interfaces-frontend-accepts"></a>`interfaces.frontend.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-mqtt"></a>`listeners.mqtt` | `object` |
| <a id="declaration-listeners-mqtt-service"></a>`listeners.mqtt.service` | `"mqtt"` |
| <a id="declaration-listeners-mqtt-namespace"></a>`listeners.mqtt.namespace` | `"host"` |
| <a id="declaration-listeners-mqtt-interface"></a>`listeners.mqtt.interface` | `"backend"` |
| <a id="declaration-listeners-mqtt-bind"></a>`listeners.mqtt.bind` | `"wildcard"` |
| <a id="declaration-listeners-mqtt-protocol"></a>`listeners.mqtt.protocol` | `"tcp"` |
| <a id="declaration-listeners-mqtt-port"></a>`listeners.mqtt.port` | `1883` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-backend"></a>`endpoints.backend` | `object` |
| <a id="declaration-endpoints-backend-listener"></a>`endpoints.backend.listener` | `"mqtt"` |
| <a id="declaration-endpoints-backend-protocol"></a>`endpoints.backend.protocol` | `"tcp"` |
| <a id="declaration-endpoints-backend-via"></a>`endpoints.backend.via` | `"backend"` |
| <a id="declaration-endpoints-frontend"></a>`endpoints.frontend` | `object` |
| <a id="declaration-endpoints-frontend-listener"></a>`endpoints.frontend.listener` | `"mqtt"` |
| <a id="declaration-endpoints-frontend-protocol"></a>`endpoints.frontend.protocol` | `"tcp"` |
| <a id="declaration-endpoints-frontend-via"></a>`endpoints.frontend.via` | `"frontend"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/mosquitto/config"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `true` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/mosquitto/data"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-storage-log"></a>`storage.log` | `object` |
| <a id="declaration-storage-log-target"></a>`storage.log.target` | `"/mosquitto/log"` |
| <a id="declaration-storage-log-read-only"></a>`storage.log.read_only` | `false` |
| <a id="declaration-storage-log-required"></a>`storage.log.required` | `true` |
| <a id="declaration-storage-log-kind"></a>`storage.log.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `{}` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "mqtt-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "mqtt"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-probe"></a>`secrets.probe` | `object` |
| <a id="declaration-secrets-probe-required"></a>`secrets.probe.required` | `false` |
