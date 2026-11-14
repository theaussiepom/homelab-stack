[Documentation](../../README.md) / [Reference](../README.md)

# Home Assistant: two declared web listeners

Run Home Assistant with an explicitly supplied custom image archive and existing configuration. Recorder, metrics and MQTT are independent optional integrations.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: homeassistant-dual-web` |
| Adapter | `homeassistant` |
| Owned containers | `homeassistant` |
| Multiple instances | Fixed host TCP 8123 prevents two identical listeners on one guest. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [homeassistant-dual-web.yaml](../../../apps/homeassistant-dual-web.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The site must supply `local_id`, `archive` and `archive_sha256` for the custom image. Zero values in the public catalogue are placeholders, not usable image identities. Select the retained multicast DNS (mDNS) startup capability explicitly when required; it does not imply hardware access.

Use this retained-only variant while two explicitly selected web addresses must remain available. Return to [homeassistant-bound](homeassistant-bound.md) only in a separately reviewed later change after removing the transition address from the actual HTTP settings.

## Bound web behaviour

Prepare retained HTTP settings outside ordinary CD through the supported configuration path. Bind HTTP to both assigned web IPv4 addresses and `127.0.0.1`; `::1` is optional. The health check requires both declared non-loopback sockets and IPv4 loopback and refuses wildcards, extra addresses or a missing listener. Its existing loopback HTTP/API challenge probe is unchanged. This profile does not rewrite Home Assistant configuration, environment, data or authentication.

Bind `web_interface` to the primary web NIC and `transition_web_interface` to the address retained during conversion. Both listeners use host TCP 8123. Their `web_endpoint` and `transition_web_endpoint` export distinct addresses; publish the primary endpoint unless the site explicitly selects otherwise. Neither declaration creates a NIC, firewall permission or route. Preserve discovery, database, broker, media, custom image and credential identities. Socket checks and policy declarations are separate from live firewall and service acceptance.

## First installation

This selection requires the declared custom archive and prepared Home Assistant configuration. It does not build that archive or provide a brand-new custom installation. For the supported public-image creation path, choose [homeassistant](homeassistant.md).

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/existing-automation-dual-web.yaml).

```yaml
apps:
  homeassistant:
    profile: homeassistant-dual-web
    guest: homeassistant
    lifecycle: retained
```

### Practical complete example

Use app `homeassistant` in [examples/catalogue/existing-automation-dual-web.yaml](../../../examples/catalogue/existing-automation-dual-web.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/existing-automation-dual-web.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web_interface` | Yes | `guest-interface` |
| `transition_web_interface` | Yes | `guest-interface` |
| `home_interface` | No; selected capability can require it | `guest-interface` |
| `database_interface` | No; selected capability can require it | `guest-interface` |
| `metrics_interface` | No; selected capability can require it | `guest-interface` |
| `broker_interface` | No; selected capability can require it | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web_listener` | `homeassistant` / `host` | `interface` via `web_interface` | `8123/tcp` | None; listener remains in its declared namespace |
| `transition_web_listener` | `homeassistant` / `host` | `interface` via `transition_web_interface` | `8123/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |
| `transition_web_endpoint` | `http` | `transition_web_listener` via `transition_web_interface` |

This variant declares exactly two selected interface-bound sockets; actual checks require both and IPv4 loopback, and reject other binds. An endpoint gives consumers an address and port. It does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/0899d84fb1861034a4463788286180a80d7970e8/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

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

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/0899d84fb1861034a4463788286180a80d7970e8/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| mdns | Optional mapping | `interface` and `startup` name declared roles. The interface role must bind to a physical guest interface, and the storage role must be read-only at `/startup`. This capability requires `lifecycle: retained` and the explicitly selected `homeassistant-mdns` runtime. The base runtime does not grant `NET_ADMIN`. |

## Invalid cases

Start from the complete [examples/catalogue/existing-automation-dual-web.yaml](../../../examples/catalogue/existing-automation-dual-web.yaml), app `homeassistant`, using the [source-only setup](../../guides/first-configuration.md). Change only the input described; retain the rest of that composition. Diagnostics below are emitted results, not inferred field paths. Where no `at` context appears, no field path was emitted.

