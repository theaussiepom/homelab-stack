[Documentation](../../README.md) / [Reference](../README.md)

# Zabbix

Run the monitoring server and web frontend. Root Zabbix selection owns the generated monitoring credentials and selected guest-agent relationship.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: zabbix` |
| Adapter | `zabbix` |
| Owned containers | `zabbix_server`, `zabbix_web` |
| Multiple instances | Select one root monitoring server explicitly when several exist. Independent same-guest server installations are not qualified here. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [zabbix.yaml](../../../apps/zabbix.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Select root zabbix to activate the existing generated monitoring credential owner. database_password is structurally optional in the profile; the current ordinary caller uses monitoring-owned material and refuses an arbitrary supplied scalar. SAML is optional through the named policy. Local web8081 is the bounded setup path, not a second user-facing exposure.

## First installation

The current ordinary deployment path requires explicit root monitoring, its already configured provider/credential owner and a selected owned PostgreSQL app. The example uses this path; an outside-root password is structurally accepted but does not satisfy the ordinary materializer. Root monitoring does not by itself commission a new fleet or prove schema readiness/administrator login.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/identity-monitoring.yaml).

```yaml
apps:
  monitoring:
    profile: zabbix
    guest: monitoring
    lifecycle: retained
```

### Practical complete example

Use app `monitoring` in [examples/catalogue/identity-monitoring.yaml](../../../examples/catalogue/identity-monitoring.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/identity-monitoring.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `server` | Yes | `guest-interface` |
| `postgresql` | Yes | `guest-interface` |
| `metrics` | No; selected capability can require it | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |
| `private` | Yes | `app-network` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `server` | `zabbix_server` / `app-network` | `wildcard` via `private` | `10051/tcp` | `guest-interface` 10051 via `server` |
| `web` | `zabbix_web` / `app-network` | `wildcard` via `private` | `8080/tcp` | `guest-interface` 8080 via `web` |
| `local_web` | `zabbix_web` / `app-network` | `wildcard` via `private` | `8080/tcp` | `guest-loopback` 8081 |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |
| `server` | `tcp` | `server` via `server` |

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

No app storage role is declared. Generated private runtime files retain their separate owned paths.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `postgresql` | Yes | `start` | None |
| `public` | `https` | No | `start` | None |
| `proxmox` | `https` | No | None | None |
| `metrics` | `influxdb` | No | None | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `database_password` | Optional until its capability requires it |

Authentication requirement: `zabbix-saml` (optional), selected by a named site authentication policy.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| database | Required mapping | name and user use `[a-z][a-z0-9_]{0,62}`, excluding postgres/template0/template1. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Select root monitoring and also supply database_password | Refuses duplicate credential ownership. |
| Bind database to the wrong protocol/port | Refuses the PostgreSQL binding. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`zabbix-images`](../software-and-runtime.md#registration-software-zabbix-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`zabbix`](../software-and-runtime.md#registration-runtime-profiles-zabbix).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `zabbix_server` | `zabbix_server` | Immutable registry digest |
| `zabbix_web` | `zabbix_web` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `zabbix_server` | 768 | 1 | 256 |
| `zabbix_web` | 512 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the selected root server, member inventory and ordinary agent configuration while preserving existing monitoring credential/PSK identities and history. Root selection is an explicit monitoring capability, not an instruction to rebuild a fleet. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [zabbix.yaml](../../../apps/zabbix.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"zabbix"` |
| <a id="declaration-display-name"></a>`display_name` | `"Zabbix"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-server"></a>`interfaces.server` | `object` |
| <a id="declaration-interfaces-server-required"></a>`interfaces.server.required` | `true` |
| <a id="declaration-interfaces-server-accepts"></a>`interfaces.server.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-postgresql"></a>`interfaces.postgresql` | `object` |
| <a id="declaration-interfaces-postgresql-required"></a>`interfaces.postgresql.required` | `true` |
| <a id="declaration-interfaces-postgresql-accepts"></a>`interfaces.postgresql.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-metrics"></a>`interfaces.metrics` | `object` |
| <a id="declaration-interfaces-metrics-required"></a>`interfaces.metrics.required` | `false` |
| <a id="declaration-interfaces-metrics-accepts"></a>`interfaces.metrics.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management"></a>`interfaces.management` | `object` |
| <a id="declaration-interfaces-management-required"></a>`interfaces.management.required` | `false` |
| <a id="declaration-interfaces-management-accepts"></a>`interfaces.management.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-server"></a>`listeners.server` | `object` |
| <a id="declaration-listeners-server-service"></a>`listeners.server.service` | `"zabbix_server"` |
| <a id="declaration-listeners-server-namespace"></a>`listeners.server.namespace` | `"app-network"` |
| <a id="declaration-listeners-server-interface"></a>`listeners.server.interface` | `"private"` |
| <a id="declaration-listeners-server-bind"></a>`listeners.server.bind` | `"wildcard"` |
| <a id="declaration-listeners-server-protocol"></a>`listeners.server.protocol` | `"tcp"` |
| <a id="declaration-listeners-server-port"></a>`listeners.server.port` | `10051` |
| <a id="declaration-listeners-server-publish"></a>`listeners.server.publish` | `object` |
| <a id="declaration-listeners-server-publish-scope"></a>`listeners.server.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-server-publish-interface"></a>`listeners.server.publish.interface` | `"server"` |
| <a id="declaration-listeners-server-publish-port"></a>`listeners.server.publish.port` | `10051` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"zabbix_web"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"private"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `8080` |
| <a id="declaration-listeners-web-publish"></a>`listeners.web.publish` | `object` |
| <a id="declaration-listeners-web-publish-scope"></a>`listeners.web.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-publish-interface"></a>`listeners.web.publish.interface` | `"web"` |
| <a id="declaration-listeners-web-publish-port"></a>`listeners.web.publish.port` | `8080` |
| <a id="declaration-listeners-local-web"></a>`listeners.local_web` | `object` |
| <a id="declaration-listeners-local-web-service"></a>`listeners.local_web.service` | `"zabbix_web"` |
| <a id="declaration-listeners-local-web-namespace"></a>`listeners.local_web.namespace` | `"app-network"` |
| <a id="declaration-listeners-local-web-interface"></a>`listeners.local_web.interface` | `"private"` |
| <a id="declaration-listeners-local-web-bind"></a>`listeners.local_web.bind` | `"wildcard"` |
| <a id="declaration-listeners-local-web-protocol"></a>`listeners.local_web.protocol` | `"tcp"` |
| <a id="declaration-listeners-local-web-port"></a>`listeners.local_web.port` | `8080` |
| <a id="declaration-listeners-local-web-publish"></a>`listeners.local_web.publish` | `object` |
| <a id="declaration-listeners-local-web-publish-scope"></a>`listeners.local_web.publish.scope` | `"guest-loopback"` |
| <a id="declaration-listeners-local-web-publish-port"></a>`listeners.local_web.publish.port` | `8081` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-endpoints-server"></a>`endpoints.server` | `object` |
| <a id="declaration-endpoints-server-listener"></a>`endpoints.server.listener` | `"server"` |
| <a id="declaration-endpoints-server-protocol"></a>`endpoints.server.protocol` | `"tcp"` |
| <a id="declaration-endpoints-server-via"></a>`endpoints.server.via` | `"server"` |
| <a id="declaration-storage"></a>`storage` | `{}` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-database"></a>`connections.database` | `object` |
| <a id="declaration-connections-database-type"></a>`connections.database.type` | `"postgresql"` |
| <a id="declaration-connections-database-required"></a>`connections.database.required` | `true` |
| <a id="declaration-connections-database-readiness"></a>`connections.database.readiness` | `["start"]` |
| <a id="declaration-connections-public"></a>`connections.public` | `object` |
| <a id="declaration-connections-public-type"></a>`connections.public.type` | `"https"` |
| <a id="declaration-connections-public-required"></a>`connections.public.required` | `false` |
| <a id="declaration-connections-public-readiness"></a>`connections.public.readiness` | `["start"]` |
| <a id="declaration-connections-proxmox"></a>`connections.proxmox` | `object` |
| <a id="declaration-connections-proxmox-type"></a>`connections.proxmox.type` | `"https"` |
| <a id="declaration-connections-proxmox-required"></a>`connections.proxmox.required` | `false` |
| <a id="declaration-connections-metrics"></a>`connections.metrics` | `object` |
| <a id="declaration-connections-metrics-type"></a>`connections.metrics.type` | `"influxdb"` |
| <a id="declaration-connections-metrics-required"></a>`connections.metrics.required` | `false` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "zabbix-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "zabbix"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-authentication"></a>`authentication` | `"zabbix-saml"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-database-password"></a>`secrets.database_password` | `object` |
| <a id="declaration-secrets-database-password-required"></a>`secrets.database_password.required` | `false` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
