[Documentation](../../README.md) / [Reference](../README.md)

# Pi-hole with a separate web interface

Keep DNS on its existing service address and bind the web UI to a separately selected guest NIC. Select an upstream resolver explicitly; Unbound is one possible independent upstream. The ordinary [pihole](pihole.md) profile retains its wildcard web behavior.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: pihole-web` |
| Adapter | `pihole` |
| Owned containers | `pihole` |
| Multiple instances | Use one Pi-hole instance per guest. The file tracking HomeLab-managed DNS records has a fixed location, and the DNS and web listeners must not conflict with other listeners. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [pihole-web.yaml](../../../apps/pihole-web.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The optional upstream interface role becomes necessary when binding the required upstream connection. A same-guest Unbound target uses guest-loopback; a remote target uses a physical role. The context’s DNS setting supplies an address; it does not create the upstream connection or make Pi-hole wait for it.

## Separate web behavior

Bind `service_interface` to the existing DNS NIC and `web_interface` to the web NIC. The DNS UDP/TCP 53 declarations and upstream stay unchanged. `web_listener` binds only the selected web IPv4 address on TCP 80; `web_endpoint` advertises that address. HomeLab sets only `FTLCONF_webserver_port` to that address and port, preserving the existing image, data, service identity, authentication and other environment settings. The generated socket check rejects a wildcard or legacy web bind. The [Pi-hole FTL setting](https://docs.pi-hole.net/ftldns/configfile/#port) supports this address-and-port form. This selects HTTP 80 only; HTTPS remains the responsibility of an explicitly selected ingress.

Changing this selected listener recreates the owned container and may briefly interrupt DNS. Review that interruption before deployment. Existing consumers of the ordinary profile do not opt in automatically. Compilation and socket-check generation do not prove live listener or DNS acceptance.

## First installation

You need a prepared Pi-hole configuration directory and an explicitly selected upstream resolver. This profile does not generate a complete new Pi-hole configuration or adopt arbitrary existing data. The practical example therefore uses an already HomeLab-managed installation.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/local-dns-web/site.yaml).

```yaml
apps:
  filtering:
    profile: pihole-web
    guest: resolver
    lifecycle: retained
```

### Practical complete example

Use app `filtering` in [examples/catalogue/local-dns-web/site.yaml](../../../examples/catalogue/local-dns-web/site.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/local-dns-web/site.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service_interface` | Yes | `guest-interface` |
| `web_interface` | Yes | `guest-interface` |
| `upstream_interface` | No; selected capability can require it | `guest-interface`, `guest-loopback` |

Use an expanded `interface: NIC_ID` binding beneath each role to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `dns_udp_listener` | `pihole` / `host` | `wildcard` via `service_interface` | `53/udp` | None; listener remains in its declared namespace |
| `dns_tcp_listener` | `pihole` / `host` | `wildcard` via `service_interface` | `53/tcp` | None; listener remains in its declared namespace |
| `web_listener` | `pihole` / `host` | `interface` via `web_interface` | `80/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `dns_udp_endpoint` | `udp` | `dns_udp_listener` via `service_interface` |
| `dns_tcp_endpoint` | `tcp` | `dns_tcp_listener` via `service_interface` |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |

The DNS wildcard listeners can accept connections through interfaces other than the advertised DNS NIC. The web socket is separately bound; this does not restrict DNS to that web NIC. An endpoint gives consumers an address and port. It does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

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

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/app-properties.md).

This adapter accepts no application property keys. It rejects unknown keys and provides no way to pass arbitrary commands, environment variables or mounts.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit the upstream connection | Refuses the required connection. |
| Omit `web_interface` | Refuses the required role before generating a packet. |
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

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/63c656ad424a1a7cc6b8d56f000828d114926885/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#pihole-web) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [pihole-web.yaml](../../../apps/pihole-web.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"pihole"` |
| <a id="declaration-display-name"></a>`display_name` | `"Pi-hole with a separate web interface"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-service-interface"></a>`interfaces.service_interface` | `object` |
| <a id="declaration-interfaces-service-interface-required"></a>`interfaces.service_interface.required` | `true` |
| <a id="declaration-interfaces-service-interface-accepts"></a>`interfaces.service_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-upstream-interface"></a>`interfaces.upstream_interface` | `object` |
| <a id="declaration-interfaces-upstream-interface-required"></a>`interfaces.upstream_interface.required` | `false` |
| <a id="declaration-interfaces-upstream-interface-accepts"></a>`interfaces.upstream_interface.accepts` | `["guest-interface", "guest-loopback"]` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-dns-udp-listener"></a>`listeners.dns_udp_listener` | `object` |
| <a id="declaration-listeners-dns-udp-listener-service"></a>`listeners.dns_udp_listener.service` | `"pihole"` |
| <a id="declaration-listeners-dns-udp-listener-namespace"></a>`listeners.dns_udp_listener.namespace` | `"host"` |
| <a id="declaration-listeners-dns-udp-listener-interface"></a>`listeners.dns_udp_listener.interface` | `"service_interface"` |
| <a id="declaration-listeners-dns-udp-listener-bind"></a>`listeners.dns_udp_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-udp-listener-protocol"></a>`listeners.dns_udp_listener.protocol` | `"udp"` |
| <a id="declaration-listeners-dns-udp-listener-port"></a>`listeners.dns_udp_listener.port` | `53` |
| <a id="declaration-listeners-dns-tcp-listener"></a>`listeners.dns_tcp_listener` | `object` |
| <a id="declaration-listeners-dns-tcp-listener-service"></a>`listeners.dns_tcp_listener.service` | `"pihole"` |
| <a id="declaration-listeners-dns-tcp-listener-namespace"></a>`listeners.dns_tcp_listener.namespace` | `"host"` |
| <a id="declaration-listeners-dns-tcp-listener-interface"></a>`listeners.dns_tcp_listener.interface` | `"service_interface"` |
| <a id="declaration-listeners-dns-tcp-listener-bind"></a>`listeners.dns_tcp_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-dns-tcp-listener-protocol"></a>`listeners.dns_tcp_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-dns-tcp-listener-port"></a>`listeners.dns_tcp_listener.port` | `53` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"pihole"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"host"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"interface"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `80` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-dns-udp-endpoint"></a>`endpoints.dns_udp_endpoint` | `object` |
| <a id="declaration-endpoints-dns-udp-endpoint-listener"></a>`endpoints.dns_udp_endpoint.listener` | `"dns_udp_listener"` |
| <a id="declaration-endpoints-dns-udp-endpoint-protocol"></a>`endpoints.dns_udp_endpoint.protocol` | `"udp"` |
| <a id="declaration-endpoints-dns-udp-endpoint-via"></a>`endpoints.dns_udp_endpoint.via` | `"service_interface"` |
| <a id="declaration-endpoints-dns-tcp-endpoint"></a>`endpoints.dns_tcp_endpoint` | `object` |
| <a id="declaration-endpoints-dns-tcp-endpoint-listener"></a>`endpoints.dns_tcp_endpoint.listener` | `"dns_tcp_listener"` |
| <a id="declaration-endpoints-dns-tcp-endpoint-protocol"></a>`endpoints.dns_tcp_endpoint.protocol` | `"tcp"` |
| <a id="declaration-endpoints-dns-tcp-endpoint-via"></a>`endpoints.dns_tcp_endpoint.via` | `"service_interface"` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
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
