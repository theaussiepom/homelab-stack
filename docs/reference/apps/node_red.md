[Documentation](../../README.md) / [Reference](../README.md)

# Node-RED — `node_red`

Start Node-RED with the declared official public image and its standard data directory, independently of Home Assistant.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: node_red` |
| Adapter | `node_red` |
| Owned containers | `node_red` |
| Multiple instances | Fixed host TCP 1880; use separate guests. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [node_red.yaml](../../../apps/node_red.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

For prepared custom software, choose [`node_red-custom`](node_red-custom.md). See [consumer migration](../../guides/images-and-updates.md#migrate-an-existing-consumer) before changing an existing selection.

## Application requirements

This public-image variant does not install the existing profile’s OpenID Connect (OIDC) sign-in setup or its settings and health-check scripts. Choose access controls and authentication before making the service reachable. Do not use this variant to silently remove authentication from an existing instance.

## First installation

This profile can create a new data directory beneath the declared provider volume and start the public image. This variant does not install the existing profile’s OpenID Connect sign-in setup or import existing flows and credentials.

For a complete example using the creation policy, see [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml), app `node_red`. The example must resolve and generate deployment files successfully. These checks do not prove that the service has been deployed.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/new-automation.yaml).

```yaml
apps:
  node_red:
    profile: node_red
    guest: node_red-public
    lifecycle: fresh
```

### Practical complete example

Use app `node_red` in [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/new-automation.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web_interface` | Yes | `guest-interface` |
| `broker_interface` | No; selected capability can require it | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web_listener` | `node_red` / `host` | `wildcard` via `web_interface` | `1880/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |

A wildcard host listener can accept connections through interfaces other than the advertised NIC. An endpoint gives consumers an address and port. It does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/data` | directory / writable | Create-only 1000:1000 mode 0700 |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/app-properties.md).

This adapter accepts no application property keys. It rejects unknown keys and provides no way to pass arbitrary commands, environment variables or mounts.

## Invalid cases

Start from the complete [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml), app `node_red`, using the [source-only setup](../../guides/first-configuration.md). Change only the input described; retain the rest of that composition. Diagnostics below are emitted results, not inferred field paths. Where no `at` context appears, no field path was emitted.

| Invalid variation | Actual refusal and enforcing layer | Cause and supported correction |
| --- | --- | --- |
| <a id="invalid-omit-data-binding"></a>Remove the app’s `storage.data` binding. | `component.invalid` — Profile storage binding during app resolution. | The data role is required. Restore its owned volume/root-path binding; neither `fresh` nor an image selection adopts an unrelated directory. |
| <a id="invalid-raw-settings-property"></a>Add `properties.settings: unrestricted settings text`. | `component.fields at apps.node_red.properties` — Closed app-property validation. | Node-RED accepts no application property keys. Remove it. Custom variants select existing settings/healthcheck files through their storage roles; the public variant does not gain those capabilities from raw text. |

After repair, resolve the same complete source and generate every guest’s deployment packet; expect both to pass as the unchanged baseline does. Source checks neither inspect credential contents nor establish installation, routing, socket isolation or service recovery on a target.

The existing [complete-profile integrations](../../../tests/test_profile_examples.py) and [composition cases](../../../tests/test_component_composition.py) exercise the real selected framework. Its validators, binding checks and packet/file builders enforce these boundaries; the [testing guide](../../testing.md#documentation-conformance) explains the evidence limits.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`node_red-upstream-images`](../software-and-runtime.md#registration-software-node-red-upstream-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`node_red`](../software-and-runtime.md#registration-runtime-profiles-node-red).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `node_red` | `node_red_upstream` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `node_red` | 1024 | 1 | 256 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab updates the same instance with its existing data and flows. It does not substitute the retained OIDC profile or import another installation’s credentials.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/f8a629ed78732f5fb72f3da6c7da0e88b7844606/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#node_red) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [node_red.yaml](../../../apps/node_red.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"node_red"` |
| <a id="declaration-display-name"></a>`display_name` | `"Node-RED"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-broker-interface"></a>`interfaces.broker_interface` | `object` |
| <a id="declaration-interfaces-broker-interface-required"></a>`interfaces.broker_interface.required` | `false` |
| <a id="declaration-interfaces-broker-interface-accepts"></a>`interfaces.broker_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"node_red"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"host"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `1880` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/data"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-storage-data-initialize"></a>`storage.data.initialize` | `object` |
| <a id="declaration-storage-data-initialize-type"></a>`storage.data.initialize.type` | `"directory"` |
| <a id="declaration-storage-data-initialize-uid"></a>`storage.data.initialize.uid` | `1000` |
| <a id="declaration-storage-data-initialize-gid"></a>`storage.data.initialize.gid` | `1000` |
| <a id="declaration-storage-data-initialize-mode"></a>`storage.data.initialize.mode` | `"0700"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-broker"></a>`connections.broker` | `object` |
| <a id="declaration-connections-broker-type"></a>`connections.broker.type` | `"mqtt"` |
| <a id="declaration-connections-broker-required"></a>`connections.broker.required` | `false` |
| <a id="declaration-connections-broker-readiness"></a>`connections.broker.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "node_red-upstream-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "node_red"]` |
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
