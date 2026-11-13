[Documentation](../../README.md) / [Reference](../README.md)

# MQTT Explorer

Run MQTT Explorer behind its own gateway, configured from files, with a saved broker connection. It requires an existing authentication outpost, the service that checks whether requests are signed in.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: mqtt_explorer` |
| Adapter | `mqtt_explorer` |
| Owned containers | `mqtt_explorer`, `explorer_gateway` |
| Multiple instances | Helper tests cover independent instances with separate service names, Compose projects, data paths, runtime directories and protected credential directories. Each instance also needs a distinct published address and port. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [mqtt_explorer.yaml](../../../apps/mqtt_explorer.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The broker connection must select TCP port 1883, a saved hostname and either an explicit same-guest managed mqtt-client account or an explicit existing credential. Managed access is read-write-all (all topics). The required HTTP outpost target is the existing Authentik service on port 9000; it is not a newly created identity provider. Only the gateway is published. Saved profile passwords are plaintext at rest; startup log suppression keeps them out of console output. The derived backend alias applies only to Explorer, not managed DNS or the broker.

## First installation

This profile can create its owned data directory beneath a declared provider volume and prepare the saved profile. You must supply an existing broker credential, or select the supported managed-account capability on the same guest. A configured outpost and canonical HTTPS route are also required. It does not provision the identity provider.

For a complete example using the creation policy, see [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml), app `browser`. The example must resolve and generate deployment files successfully. These checks do not prove that the service has been deployed.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/messaging-radio.yaml).

```yaml
apps:
  browser:
    profile: mqtt_explorer
    guest: browser
    lifecycle: fresh
```

### Practical complete example

Use app `browser` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

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
| `private_interface` | Yes | `app-network` |
| `broker_interface` | Yes | `guest-interface` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web_listener` | `explorer_gateway` / `app-network` | `wildcard` via `private_interface` | `4180/tcp` | `guest-interface` 80 via `web` |
| `explorer_listener` | `mqtt_explorer` / `app-network` | `wildcard` via `private_interface` | `3000/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |

A wildcard listener accepts connections within the declared app network. A port becomes available on the guest only when explicitly published. Endpoints do not permit network traffic or make another app wait for this service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/app/data` | directory / writable | Create-only 1001:1001 mode 0700 |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | Yes | `start` | `mqtt-client` |
| `outpost` | `http` | Yes | None | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret. Saved GUI credentials, where used, are plaintext at rest in their protected workspace.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| connection_name | Required string | Nonempty single line, at most 100 characters. The broker hostname comes from the selected connection; the canonical HTTPS origin is explicit. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit both the existing broker credential and managed-account selection, or omit the saved hostname or outpost | Validation rejects the missing prerequisite: choose one supported credential source and supply the saved hostname and existing authentication outpost. |
| Bind an existing unmanaged data directory or protected credential directory as fresh | HomeLab rejects the directory because its ownership does not match this app; fresh cannot adopt it. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`mqtt_explorer-images`](../software-and-runtime.md#registration-software-mqtt-explorer-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`mqtt_explorer`](../software-and-runtime.md#registration-runtime-profiles-mqtt-explorer).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `mqtt_explorer` | `mqtt_explorer` | Immutable registry digest |
| `explorer_gateway` | `traefik` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `mqtt_explorer` | 256 | 1 | 128 |
| `explorer_gateway` | 128 | 1 | 128 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Gateway and saved-profile behavior

Every app and Socket.IO request passes through the named existing outpost; callback routing goes to that outpost separately. The gateway uses only file configuration and has no ACME, dashboard, API, Docker socket or infrastructure provider. No identity-provider registration is performed.

The version 1 saved profile preserves unrelated settings and profiles. It does not choose a fixed client ID, autoconnect, a public demo broker or an AI key. When creating a managed account, HomeLab verifies the password file through its mounted parent directory, adds the account atomically, then sends HUP to reload the broker. Ordinary GUI changes affect only this app’s services. Health checks cover the app, gateway and backend alias; after deployment, separately verify sign-in, reading and publishing messages, and continued access for existing clients.

## Later deployments

HomeLab maintains the same data, saved profile and ownership of the protected credential files. Preserve the selected broker credential, saved hostname and configured outpost; a source revision cannot silently rotate the saved password or adopt another profile.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#mqtt_explorer) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [mqtt_explorer.yaml](../../../apps/mqtt_explorer.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"mqtt_explorer"` |
| <a id="declaration-display-name"></a>`display_name` | `"MQTT Explorer"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private-interface"></a>`interfaces.private_interface` | `object` |
| <a id="declaration-interfaces-private-interface-required"></a>`interfaces.private_interface.required` | `true` |
| <a id="declaration-interfaces-private-interface-accepts"></a>`interfaces.private_interface.accepts` | `["app-network"]` |
| <a id="declaration-interfaces-broker-interface"></a>`interfaces.broker_interface` | `object` |
| <a id="declaration-interfaces-broker-interface-required"></a>`interfaces.broker_interface.required` | `true` |
| <a id="declaration-interfaces-broker-interface-accepts"></a>`interfaces.broker_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"explorer_gateway"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `4180` |
| <a id="declaration-listeners-web-listener-publish"></a>`listeners.web_listener.publish` | `object` |
| <a id="declaration-listeners-web-listener-publish-scope"></a>`listeners.web_listener.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-listener-publish-interface"></a>`listeners.web_listener.publish.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-publish-port"></a>`listeners.web_listener.publish.port` | `80` |
| <a id="declaration-listeners-explorer-listener"></a>`listeners.explorer_listener` | `object` |
| <a id="declaration-listeners-explorer-listener-service"></a>`listeners.explorer_listener.service` | `"mqtt_explorer"` |
| <a id="declaration-listeners-explorer-listener-namespace"></a>`listeners.explorer_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-explorer-listener-interface"></a>`listeners.explorer_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-explorer-listener-bind"></a>`listeners.explorer_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-explorer-listener-protocol"></a>`listeners.explorer_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-explorer-listener-port"></a>`listeners.explorer_listener.port` | `3000` |
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
| <a id="declaration-storage-data-initialize"></a>`storage.data.initialize` | `object` |
| <a id="declaration-storage-data-initialize-type"></a>`storage.data.initialize.type` | `"directory"` |
| <a id="declaration-storage-data-initialize-uid"></a>`storage.data.initialize.uid` | `1001` |
| <a id="declaration-storage-data-initialize-gid"></a>`storage.data.initialize.gid` | `1001` |
| <a id="declaration-storage-data-initialize-mode"></a>`storage.data.initialize.mode` | `"0700"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-broker"></a>`connections.broker` | `object` |
| <a id="declaration-connections-broker-type"></a>`connections.broker.type` | `"mqtt"` |
| <a id="declaration-connections-broker-required"></a>`connections.broker.required` | `true` |
| <a id="declaration-connections-broker-readiness"></a>`connections.broker.readiness` | `["start"]` |
| <a id="declaration-connections-broker-accounts"></a>`connections.broker.accounts` | `["mqtt-client"]` |
| <a id="declaration-connections-outpost"></a>`connections.outpost` | `object` |
| <a id="declaration-connections-outpost-type"></a>`connections.outpost.type` | `"http"` |
| <a id="declaration-connections-outpost-required"></a>`connections.outpost.required` | `true` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "mqtt_explorer-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "mqtt_explorer"]` |
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
