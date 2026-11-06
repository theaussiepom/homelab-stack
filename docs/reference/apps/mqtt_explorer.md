[Documentation](../../README.md) / [Reference](../README.md)

# MQTT Explorer

Provide MQTT Explorer behind its owned file-only gateway, with a saved broker connection and a required existing authentication outpost.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: mqtt_explorer` |
| Adapter | `mqtt_explorer` |
| Owned containers | `mqtt_explorer`, `explorer_gateway` |
| Multiple instances | Namespace-aware helper tests cover independent instances with distinct services, project, data, runtime and custody paths/publications. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [mqtt_explorer.yaml](../../../apps/mqtt_explorer.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The broker connection must select TCP port 1883, a saved hostname and either an explicit same-guest managed mqtt-client account or an explicit existing credential. Managed access is read-write-all (all topics). The required HTTP outpost target is the existing Authentik service on port 9000; it is not a newly created identity provider. Only the gateway is published. Saved profile passwords are plaintext at rest; startup log suppression keeps them out of console output. The derived backend alias applies only to Explorer, not managed DNS or the broker.

## First installation

Can create its owned data directory beneath a declared provider volume and prepare the saved profile. Requires an existing broker credential (or the separate supported same-guest managed-account capability), configured outpost and canonical HTTPS route. It does not provision the identity provider.

Complete creation-policy source: [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml), app `browser`. It must pass both resolution and packet generation; it is not proof of a deployed service.

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

Use app `browser` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |
| `broker` | Yes | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `explorer_gateway` / `app-network` | `wildcard` via `private` | `4180/tcp` | `guest-interface` 80 via `web` |
| `explorer` | `mqtt_explorer` / `app-network` | `wildcard` via `private` | `3000/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/app/data` | directory / writable | Create-only 1001:1001 mode 0700 |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | Yes | `start` | `mqtt-client` |
| `outpost` | `http` | Yes | None | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update. Saved GUI credentials, where used, are plaintext at rest in their protected workspace.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| connection_name | Required string | Nonempty single line, at most 100 characters. The broker hostname comes from the selected connection; the canonical HTTPS origin is explicit. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit broker credential/account, saved hostname or outpost | Refuses the selected broker/authentication binding. |
| Bind an unowned existing data/custody directory as fresh | Refuses adoption or mismatched ownership. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

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

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Gateway and saved-profile behavior

Every app and Socket.IO request passes through the named existing outpost; callback routing goes to that outpost separately. The file-only gateway has no ACME, dashboard/API, Docker socket or infrastructure provider. No identity-provider registration is performed.

The version1 saved profile preserves unrelated settings and profiles. No fixed client ID, autoconnect, public demo broker or AI key is chosen. Managed account creation verifies the parent-mounted password file before atomic addition/HUP; ordinary GUI changes target only owned services. Health checks the app/gateway/backend alias, while actual sign-in, read/publish and existing-client continuity are later service acceptance checks.

## Later deployments

Maintains the same data, saved profile and custody owner. Preserve the selected broker credential/hostname and configured outpost; a source revision cannot silently rotate the saved password or adopt another profile. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [mqtt_explorer.yaml](../../../apps/mqtt_explorer.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"mqtt_explorer"` |
| <a id="declaration-display-name"></a>`display_name` | `"MQTT Explorer"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-interfaces-broker"></a>`interfaces.broker` | `object` |
| <a id="declaration-interfaces-broker-required"></a>`interfaces.broker.required` | `true` |
| <a id="declaration-interfaces-broker-accepts"></a>`interfaces.broker.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"explorer_gateway"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"private"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `4180` |
| <a id="declaration-listeners-web-publish"></a>`listeners.web.publish` | `object` |
| <a id="declaration-listeners-web-publish-scope"></a>`listeners.web.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-publish-interface"></a>`listeners.web.publish.interface` | `"web"` |
| <a id="declaration-listeners-web-publish-port"></a>`listeners.web.publish.port` | `80` |
| <a id="declaration-listeners-explorer"></a>`listeners.explorer` | `object` |
| <a id="declaration-listeners-explorer-service"></a>`listeners.explorer.service` | `"mqtt_explorer"` |
| <a id="declaration-listeners-explorer-namespace"></a>`listeners.explorer.namespace` | `"app-network"` |
| <a id="declaration-listeners-explorer-interface"></a>`listeners.explorer.interface` | `"private"` |
| <a id="declaration-listeners-explorer-bind"></a>`listeners.explorer.bind` | `"wildcard"` |
| <a id="declaration-listeners-explorer-protocol"></a>`listeners.explorer.protocol` | `"tcp"` |
| <a id="declaration-listeners-explorer-port"></a>`listeners.explorer.port` | `3000` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
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
