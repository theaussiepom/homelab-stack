[Documentation](../../README.md) / [Reference](../README.md)

# Bitwarden

Run the existing Bitwarden Lite vault against its selected MariaDB database, preserving its installation keys and the numeric user and group IDs that own its data.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: bitwarden` |
| Adapter | `bitwarden` |
| Owned containers | `bitwarden` |
| Multiple instances | Each instance needs separate storage, a distinct Compose project and distinct service names. Running multiple instances on one guest has not been verified here. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [bitwarden.yaml](../../../apps/bitwarden.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## First installation

Not implemented by this profile: it cannot create a brand-new vault. The example requires an already HomeLab-managed vault, database, installation keys and data.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/vault.yaml).

```yaml
apps:
  vault:
    profile: bitwarden
    guest: vault
    lifecycle: retained
```

### Practical complete example

Use app `vault` in [examples/catalogue/vault.yaml](../../../examples/catalogue/vault.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/vault.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `database` | Yes | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |
| `private` | Yes | `app-network` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `bitwarden` / `app-network` | `wildcard` via `private` | `8080/tcp` | `guest-interface` 8080 via `web` |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

The web listener accepts connections inside the private app network. Its explicit publication makes TCP port 8080 available through the guest interface bound to `web`. The endpoint advertises the resulting address and port; it does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/etc/bitwarden` | directory / writable | None |
| `logs` | Yes | `/var/log/bitwarden` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `mariadb` | Yes | `configure`, `start` | None |
| `public` | `https` | No | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `runtime_environment` | Required |

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| issuer | Required mapping | protocol is http or https; domain names a site domains entry. This metadata is separate from the HTTPS app origin. |
| database_name | Required string | Use a nonempty name containing letters, digits or underscores. It must match the sealed runtime environment and selected MariaDB database. |
| data_uid / data_gid | Required positive integers | 1..2147483647, matching existing numeric data ownership and private environment values. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Select lifecycle fresh | Refuses: new-vault creation is unsupported. |
| Supply a floating or local image or an authored environment checksum | Validation rejects floating or local images because this profile requires an immutable registry image. It also rejects an authored environment-checksum property, which this adapter does not accept. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`bitwarden-images`](../software-and-runtime.md#registration-software-bitwarden-images), [`mariadb-client`](../software-and-runtime.md#registration-software-mariadb-client). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`bitwarden`](../software-and-runtime.md#registration-runtime-profiles-bitwarden).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `bitwarden` | `bitwarden` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `bitwarden` | 1536 | 1 | 256 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the existing vault, preserving its database, installation keys, data and selected protected runtime environment. Software and image changes follow the normal immutable manifest policy; no vault upgrade or credential rotation is implied. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/85868a5a4b430e01943ca44eb83e92c4e36a5050/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#bitwarden) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [bitwarden.yaml](../../../apps/bitwarden.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"bitwarden"` |
| <a id="declaration-display-name"></a>`display_name` | `"Bitwarden"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-database"></a>`interfaces.database` | `object` |
| <a id="declaration-interfaces-database-required"></a>`interfaces.database.required` | `true` |
| <a id="declaration-interfaces-database-accepts"></a>`interfaces.database.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management"></a>`interfaces.management` | `object` |
| <a id="declaration-interfaces-management-required"></a>`interfaces.management.required` | `false` |
| <a id="declaration-interfaces-management-accepts"></a>`interfaces.management.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private"></a>`interfaces.private` | `object` |
| <a id="declaration-interfaces-private-required"></a>`interfaces.private.required` | `true` |
| <a id="declaration-interfaces-private-accepts"></a>`interfaces.private.accepts` | `["app-network"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"bitwarden"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"private"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `8080` |
| <a id="declaration-listeners-web-publish"></a>`listeners.web.publish` | `object` |
| <a id="declaration-listeners-web-publish-scope"></a>`listeners.web.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-publish-interface"></a>`listeners.web.publish.interface` | `"web"` |
| <a id="declaration-listeners-web-publish-port"></a>`listeners.web.publish.port` | `8080` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/etc/bitwarden"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-storage-logs"></a>`storage.logs` | `object` |
| <a id="declaration-storage-logs-target"></a>`storage.logs.target` | `"/var/log/bitwarden"` |
| <a id="declaration-storage-logs-read-only"></a>`storage.logs.read_only` | `false` |
| <a id="declaration-storage-logs-required"></a>`storage.logs.required` | `true` |
| <a id="declaration-storage-logs-kind"></a>`storage.logs.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-database"></a>`connections.database` | `object` |
| <a id="declaration-connections-database-type"></a>`connections.database.type` | `"mariadb"` |
| <a id="declaration-connections-database-required"></a>`connections.database.required` | `true` |
| <a id="declaration-connections-database-readiness"></a>`connections.database.readiness` | `["configure", "start"]` |
| <a id="declaration-connections-public"></a>`connections.public` | `object` |
| <a id="declaration-connections-public-type"></a>`connections.public.type` | `"https"` |
| <a id="declaration-connections-public-required"></a>`connections.public.required` | `false` |
| <a id="declaration-connections-public-readiness"></a>`connections.public.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "bitwarden-images", "mariadb-client"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "bitwarden"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-runtime-environment"></a>`secrets.runtime_environment` | `object` |
| <a id="declaration-secrets-runtime-environment-required"></a>`secrets.runtime_environment.required` | `true` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"state"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-logs"></a>`backup.exclude.logs` | `"transient"` |
