[Documentation](../../README.md) / [Reference](../README.md)

# Home Assistant — `homeassistant-public`

Start an independent Home Assistant using the declared official public image and create-only configuration directory.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: homeassistant-public` |
| Adapter | `homeassistant` |
| Owned containers | `homeassistant` |
| Multiple instances | Fixed host TCP 8123; put another instance on another guest. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [homeassistant-public.yaml](../../../apps/homeassistant-public.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The config initializer is create-only beneath a proven provider volume with a nonempty app subpath. It does not chown an existing tree or adopt an unowned directory. Optional integrations do not make Node-RED, databases, MQTT, identity or ingress mandatory.

## First installation

Can create a new configuration directory beneath the declared provider volume and start the public image. Home Assistant onboarding and household integrations are separate user setup, not supplied configuration.

Complete creation-policy source: [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml), app `homeassistant`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/new-automation.yaml).

```yaml
apps:
  homeassistant:
    profile: homeassistant-public
    guest: homeassistant-public
    lifecycle: fresh
```

### Practical complete example

Use app `homeassistant` in [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/new-automation.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

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

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/config` | directory / writable | Create-only 0:0 mode 0700 |
| `media` | Conditional / optional | `/media` | directory / writable | None |
| `community` | Conditional / optional | `/hacsfiles` | directory / writable | None |
| `startup` | Conditional / optional | `/startup` | directory / read-only | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `recorder` | `mariadb` | No | `start` | None |
| `metrics` | `influxdb` | No | `start` | None |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| mdns | Optional mapping | interface and startup are declared role IDs. Retained only; select homeassistant-mdns runtime, a physical Home role and read-only /startup binding. No NET_ADMIN in the base runtime. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use a pre-existing foreign configuration directory as fresh initialization | Refuses instead of adopting/chowning it. |
| Add the retained mDNS/NET_ADMIN startup capability without its declared support | Refuses the capability/security contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`homeassistant-public-images`](../software-and-runtime.md#registration-software-homeassistant-public-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`homeassistant`](../software-and-runtime.md#registration-runtime-profiles-homeassistant).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `homeassistant` | `homeassistant_public` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `homeassistant` | 2048 | 2 | 512 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates the same instance with its existing configuration directory. The initializer does not run again against existing data; household/onboarding choices remain in that owned configuration. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [homeassistant-public.yaml](../../../apps/homeassistant-public.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

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
| <a id="declaration-storage-config-initialize"></a>`storage.config.initialize` | `object` |
| <a id="declaration-storage-config-initialize-type"></a>`storage.config.initialize.type` | `"directory"` |
| <a id="declaration-storage-config-initialize-uid"></a>`storage.config.initialize.uid` | `0` |
| <a id="declaration-storage-config-initialize-gid"></a>`storage.config.initialize.gid` | `0` |
| <a id="declaration-storage-config-initialize-mode"></a>`storage.config.initialize.mode` | `"0700"` |
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
| <a id="declaration-software"></a>`software` | `["docker", "curl", "homeassistant-public-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "homeassistant"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
