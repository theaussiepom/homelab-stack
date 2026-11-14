[Documentation](../../README.md) / [Reference](../README.md)

# Zabbix

Run the monitoring server and web frontend. Selecting Zabbix at the site root controls the generated monitoring credentials and which guest agents connect to the server.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: zabbix` |
| Adapter | `zabbix` |
| Owned containers | `zabbix_server`, `zabbix_web` |
| Multiple instances | Select one root monitoring server explicitly when several exist. Independent same-guest server installations are not qualified here. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [zabbix.yaml](../../../apps/zabbix.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Select `zabbix` at the site root to use the existing monitoring credential records. The profile marks `database_password` optional, but the normal deployment code uses credentials managed by monitoring and rejects an independently supplied password. You can select SAML sign-in through the named policy. Local web port 8081 is reserved for setup; it is not a second public interface.

## First installation

For the normal deployment procedure, select monitoring at the site root, supply its existing provider configuration and credential records, and select a HomeLab-managed PostgreSQL app. The example follows these requirements. Although structural validation accepts a password supplied outside root monitoring, the code that prepares private deployment inputs rejects it. Selecting root monitoring alone does not configure a new fleet or verify the database schema and administrator login.

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

Use app `monitoring` in [examples/catalogue/identity-monitoring.yaml](../../../examples/catalogue/identity-monitoring.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/identity-monitoring.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web_interface` | Yes | `guest-interface` |
| `server_interface` | Yes | `guest-interface` |
| `postgresql_interface` | Yes | `guest-interface` |
| `metrics_interface` | No; selected capability can require it | `guest-interface` |
| `management_interface` | No; selected capability can require it | `guest-interface` |
| `private_interface` | Yes | `app-network` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `server_listener` | `zabbix_server` / `app-network` | `wildcard` via `private_interface` | `10051/tcp` | `guest-interface` 10051 via `server_interface` |
| `web_listener` | `zabbix_web` / `app-network` | `wildcard` via `private_interface` | `8080/tcp` | `guest-interface` 8080 via `web_interface` |
| `local_web_listener` | `zabbix_web` / `app-network` | `wildcard` via `private_interface` | `8080/tcp` | `guest-loopback` 8081 |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web_endpoint` | `http` | `web_listener` via `web_interface` |
| `server_endpoint` | `tcp` | `server_listener` via `server_interface` |

A wildcard listener accepts connections within the declared app network. A port becomes available on the guest only when explicitly published. Endpoints do not permit network traffic or make another app wait for this service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

No app storage role is declared. Generated private runtime files retain their separate owned paths.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `postgresql` | Yes | `start` | None |
| `public` | `https` | No | `start` | None |
| `proxmox` | `https` | No | None | None |
| `metrics` | `influxdb` | No | None | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `database_password` | Optional until its capability requires it |

Authentication requirement: `zabbix-saml` (optional), selected by a named site authentication policy.

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| database | Required mapping | name and user use `[a-z][a-z0-9_]{0,62}`, excluding postgres/template0/template1. |

## Invalid cases

Start from the complete [examples/catalogue/identity-monitoring.yaml](../../../examples/catalogue/identity-monitoring.yaml), app `monitoring`, using the [source-only setup](../../guides/first-configuration.md). Change only the input described; retain the rest of that composition. Diagnostics below are emitted results, not inferred field paths. Where no `at` context appears, no field path was emitted.

| Invalid variation | Actual refusal and enforcing layer | Cause and supported correction |
| --- | --- | --- |
| <a id="invalid-omit-managed-database"></a>Remove `connections.monitoring_database`. | `component.connection-required` — Required connection binding during resolution. | Zabbix requires its PostgreSQL producer connection. Restore that connection and its selected managed-credential ownership; do not add an unrelated password to bypass monitoring ownership. |
| <a id="invalid-reserved-database-name"></a>Set `properties.database.name: postgres`, retaining the existing valid user. | `component.database at apps.monitoring.properties` — Adapter database-property validation. | The reserved PostgreSQL database name is not an application database selection. Restore `example_monitoring` from the complete example or another accepted non-reserved SQL ID. |

After repair, resolve the same complete source and generate every guest’s deployment packet; expect both to pass as the unchanged baseline does. Source checks neither inspect credential contents nor establish installation, routing, socket isolation or service recovery on a target.

The existing [complete-profile integrations](../../../tests/test_profile_examples.py) and [composition cases](../../../tests/test_component_composition.py) exercise the real selected framework. Its validators, binding checks and packet/file builders enforce these boundaries; the [testing guide](../../testing.md#documentation-conformance) explains the evidence limits.

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

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the selected root server, member inventory and ordinary agent configuration while preserving existing monitoring credentials, pre-shared-key (PSK) identities and history. Root selection is an explicit monitoring capability, not an instruction to rebuild a fleet.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/f3c7ad1636da18c160a55051991e6c4d4a87e742/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#zabbix) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [zabbix.yaml](../../../apps/zabbix.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"zabbix"` |
| <a id="declaration-display-name"></a>`display_name` | `"Zabbix"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-server-interface"></a>`interfaces.server_interface` | `object` |
| <a id="declaration-interfaces-server-interface-required"></a>`interfaces.server_interface.required` | `true` |
| <a id="declaration-interfaces-server-interface-accepts"></a>`interfaces.server_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-postgresql-interface"></a>`interfaces.postgresql_interface` | `object` |
| <a id="declaration-interfaces-postgresql-interface-required"></a>`interfaces.postgresql_interface.required` | `true` |
| <a id="declaration-interfaces-postgresql-interface-accepts"></a>`interfaces.postgresql_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-metrics-interface"></a>`interfaces.metrics_interface` | `object` |
| <a id="declaration-interfaces-metrics-interface-required"></a>`interfaces.metrics_interface.required` | `false` |
| <a id="declaration-interfaces-metrics-interface-accepts"></a>`interfaces.metrics_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management-interface"></a>`interfaces.management_interface` | `object` |
| <a id="declaration-interfaces-management-interface-required"></a>`interfaces.management_interface.required` | `false` |
| <a id="declaration-interfaces-management-interface-accepts"></a>`interfaces.management_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private-interface"></a>`interfaces.private_interface` | `object` |
| <a id="declaration-interfaces-private-interface-required"></a>`interfaces.private_interface.required` | `true` |
| <a id="declaration-interfaces-private-interface-accepts"></a>`interfaces.private_interface.accepts` | `["app-network"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-server-listener"></a>`listeners.server_listener` | `object` |
| <a id="declaration-listeners-server-listener-service"></a>`listeners.server_listener.service` | `"zabbix_server"` |
| <a id="declaration-listeners-server-listener-namespace"></a>`listeners.server_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-server-listener-interface"></a>`listeners.server_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-server-listener-bind"></a>`listeners.server_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-server-listener-protocol"></a>`listeners.server_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-server-listener-port"></a>`listeners.server_listener.port` | `10051` |
| <a id="declaration-listeners-server-listener-publish"></a>`listeners.server_listener.publish` | `object` |
| <a id="declaration-listeners-server-listener-publish-scope"></a>`listeners.server_listener.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-server-listener-publish-interface"></a>`listeners.server_listener.publish.interface` | `"server_interface"` |
| <a id="declaration-listeners-server-listener-publish-port"></a>`listeners.server_listener.publish.port` | `10051` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"zabbix_web"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `8080` |
| <a id="declaration-listeners-web-listener-publish"></a>`listeners.web_listener.publish` | `object` |
| <a id="declaration-listeners-web-listener-publish-scope"></a>`listeners.web_listener.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-listener-publish-interface"></a>`listeners.web_listener.publish.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-publish-port"></a>`listeners.web_listener.publish.port` | `8080` |
| <a id="declaration-listeners-local-web-listener"></a>`listeners.local_web_listener` | `object` |
| <a id="declaration-listeners-local-web-listener-service"></a>`listeners.local_web_listener.service` | `"zabbix_web"` |
| <a id="declaration-listeners-local-web-listener-namespace"></a>`listeners.local_web_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-local-web-listener-interface"></a>`listeners.local_web_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-local-web-listener-bind"></a>`listeners.local_web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-local-web-listener-protocol"></a>`listeners.local_web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-local-web-listener-port"></a>`listeners.local_web_listener.port` | `8080` |
| <a id="declaration-listeners-local-web-listener-publish"></a>`listeners.local_web_listener.publish` | `object` |
| <a id="declaration-listeners-local-web-listener-publish-scope"></a>`listeners.local_web_listener.publish.scope` | `"guest-loopback"` |
| <a id="declaration-listeners-local-web-listener-publish-port"></a>`listeners.local_web_listener.publish.port` | `8081` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-endpoints-server-endpoint"></a>`endpoints.server_endpoint` | `object` |
| <a id="declaration-endpoints-server-endpoint-listener"></a>`endpoints.server_endpoint.listener` | `"server_listener"` |
| <a id="declaration-endpoints-server-endpoint-protocol"></a>`endpoints.server_endpoint.protocol` | `"tcp"` |
| <a id="declaration-endpoints-server-endpoint-via"></a>`endpoints.server_endpoint.via` | `"server_interface"` |
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
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `{}` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
