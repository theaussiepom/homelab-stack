[Documentation](../../README.md) / [Reference](../README.md)

# Unbound

Provide a recursive resolver with a private container listener and explicit guest-loopback TCP/UDP publications.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: unbound` |
| Adapter | `unbound` |
| Owned containers | `unbound` |
| Multiple instances | Repeated instances are compiler-tested on one guest with different publish_port values and independent service/network identities. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [unbound.yaml](../../../apps/unbound.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The `service` role accepts guest-loopback only. A physical NIC binding is rejected; it does not expose Unbound on the LAN. For a new installation, HomeLab sizes the configuration from the app’s declared memory and CPU budget, not the host’s memory.

## First installation

The profile can create a new installation without a pre-existing configuration mount. The maintained starter uses `lifecycle: fresh`; keep that value unchanged for later deployments of the same resolver.

For a complete example using the creation policy, see [site.example.yaml](../../../site.example.yaml), app `recursive_dns`. The example must resolve and generate deployment files successfully. These checks do not prove that the service has been deployed.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../site.example.yaml).

```yaml
apps:
  recursive_dns:
    profile: unbound
    guest: resolver
    lifecycle: fresh
```

### Practical complete example

Use app `recursive_dns` in [site.example.yaml](../../../site.example.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/site.example.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-loopback` |
| `private` | Yes | `app-network` |

Bind `service` to `{scope: guest-loopback}` and `private` to `{scope: app-network, network: default}`. This profile does not accept a physical NIC for either role. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `dns_udp` | `unbound` / `app-network` | `wildcard` via `private` | `53/udp` | `guest-loopback` 5335 |
| `dns_tcp` | `unbound` / `app-network` | `wildcard` via `private` | `53/tcp` | `guest-loopback` 5335 |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `dns_udp` | `udp` | `dns_udp` via `service` |
| `dns_tcp` | `tcp` | `dns_tcp` via `service` |