Use the two canonical cases: [omit web interface](homeassistant.md#invalid-omit-web-interface) and [mdns missing startup field](homeassistant.md#invalid-mdns-missing-startup-field). The additional transition role and two-socket checks do not relax the required primary web role or mDNS property grammar. Keep the transition binding and retained settings intact.

After repair, resolve the same complete source and generate every guest’s deployment packet; expect both to pass as the unchanged baseline does. Source checks neither inspect credential contents nor establish installation, routing, socket isolation or service recovery on a target.

The existing [complete-profile integrations](../../../tests/test_profile_examples.py) and [composition cases](../../../tests/test_component_composition.py) exercise the real selected framework. Its validators, binding checks and packet/file builders enforce these boundaries; the [testing guide](../../testing.md#documentation-conformance) explains the evidence limits.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`homeassistant-custom-images`](../software-and-runtime.md#registration-software-homeassistant-custom-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`homeassistant`](../software-and-runtime.md#registration-runtime-profiles-homeassistant).

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

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/0899d84fb1861034a4463788286180a80d7970e8/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/0899d84fb1861034a4463788286180a80d7970e8/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/0899d84fb1861034a4463788286180a80d7970e8/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/0899d84fb1861034a4463788286180a80d7970e8/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/0899d84fb1861034a4463788286180a80d7970e8/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#homeassistant-dual-web) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

Complete values from [homeassistant-dual-web.yaml](../../../apps/homeassistant-dual-web.yaml). [Reading declaration records](../declaration-records.md) explains binding and ownership.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"homeassistant"` |
| <a id="declaration-display-name"></a>`display_name` | `"Home Assistant with two declared web listeners"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-home-interface"></a>`interfaces.home_interface` | `object` |
| <a id="declaration-interfaces-home-interface-required"></a>`interfaces.home_interface.required` | `false` |
| <a id="declaration-interfaces-home-interface-accepts"></a>`interfaces.home_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-database-interface"></a>`interfaces.database_interface` | `object` |
| <a id="declaration-interfaces-database-interface-required"></a>`interfaces.database_interface.required` | `false` |
| <a id="declaration-interfaces-database-interface-accepts"></a>`interfaces.database_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-metrics-interface"></a>`interfaces.metrics_interface` | `object` |
| <a id="declaration-interfaces-metrics-interface-required"></a>`interfaces.metrics_interface.required` | `false` |
| <a id="declaration-interfaces-metrics-interface-accepts"></a>`interfaces.metrics_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-broker-interface"></a>`interfaces.broker_interface` | `object` |
| <a id="declaration-interfaces-broker-interface-required"></a>`interfaces.broker_interface.required` | `false` |
| <a id="declaration-interfaces-broker-interface-accepts"></a>`interfaces.broker_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-transition-web-interface"></a>`interfaces.transition_web_interface` | `object` |
| <a id="declaration-interfaces-transition-web-interface-required"></a>`interfaces.transition_web_interface.required` | `true` |
| <a id="declaration-interfaces-transition-web-interface-accepts"></a>`interfaces.transition_web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"homeassistant"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"host"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"interface"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `8123` |
| <a id="declaration-listeners-transition-web-listener"></a>`listeners.transition_web_listener` | `object` |
| <a id="declaration-listeners-transition-web-listener-service"></a>`listeners.transition_web_listener.service` | `"homeassistant"` |
| <a id="declaration-listeners-transition-web-listener-namespace"></a>`listeners.transition_web_listener.namespace` | `"host"` |
| <a id="declaration-listeners-transition-web-listener-interface"></a>`listeners.transition_web_listener.interface` | `"transition_web_interface"` |
| <a id="declaration-listeners-transition-web-listener-bind"></a>`listeners.transition_web_listener.bind` | `"interface"` |
| <a id="declaration-listeners-transition-web-listener-protocol"></a>`listeners.transition_web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-transition-web-listener-port"></a>`listeners.transition_web_listener.port` | `8123` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-endpoints-transition-web-endpoint"></a>`endpoints.transition_web_endpoint` | `object` |
| <a id="declaration-endpoints-transition-web-endpoint-listener"></a>`endpoints.transition_web_endpoint.listener` | `"transition_web_listener"` |
| <a id="declaration-endpoints-transition-web-endpoint-protocol"></a>`endpoints.transition_web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-transition-web-endpoint-via"></a>`endpoints.transition_web_endpoint.via` | `"transition_web_interface"` |
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
| <a id="declaration-software"></a>`software` | `["docker", "curl", "homeassistant-custom-images"]` |
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
