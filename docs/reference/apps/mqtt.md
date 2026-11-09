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

This profile runs on Debian 13 LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [mqtt.yaml](../../../apps/mqtt.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The profile marks `probe` as optional metadata, but the current MQTT adapter requires it to select an existing controller MQTT probe record through a file secret source. A source without that binding refuses with `component.secret-required`. The probe uses a separate account from GUI, application and identity-provider credentials. Ordinary account changes use the supported procedure: mount the password file’s parent directory, update the file, then send HUP to reload the broker. This procedure does not recreate peer clients.

## First installation

You need valid Mosquitto configuration and data directories, plus the existing probe record on the controller. The profile does not invent broker configuration, ACLs or arbitrary accounts. The practical example uses an already HomeLab-managed broker.

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

Use app `broker` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

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

The guest’s `primary` NIC supplies both endpoint addresses. `backend` and `frontend` advertise the same host TCP listener; they do not create separate sockets. Root path `data` and subpaths within it determine the three mounts. At deployment, the explicit retained identity must match the records proving that HomeLab already manages this broker. See [interface binding](../../guides/multiple-interfaces.md), [storage rules](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/storage.md) and [later deployments](#later-deployments).

## Resolved result

The resolver takes each broker endpoint’s address from the selected guest NIC and its TCP port from the listener. It selects host networking, the image and runtime requirements for this app, and all three storage locations. The deployment-file generator then produces the broker’s Compose configuration, runtime settings and health-check definition. The integration test compares the endpoint values with the guest and listener definitions and checks that all deployment files can be generated.

The composition's Explorer, radio and telemetry consumers have explicitly declared targets. Mere co-location in source does not connect them to this broker. [Consumer connections](../../guides/connect-apps.md) distinguish values from readiness, network access, credentials and managed accounts. No device role, inbound HTTP route, OAuth client or consumer connection role is selected by the MQTT profile.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

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

A wildcard host listener can accept connections through interfaces other than the advertised NIC. An endpoint gives consumers an address and port. It does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Presence | Container target | Kind and access |
| --- | --- | --- | --- |
| `config` | [Required flag](#declaration-storage-config-required) | [Target path](#declaration-storage-config-target) | [Kind](#declaration-storage-config-kind) and [read-only flag](#declaration-storage-config-read-only) |
| `data` | [Required flag](#declaration-storage-data-required) | [Target path](#declaration-storage-data-target) | [Kind](#declaration-storage-data-kind) and [read-only flag](#declaration-storage-data-read-only) |
| `log` | [Required flag](#declaration-storage-log-required) | [Target path](#declaration-storage-log-target) | [Kind](#declaration-storage-log-kind) and [read-only flag](#declaration-storage-log-read-only) |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

| App secret role | Requirement |
| --- | --- |
| `probe` | Required by the current adapter; bind a file secret source |

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

<a id="mqtt-probe"></a>
## Probe binding

**Type and reference:** a site identifier string selecting `secret_sources.<name>` in the same complete site. For this adapter the selected source MUST be `{type: file, path: ABSOLUTE_PATH}`; file path syntax is defined by the compatible [secret-source contract](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/identity-and-secrets.md). The source identifies a file on the controller. Resolving the reference does not read the file or create an account.

**Presence/default:** the MQTT adapter requires this role even though the profile metadata marks it optional. There is no default source or credential. Omitting it produces `component.secret-required`. An environment source is also rejected because this adapter requires a file. Null and empty identifiers fail the reference and type checks. The [diagnostic example](#invalid-cases) demonstrates omission from an otherwise valid source.

**Material and output:** the runtime parser accepts one existing JSON probe record with exactly `username` and `password`, both nonempty strings of at most 65,535 UTF-8 bytes without carriage returns (CR), line feeds (LF) or NUL characters. It prepares private `mqtt-probe.json` owned by UID 0 and GID 0 with mode 0600 under the app's selected runtime directory. No actual values belong in public documentation or source. See [probe parser](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/proxmox/applications/mqtt_runtime.py) and [required probe binding](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/blueprints/component_foundations.py).

**Lifecycle:** supply a genuinely existing probe account and prepared broker that accepts it. This record is separate from application credentials, GUI credentials and credentials for an identity service. Ordinary updates must preserve the existing private inputs. Changing a source name or path does not authorize credential rotation. Source compilation neither checks credential contents nor proves broker acceptance. The adapter's health definition checks authenticated acceptance and anonymous refusal after actual deployment; this source suite does not perform that target check.

<a id="mqtt-password-file"></a>
## Password file

**Purpose:** names the existing Mosquitto password file for the separately selected managed MQTT-account capability. It does not create `mosquitto.conf`, an ACL or arbitrary broker accounts. A plain broker with an existing explicit credential consumer can omit it, as in the [canonical composition](#complete-broker-entry).

**Type and constraint:** optional string matching `/mosquitto/config/[A-Za-z0-9_.-]{1,100}`; the basename cannot be `.` or `..`. This is a path inside the declared config mount, not a secret-source ID or controller path. Absolute paths elsewhere, nested subdirectories, null and the empty string fail `component.property`. No units, enum or nested object apply.

**Conditional requirement:** when a supported MQTT Explorer connection selects a managed account on this broker, the resolver requires this property and supplies it to the procedure that creates the account; absence then fails `component.broker-binding`. An Explorer connection using an explicit existing credential is a different mode and does not create that managed account. See the compatible [connection/account rules](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/blueprints/component_foundations.py) and [Explorer's choice](mqtt_explorer.md).

**Default/resolution:** no default is declared in this profile; omission leaves it absent. The resolver copies direct profile property keys then replaces them with explicit site property keys. This field is scalar, so no recursive merge applies. The MQTT property object rejects unknown fields: `password_file` is its only accepted key at this snapshot. `port: 1884` is not an available override and fails `component.fields`.

**Conditional syntax fragment**, to be placed in an otherwise valid broker instance whose separately declared managed-account composition requires it:

```yaml
properties:
  password_file: /mosquitto/config/passwords
```

This fragment passes the property's value rule; it does not by itself select or prove the account operation. That operation uses the supported procedure that mounts the password file’s parent directory, updates the file and reloads the broker with HUP, while checking that existing ownership and private inputs remain unchanged. HUP tells the broker to reload its configuration. Other broker updates may still require a restart. See [lifecycle](#later-deployments) and [invalid property diagnostics](#invalid-cases).


## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| `password_file` | Conditional string | See [Password file](#mqtt-password-file) for the exact basename rule, the behavior of omitted, null and empty values, and the managed-account condition. This property does not create configuration or access-control lists (ACLs). |

## Invalid cases

Start from the complete valid messaging composition and change only the input shown. These source-only tests exercise the selected resolver and adapter, without reading a credential file or contacting a broker.

| Invalid input | Actual refusal and layer | Correction |
| --- | --- | --- |
| Omit `apps.broker.secrets.probe`, or point it to a valid environment source | `component.secret-required at apps.broker.properties` in the MQTT adapter resolution floor. The diagnostic context is the adapter's properties scope, not the literal secret-source field. | Bind the existing file source described in [Probe binding](#mqtt-probe). |
| Set `properties.password_file: /elsewhere/passwords` | `component.property at apps.broker.properties` in MQTT property validation | Use the supported container config basename from [Password file](#mqtt-password-file). |
| Add `properties.port: 1884` | `component.fields at apps.broker.properties` in the closed property validator | MQTT has no port override; use supported placement with distinct guest sockets. |

After repair, resolve the same complete source and generate its deployment files. These checks confirm that invalid inputs are rejected and valid source passes. They do not check credential contents, authentication or listener isolation on a running target. [Troubleshooting](../../troubleshooting.md#mqtt-probe-refusal) links back to these inputs.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`mqtt-images`](../software-and-runtime.md#registration-software-mqtt-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`mqtt`](../software-and-runtime.md#registration-runtime-profiles-mqtt).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `mqtt` | `mqtt` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `mqtt` | 256 | 1 | 128 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

| Change or condition | Supported effect and boundary |
| --- | --- |
| Update the same HomeLab-managed app through normal CD | HomeLab brings the broker and runtime settings into line with the declared configuration and image selection. A container configuration or image change may recreate or restart the broker; uninterrupted clients are not promised. |
| Explicit supported managed MQTT-account operation | HomeLab mounts the password file’s parent directory, checks existing credentials and ownership, updates the file, and sends HUP to reload the broker. This capability does not generate arbitrary ACLs or broker configuration. |
| Existing data, configuration and log directories | HomeLab verifies their existing locations and owners without moving them or changing Unix ownership. A different source path does not authorize importing data. |
| Change to the probe credentials or their source name | HomeLab still requires unchanged existing private inputs and current records proving ownership. Changing a name or path does not authorize credential rotation. |
| Foreign broker, missing ownership or unresolved HOLD | Normal deployment rejects the operation. Preserve the ownership records and HOLD, inspect the reported diagnostic, and follow the supported lifecycle procedure; do not clear records to force another attempt. |
| Version migration, restore, arbitrary replacement or hardware behavior | This source suite has not verified these operations. Neither a vendor image nor successful compilation proves that the service works after them. |


HomeLab updates the broker’s container, configuration and probe reference while preserving its existing data, credentials and ownership records. The supported password-file update and HUP reload procedure applies only when the separate managed-account capability is explicitly selected.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#mqtt) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [mqtt.yaml](../../../apps/mqtt.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

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
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-config"></a>`backup.include.config` | `object` |
| <a id="declaration-backup-include-config-category"></a>`backup.include.config.category` | `"configuration"` |
| <a id="declaration-backup-include-config-capture"></a>`backup.include.config.capture` | `"files"` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"state"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-log"></a>`backup.exclude.log` | `"transient"` |
