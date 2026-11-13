[Documentation](../../README.md) / [Reference](../README.md)

# Music Assistant: separate web and player networks

Run an existing Music Assistant installation without resetting its provider and account settings or data.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: music_assistant-split` |
| Adapter | `music_assistant` |
| Owned containers | `music_assistant` |
| Multiple instances | The player and web listeners use fixed host sockets, so another identical instance needs a separate guest. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [music_assistant-split.yaml](../../../apps/music_assistant-split.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The profile marks `public` optional, but generating deployment files currently requires an explicit HTTPS connection and the app’s canonical origin (its public base URL). The route check uses both. The connection must use the physical `web` role as its source, so even an independently selected Music Assistant instance needs this ingress connection.

The web address comes from `web`; the player bind and published address come from `stream`. The existing helper checks settings through the selected data root before startup; it does not reset streaming providers. The declared latest image policy is intentional and remains distinct from digest-pinned profiles.

## Separate listener behaviour

Before changing an existing installation, separately back up its retained settings.
For a web-only move, adjust the web bind address and bind the `stream` role to the
existing player address, leaving the stream bind/publish settings unchanged.
If streaming also moves, separately set both stream `bind_ip` and `publish_ip`
to the selected `stream` role address and verify the affected players.
Ordinary CD refuses either stream address if it differs from that role; it does
not rewrite these settings. Preserve provider credentials, identity and library.
Selecting this profile does not update an HA Music Assistant integration URL or
a player device.

## First installation

This retained profile cannot create and configure a new Music Assistant installation. The example requires an already HomeLab-managed installation and its valid existing settings and data.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/music-split.yaml).

```yaml
apps:
  music:
    profile: music_assistant-split
    guest: media
    lifecycle: retained
```

### Practical complete example

Use app `music` in [examples/catalogue/music-split.yaml](../../../examples/catalogue/music-split.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/music-split.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `stream` | Yes | `guest-interface` |

Bind each role to a guest NIC with `{interface: NIC_ID}`. This profile accepts only `guest-interface`; loopback and app-network scopes are not supported. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `music_assistant` / `host` | `interface` via `web` | `8095/tcp` | None; listener remains in its declared namespace |
| `stream` | `music_assistant` / `host` | `interface` via `stream` | `8097/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |
| `stream` | `http` | `stream` via `stream` |

The web listener binds to `web` on TCP8095; player streaming binds to `stream` on TCP8097. Existing player discovery and audio networks stay separate from web access. Their endpoints advertise those addresses and ports. Advertising an endpoint does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/data` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `public` | `https` | No | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/docs/reference/app-properties.md).

This adapter accepts no application property keys. It rejects unknown keys and provides no way to pass arbitrary commands, environment variables or mounts.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit explicit public HTTPS connection or canonical origin | HomeLab cannot generate the health check without the explicit HTTPS connection and canonical URL. |
| Bind the HTTPS source to a different address than the web role | Refuses the source-address requirement. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`music_assistant-images`](../software-and-runtime.md#registration-software-music-assistant-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`music_assistant`](../software-and-runtime.md#registration-runtime-profiles-music-assistant).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `music_assistant` | `music_assistant` | Declared floating latest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `music_assistant` | 1536 | 2 | 512 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the existing settings and data and verifies the core listener, stream listener and selected HTTPS route. It does not commission providers, replace authentication or repair vendor state. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/c694b1d286faf60e29f5a9f5a0a218c9dcbbc4da/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#music_assistant-split) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

Complete values from [music_assistant-split.yaml](../../../apps/music_assistant-split.yaml). [Reading declaration records](../declaration-records.md) explains binding and ownership.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"music_assistant"` |
| <a id="declaration-display-name"></a>`display_name` | `"Music Assistant with separate web and player networks"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-stream"></a>`interfaces.stream` | `object` |
| <a id="declaration-interfaces-stream-required"></a>`interfaces.stream.required` | `true` |
| <a id="declaration-interfaces-stream-accepts"></a>`interfaces.stream.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"music_assistant"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"host"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"web"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"interface"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `8095` |
| <a id="declaration-listeners-stream"></a>`listeners.stream` | `object` |
| <a id="declaration-listeners-stream-service"></a>`listeners.stream.service` | `"music_assistant"` |
| <a id="declaration-listeners-stream-namespace"></a>`listeners.stream.namespace` | `"host"` |
| <a id="declaration-listeners-stream-interface"></a>`listeners.stream.interface` | `"stream"` |
| <a id="declaration-listeners-stream-bind"></a>`listeners.stream.bind` | `"interface"` |
| <a id="declaration-listeners-stream-protocol"></a>`listeners.stream.protocol` | `"tcp"` |
| <a id="declaration-listeners-stream-port"></a>`listeners.stream.port` | `8097` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-endpoints-stream"></a>`endpoints.stream` | `object` |
| <a id="declaration-endpoints-stream-listener"></a>`endpoints.stream.listener` | `"stream"` |
| <a id="declaration-endpoints-stream-protocol"></a>`endpoints.stream.protocol` | `"http"` |
| <a id="declaration-endpoints-stream-via"></a>`endpoints.stream.via` | `"stream"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/data"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-public"></a>`connections.public` | `object` |
| <a id="declaration-connections-public-type"></a>`connections.public.type` | `"https"` |
| <a id="declaration-connections-public-required"></a>`connections.public.required` | `false` |
| <a id="declaration-connections-public-readiness"></a>`connections.public.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "music_assistant-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "music_assistant"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-health-ready-source-interface"></a>`health.ready.source_interface` | `"web"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"state"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
