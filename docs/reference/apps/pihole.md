[Documentation](../../README.md) / [Reference](../README.md)

# Pi-hole

Provide DNS filtering and a web UI. Select an upstream resolver explicitly; Unbound is one possible independent upstream.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: pihole` |
| Adapter | `pihole` |
| Owned containers | `pihole` |
| Multiple instances | Use one Pi-hole instance per guest. The file tracking HomeLab-managed DNS records has a fixed location, and the DNS and web listeners must not conflict with other listeners. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [pihole.yaml](../../../apps/pihole.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The optional upstream interface role becomes necessary when binding the required upstream connection. A same-guest Unbound target uses guest-loopback; a remote target uses a physical role. The context’s DNS setting supplies an address; it does not create the upstream connection or make Pi-hole wait for it.

## First installation

You need a prepared Pi-hole configuration directory and an explicitly selected upstream resolver. This profile does not generate a complete new Pi-hole configuration or adopt arbitrary existing data. The practical example therefore uses an already HomeLab-managed installation.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/local-dns/site.yaml).

```yaml
apps:
  filtering:
    profile: pihole
    guest: resolver
    lifecycle: retained
```

### Practical complete example

Use app `filtering` in [examples/catalogue/local-dns/site.yaml](../../../examples/catalogue/local-dns/site.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/local-dns/site.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-interface` |
| `upstream` | No; selected capability can require it | `guest-interface`, `guest-loopback` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `dns_udp` | `pihole` / `host` | `wildcard` via `service` | `53/udp` | None; listener remains in its declared namespace |
| `dns_tcp` | `pihole` / `host` | `wildcard` via `service` | `53/tcp` | None; listener remains in its declared namespace |
| `web` | `pihole` / `host` | `wildcard` via `service` | `80/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `dns_udp` | `udp` | `dns_udp` via `service` |
| `dns_tcp` | `tcp` | `dns_tcp` via `service` |
| `web` | `http` | `web` via `service` |

A wildcard host listener can accept connections through interfaces other than the advertised NIC. An endpoint gives consumers an address and port. It does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/etc/pihole` | directory / writable | None |
| `database` | Conditional / optional | `/ftl-db` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `upstream` | `dns` | Yes | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/app-properties.md).

This adapter accepts no application property keys. It rejects unknown keys and provides no way to pass arbitrary commands, environment variables or mounts.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit the upstream connection | Refuses the required connection. |
| Use a physical source role for a same-guest loopback upstream | Refuses the connection-scope relationship. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`pihole-images`](../software-and-runtime.md#registration-software-pihole-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`pihole`](../software-and-runtime.md#registration-runtime-profiles-pihole).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `pihole` | `pihole` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `pihole` | 256 | 1 | 128 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab updates the selected upstream and the DNS records it manages, while preserving the configuration and unrelated records. It can remove a record only when the previous deployment payload proves that it managed that name. This is not a general DNS cleanup procedure.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#pihole) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [pihole.yaml](../../../apps/pihole.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"pihole"` |
| <a id="declaration-display-name"></a>`display_name` | `"Pi-hole"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service"></a>`interfaces.service` | `object` |
| <a id="declaration-interfaces-service-required"></a>`interfaces.service.required` | `true` |
| <a id="declaration-interfaces-service-accepts"></a>`interfaces.service.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-upstream"></a>`interfaces.upstream` | `object` |
| <a id="declaration-interfaces-upstream-required"></a>`interfaces.upstream.required` | `false` |
| <a id="declaration-interfaces-upstream-accepts"></a>`interfaces.upstream.accepts` | `["guest-interface", "guest-loopback"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-dns-udp"></a>`listeners.dns_udp` | `object` |
| <a id="declaration-listeners-dns-udp-service"></a>`listeners.dns_udp.service` | `"pihole"` |
| <a id="declaration-listeners-dns-udp-namespace"></a>`listeners.dns_udp.namespace` | `"host"` |
| <a id="declaration-listeners-dns-udp-interface"></a>`listeners.dns_udp.interface` | `"service"` |
| <a id="declaration-listeners-dns-udp-bind"></a>`listeners.dns_udp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-udp-protocol"></a>`listeners.dns_udp.protocol` | `"udp"` |
| <a id="declaration-listeners-dns-udp-port"></a>`listeners.dns_udp.port` | `53` |
| <a id="declaration-listeners-dns-tcp"></a>`listeners.dns_tcp` | `object` |
| <a id="declaration-listeners-dns-tcp-service"></a>`listeners.dns_tcp.service` | `"pihole"` |
| <a id="declaration-listeners-dns-tcp-namespace"></a>`listeners.dns_tcp.namespace` | `"host"` |
| <a id="declaration-listeners-dns-tcp-interface"></a>`listeners.dns_tcp.interface` | `"service"` |
| <a id="declaration-listeners-dns-tcp-bind"></a>`listeners.dns_tcp.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-tcp-protocol"></a>`listeners.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-listeners-dns-tcp-port"></a>`listeners.dns_tcp.port` | `53` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"pihole"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"host"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"service"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `80` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-dns-udp"></a>`endpoints.dns_udp` | `object` |
| <a id="declaration-endpoints-dns-udp-listener"></a>`endpoints.dns_udp.listener` | `"dns_udp"` |
| <a id="declaration-endpoints-dns-udp-protocol"></a>`endpoints.dns_udp.protocol` | `"udp"` |
| <a id="declaration-endpoints-dns-udp-via"></a>`endpoints.dns_udp.via` | `"service"` |
| <a id="declaration-endpoints-dns-tcp"></a>`endpoints.dns_tcp` | `object` |
| <a id="declaration-endpoints-dns-tcp-listener"></a>`endpoints.dns_tcp.listener` | `"dns_tcp"` |
| <a id="declaration-endpoints-dns-tcp-protocol"></a>`endpoints.dns_tcp.protocol` | `"tcp"` |
| <a id="declaration-endpoints-dns-tcp-via"></a>`endpoints.dns_tcp.via` | `"service"` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"service"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/etc/pihole"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `true` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-database"></a>`storage.database` | `object` |
| <a id="declaration-storage-database-target"></a>`storage.database.target` | `"/ftl-db"` |
| <a id="declaration-storage-database-read-only"></a>`storage.database.read_only` | `false` |
| <a id="declaration-storage-database-required"></a>`storage.database.required` | `false` |
| <a id="declaration-storage-database-kind"></a>`storage.database.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-upstream"></a>`connections.upstream` | `object` |
| <a id="declaration-connections-upstream-type"></a>`connections.upstream.type` | `"dns"` |
| <a id="declaration-connections-upstream-required"></a>`connections.upstream.required` | `true` |
| <a id="declaration-connections-upstream-readiness"></a>`connections.upstream.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "pihole-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "pihole"]` |
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
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-database"></a>`backup.exclude.database` | `"transient"` |