A wildcard listener accepts connections within the declared app network. A port becomes available on the guest only when explicitly published. Endpoints do not permit network traffic or make another app wait for this service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/1f1ef6961bd93c2e45789e9e76863a1287bc42af/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Conditional / optional | `/opt/unbound/etc/unbound` | directory / writable | None |
| `dev` | Conditional / optional | `/opt/unbound/etc/unbound/dev` | directory / writable | None |
| `var` | Conditional / optional | `/opt/unbound/etc/unbound/var` | directory / writable | None |
| `control_key` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_control.key` | file / read-only | None |
| `control_cert` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_control.pem` | file / read-only | None |
| `server_key` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_server.key` | file / read-only | None |
| `server_cert` | Conditional / optional | `/opt/unbound/etc/unbound/unbound_server.pem` | file / read-only | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/1f1ef6961bd93c2e45789e9e76863a1287bc42af/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| publish_port | Optional integer, default 5335 | 1..65535; changes both guest-loopback publications, not container port 53. A duplicate instance can select 5336. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Bind service to a physical NIC | Refuses: this profile publishes only guest-loopback sockets. |
| Give two same-guest instances the same publication port | Refuses the listener/publication conflict; choose distinct explicit ports. |

The framework validates these requirements. [Tests](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`unbound-images`](../software-and-runtime.md#registration-software-unbound-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`unbound`](../software-and-runtime.md#registration-runtime-profiles-unbound).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `unbound` | `unbound` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `unbound` | 256 | 1 | 128 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the same resolver and selected loopback publications. Without a configuration mount, startup generates the supported configuration using the app’s resource budget. A retained configuration mount keeps its separate protection checks.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/1f1ef6961bd93c2e45789e9e76863a1287bc42af/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/1f1ef6961bd93c2e45789e9e76863a1287bc42af/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/1f1ef6961bd93c2e45789e9e76863a1287bc42af/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/1f1ef6961bd93c2e45789e9e76863a1287bc42af/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/1f1ef6961bd93c2e45789e9e76863a1287bc42af/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#unbound) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [unbound.yaml](../../../apps/unbound.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"unbound"` |
| <a id="declaration-display-name"></a>`display_name` | `"Unbound"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service"></a>`interfaces.service` | `object` |
| <a id="declaration-interfaces-service-required"></a>`interfaces.service.required` | `true` |
| <a id="declaration-interfaces-service-accepts"></a>`interfaces.service.accepts` | `["guest-loopback"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-dns-udp"></a>`listeners.dns_udp` | `object` |
| <a id="declaration-listeners-dns-udp-service"></a>`listeners.dns_udp.service` | `"unbound"` |
| <a id="declaration-listeners-dns-udp-namespace"></a>`listeners.dns_udp.namespace` | `"app-network"` |
| <a id="declaration-listeners-dns-udp-interface"></a>`listeners.dns_udp.interface` | `"private"` |
| <a id="declaration-listeners-dns-udp-bind"></a>`listeners.dns_udp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-udp-protocol"></a>`listeners.dns_udp.protocol` | `"udp"` |
| <a id="declaration-listeners-dns-udp-port"></a>`listeners.dns_udp.port` | `53` |
| <a id="declaration-listeners-dns-udp-publish"></a>`listeners.dns_udp.publish` | `object` |
| <a id="declaration-listeners-dns-udp-publish-scope"></a>`listeners.dns_udp.publish.scope` | `"guest-loopback"` |
| <a id="declaration-listeners-dns-udp-publish-port"></a>`listeners.dns_udp.publish.port` | `5335` |
| <a id="declaration-listeners-dns-tcp"></a>`listeners.dns_tcp` | `object` |
| <a id="declaration-listeners-dns-tcp-service"></a>`listeners.dns_tcp.service` | `"unbound"` |
| <a id="declaration-listeners-dns-tcp-namespace"></a>`listeners.dns_tcp.namespace` | `"app-network"` |
| <a id="declaration-listeners-dns-tcp-interface"></a>`listeners.dns_tcp.interface` | `"private"` |
| <a id="declaration-listeners-dns-tcp-bind"></a>`listeners.dns_tcp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-tcp-protocol"></a>`listeners.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-listeners-dns-tcp-port"></a>`listeners.dns_tcp.port` | `53` |
| <a id="declaration-listeners-dns-tcp-publish"></a>`listeners.dns_tcp.publish` | `object` |
| <a id="declaration-listeners-dns-tcp-publish-scope"></a>`listeners.dns_tcp.publish.scope` | `"guest-loopback"` |
| <a id="declaration-listeners-dns-tcp-publish-port"></a>`listeners.dns_tcp.publish.port` | `5335` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-dns-udp"></a>`endpoints.dns_udp` | `object` |
| <a id="declaration-endpoints-dns-udp-listener"></a>`endpoints.dns_udp.listener` | `"dns_udp"` |
| <a id="declaration-endpoints-dns-udp-protocol"></a>`endpoints.dns_udp.protocol` | `"udp"` |
| <a id="declaration-endpoints-dns-udp-via"></a>`endpoints.dns_udp.via` | `"service"` |
| <a id="declaration-endpoints-dns-tcp"></a>`endpoints.dns_tcp` | `object` |
| <a id="declaration-endpoints-dns-tcp-listener"></a>`endpoints.dns_tcp.listener` | `"dns_tcp"` |
| <a id="declaration-endpoints-dns-tcp-protocol"></a>`endpoints.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-endpoints-dns-tcp-via"></a>`endpoints.dns_tcp.via` | `"service"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/opt/unbound/etc/unbound"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `false` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-dev"></a>`storage.dev` | `object` |
| <a id="declaration-storage-dev-target"></a>`storage.dev.target` | `"/opt/unbound/etc/unbound/dev"` |
| <a id="declaration-storage-dev-read-only"></a>`storage.dev.read_only` | `false` |
| <a id="declaration-storage-dev-required"></a>`storage.dev.required` | `false` |
| <a id="declaration-storage-dev-kind"></a>`storage.dev.kind` | `"directory"` |
| <a id="declaration-storage-var"></a>`storage.var` | `object` |
| <a id="declaration-storage-var-target"></a>`storage.var.target` | `"/opt/unbound/etc/unbound/var"` |
| <a id="declaration-storage-var-read-only"></a>`storage.var.read_only` | `false` |
| <a id="declaration-storage-var-required"></a>`storage.var.required` | `false` |
| <a id="declaration-storage-var-kind"></a>`storage.var.kind` | `"directory"` |
| <a id="declaration-storage-control-key"></a>`storage.control_key` | `object` |
| <a id="declaration-storage-control-key-target"></a>`storage.control_key.target` | `"/opt/unbound/etc/unbound/unbound_control.key"` |
| <a id="declaration-storage-control-key-read-only"></a>`storage.control_key.read_only` | `true` |
| <a id="declaration-storage-control-key-required"></a>`storage.control_key.required` | `false` |
| <a id="declaration-storage-control-key-kind"></a>`storage.control_key.kind` | `"file"` |
| <a id="declaration-storage-control-cert"></a>`storage.control_cert` | `object` |
| <a id="declaration-storage-control-cert-target"></a>`storage.control_cert.target` | `"/opt/unbound/etc/unbound/unbound_control.pem"` |
| <a id="declaration-storage-control-cert-read-only"></a>`storage.control_cert.read_only` | `true` |
| <a id="declaration-storage-control-cert-required"></a>`storage.control_cert.required` | `false` |
| <a id="declaration-storage-control-cert-kind"></a>`storage.control_cert.kind` | `"file"` |
| <a id="declaration-storage-server-key"></a>`storage.server_key` | `object` |
| <a id="declaration-storage-server-key-target"></a>`storage.server_key.target` | `"/opt/unbound/etc/unbound/unbound_server.key"` |
| <a id="declaration-storage-server-key-read-only"></a>`storage.server_key.read_only` | `true` |
| <a id="declaration-storage-server-key-required"></a>`storage.server_key.required` | `false` |
| <a id="declaration-storage-server-key-kind"></a>`storage.server_key.kind` | `"file"` |
| <a id="declaration-storage-server-cert"></a>`storage.server_cert` | `object` |
| <a id="declaration-storage-server-cert-target"></a>`storage.server_cert.target` | `"/opt/unbound/etc/unbound/unbound_server.pem"` |
| <a id="declaration-storage-server-cert-read-only"></a>`storage.server_cert.read_only` | `true` |
| <a id="declaration-storage-server-cert-required"></a>`storage.server_cert.required` | `false` |
| <a id="declaration-storage-server-cert-kind"></a>`storage.server_cert.kind` | `"file"` |
| <a id="declaration-connections"></a>`connections` | `{}` |
| <a id="declaration-properties"></a>`properties` | `object` |
| <a id="declaration-properties-publish-port"></a>`properties.publish_port` | `5335` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "unbound-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "unbound"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-config"></a>`backup.include.config` | `object` |
| <a id="declaration-backup-include-config-category"></a>`backup.include.config.category` | `"configuration"` |
| <a id="declaration-backup-include-config-capture"></a>`backup.include.config.capture` | `"files"` |
| <a id="declaration-backup-include-var"></a>`backup.include.var` | `object` |
| <a id="declaration-backup-include-var-category"></a>`backup.include.var.category` | `"state"` |
| <a id="declaration-backup-include-var-capture"></a>`backup.include.var.capture` | `"application-export"` |
| <a id="declaration-backup-include-control-key"></a>`backup.include.control_key` | `object` |
| <a id="declaration-backup-include-control-key-category"></a>`backup.include.control_key.category` | `"configuration"` |
| <a id="declaration-backup-include-control-key-capture"></a>`backup.include.control_key.capture` | `"files"` |
| <a id="declaration-backup-include-control-cert"></a>`backup.include.control_cert` | `object` |
| <a id="declaration-backup-include-control-cert-category"></a>`backup.include.control_cert.category` | `"configuration"` |
| <a id="declaration-backup-include-control-cert-capture"></a>`backup.include.control_cert.capture` | `"files"` |
| <a id="declaration-backup-include-server-key"></a>`backup.include.server_key` | `object` |
| <a id="declaration-backup-include-server-key-category"></a>`backup.include.server_key.category` | `"configuration"` |
| <a id="declaration-backup-include-server-key-capture"></a>`backup.include.server_key.capture` | `"files"` |
| <a id="declaration-backup-include-server-cert"></a>`backup.include.server_cert` | `object` |
| <a id="declaration-backup-include-server-cert-category"></a>`backup.include.server_cert.category` | `"configuration"` |
| <a id="declaration-backup-include-server-cert-capture"></a>`backup.include.server_cert.capture` | `"files"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-dev"></a>`backup.exclude.dev` | `"transient"` |
