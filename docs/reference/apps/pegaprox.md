[Documentation](../../README.md) / [Reference](../README.md)

# PegaProx

Run PegaProx with the explicitly selected database key and owned data, configuration and log directories.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: pegaprox` |
| Adapter | `pegaprox` |
| Owned containers | `pegaprox` |
| Multiple instances | Each instance needs a distinct published address and port, runtime files, database-key file and writable directories. This does not establish that every layout with multiple instances works. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [pegaprox.yaml](../../../apps/pegaprox.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The selected runtime requires at least 512 MiB OS reserve. The effective guest reserve is max(guest reserve, selected runtime requirement); it is placement policy, not measured load. The management endpoint accepts only private or benchmark address ranges.

## Management and web access

Bind the optional `management_interface` role to describe the intended Proxmox API source separately from the web listener. The site connection selects `source_interface: management_interface` for traffic validation; this does not bind PegaProx’s outbound API socket to that NIC. Reaching Proxmox through a non-default NIC also requires working routing and, for a container-network app, the appropriate host forwarding policy. Verify the actual outbound source after deployment. The API endpoint and credentials remain independently declared. Omitting the role preserves the original single-interface profile behaviour.

## First installation

You need prepared data, configuration and log directories, the existing database key, and a completed administrator setup. The profile does not create a new application administrator or adopt an unrelated manager. The practical example maintains an already HomeLab-managed instance.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/edge-management.yaml).

```yaml
apps:
  manager:
    profile: pegaprox
    guest: manager
    lifecycle: retained
```

### Practical complete example

Use app `manager` in [examples/catalogue/edge-management.yaml](../../../examples/catalogue/edge-management.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/edge-management.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web_interface` | Yes | `guest-interface` |
| `management_interface` | No | `guest-interface` |
| `private_interface` | Yes | `app-network` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web_listener` | `pegaprox` / `app-network` | `wildcard` via `private_interface` | `5000/tcp` | `guest-interface` 5000 via `web_interface` |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |

A wildcard listener accepts connections within the declared app network. A port becomes available on the guest only when explicitly published. Endpoints do not permit network traffic or make another app wait for this service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/app/config` | directory / writable | None |
| `logs` | Yes | `/app/logs` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Required | Type | Meaning |
| --- | --- | --- | --- |
| `proxmox` | No | `https` | Selected hypervisor API; bind its endpoint and source interface explicitly. |

The complete example connects `manager_provider` to the existing external Proxmox endpoint through the app’s `web_interface` role. The guest’s network policy permits the API port, so source validation can check the required traffic. This connection does not configure an existing PegaProx cluster or make deployment wait for it. A site with no configured cluster can omit the role. Selecting an API connection does not require opening SSH, console or other ports.

| App secret role | Requirement |
| --- | --- |
| `database_key` | Required |

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| trusted_proxy | Required mapping | {app,interface} selecting a physical interface of the named Traefik app. It must be a distinct private address, not a hostname or arbitrary trust range. |

## Invalid cases

Start from the complete [examples/catalogue/edge-management.yaml](../../../examples/catalogue/edge-management.yaml), app `manager`, using the [source-only setup](../../guides/first-configuration.md). Change only the input described; retain the rest of that composition. Diagnostics below are emitted results, not inferred field paths. Where no `at` context appears, no field path was emitted.

| Invalid variation | Actual refusal and enforcing layer | Cause and supported correction |
| --- | --- | --- |
| <a id="invalid-literal-proxy-address"></a>Replace `properties.trusted_proxy` with a literal IPv4 string. | `component.fields at apps.manager.properties` — Closed app-property validation. | The field requires `{app: edge, interface: management_interface}` in this example, not an address literal. Restore the actual Traefik physical-role reference and its distinct private address. |
| <a id="invalid-omit-database-key"></a>Remove `secrets.database_key`. | `component.secret-required at apps.manager.secrets` — Secret binding during resolution. | PegaProx needs its existing key file. Restore the declared file source; do not create a new key or change the retained database identity. |

After repair, resolve the same complete source and generate every guest’s deployment packet; expect both to pass as the unchanged baseline does. Source checks neither inspect credential contents nor establish installation, routing, socket isolation or service recovery on a target.

The existing [complete-profile integrations](../../../tests/test_profile_examples.py) and [composition cases](../../../tests/test_component_composition.py) exercise the real selected framework. Its validators, binding checks and packet/file builders enforce these boundaries; the [testing guide](../../testing.md#documentation-conformance) explains the evidence limits.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`pegaprox-images`](../software-and-runtime.md#registration-software-pegaprox-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`pegaprox`](../software-and-runtime.md#registration-runtime-profiles-pegaprox).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `pegaprox` | `pegaprox` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `pegaprox` | 1536 | 2 | 256 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the configured manager using the same data, config, logs and database key. Existing administrator accounts and setup state stay protected; changing a trusted-proxy binding does not initialize a new manager.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#pegaprox) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [pegaprox.yaml](../../../apps/pegaprox.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"pegaprox"` |
| <a id="declaration-display-name"></a>`display_name` | `"PegaProx"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private-interface"></a>`interfaces.private_interface` | `object` |
| <a id="declaration-interfaces-private-interface-required"></a>`interfaces.private_interface.required` | `true` |
| <a id="declaration-interfaces-private-interface-accepts"></a>`interfaces.private_interface.accepts` | `["app-network"]` |
| <a id="declaration-interfaces-management-interface"></a>`interfaces.management_interface` | `object` |
| <a id="declaration-interfaces-management-interface-required"></a>`interfaces.management_interface.required` | `false` |
| <a id="declaration-interfaces-management-interface-accepts"></a>`interfaces.management_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"pegaprox"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `5000` |
| <a id="declaration-listeners-web-listener-publish"></a>`listeners.web_listener.publish` | `object` |
| <a id="declaration-listeners-web-listener-publish-scope"></a>`listeners.web_listener.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-listener-publish-interface"></a>`listeners.web_listener.publish.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-publish-port"></a>`listeners.web_listener.publish.port` | `5000` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/app/config"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `true` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-logs"></a>`storage.logs` | `object` |
| <a id="declaration-storage-logs-target"></a>`storage.logs.target` | `"/app/logs"` |
| <a id="declaration-storage-logs-read-only"></a>`storage.logs.read_only` | `false` |
| <a id="declaration-storage-logs-required"></a>`storage.logs.required` | `true` |
| <a id="declaration-storage-logs-kind"></a>`storage.logs.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-proxmox"></a>`connections.proxmox` | `object` |
| <a id="declaration-connections-proxmox-type"></a>`connections.proxmox.type` | `"https"` |
| <a id="declaration-connections-proxmox-required"></a>`connections.proxmox.required` | `false` |
| <a id="declaration-software"></a>`software` | `["docker", "pegaprox-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "pegaprox"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-database-key"></a>`secrets.database_key` | `object` |
| <a id="declaration-secrets-database-key-required"></a>`secrets.database_key.required` | `true` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-config"></a>`backup.include.config` | `object` |
| <a id="declaration-backup-include-config-category"></a>`backup.include.config.category` | `"state"` |
| <a id="declaration-backup-include-config-capture"></a>`backup.include.config.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-logs"></a>`backup.exclude.logs` | `"transient"` |
