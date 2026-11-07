[Documentation](../../README.md) / [Reference](../README.md)

# Node-RED

Run an existing Node-RED installation with an explicitly supplied custom image archive, existing scripts for settings and health checks, and its existing OpenID Connect (OIDC) sign-in setup.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: node_red` |
| Adapter | `node_red` |
| Owned containers | `node_red` |
| Multiple instances | Fixed host TCP 1880; use separate guests for independent instances. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [node_red.yaml](../../../apps/node_red.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The optional settings and healthcheck roles become mandatory in retained mode. The node-red-retained-oidc policy is required. You must supply the existing custom nodes, flows, secrets and sign-in configuration; this profile does not install or migrate them implicitly. api_token is optional until the selected API capability requires it.

## First installation

This profile updates an existing installation only. Supply its custom image archive, settings and health-check scripts, and configured OpenID Connect sign-in before deployment. It does not create a new public Node-RED installation. Choose [node_red-public](node_red-public.md) for the supported new public-image path.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/existing-automation.yaml).

```yaml
apps:
  node_red:
    profile: node_red
    guest: node-red
    lifecycle: retained
```

### Practical complete example

Use app `node_red` in [examples/catalogue/existing-automation.yaml](../../../examples/catalogue/existing-automation.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/existing-automation.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `broker` | No; selected capability can require it | `guest-interface` |

Use `{interface: NIC_ID}` to select a physical guest interface. Select loopback or an app network through its explicit scope. A role does not create another network interface. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `node_red` / `host` | `wildcard` via `web` | `1880/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can accept connections through interfaces other than the advertised NIC. An endpoint gives consumers an address and port. It does not create a firewall rule or HTTPS route, or make a consumer wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/5d4d178daf0688c9ffc6de7770ee44c2f7d38e7a/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/data` | directory / writable | None |
| `config` | Yes | `/config` | directory / writable | None |
| `settings` | Conditional / optional | `/runtime-settings.js` | file / read-only | None |
| `healthcheck` | Conditional / optional | `/healthcheck.js` | file / read-only | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `api_token` | Optional until its capability requires it |

Authentication requirement: `node-red-retained-oidc` (required), selected by a named site authentication policy.

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/5d4d178daf0688c9ffc6de7770ee44c2f7d38e7a/docs/reference/app-properties.md).

This adapter accepts no application property keys. It rejects unknown keys and provides no way to pass arbitrary commands, environment variables or mounts.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use lifecycle fresh with the retained OIDC selection | Validation rejects first-time installation because the selected runtime requires an existing Node-RED installation and sign-in setup. |
| Omit settings or healthcheck storage on a retained app | Validation rejects the app because both existing script files must be bound through the settings and healthcheck storage roles. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`node_red-images`](../software-and-runtime.md#registration-software-node-red-images). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`node_red`](../software-and-runtime.md#registration-runtime-profiles-node-red).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `node_red` | `node_red` | Versioned local archive; concrete site binding required |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `node_red` | 1024 | 1 | 256 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab maintains the same managed instance, keeping its declared service and project identities, storage and selected protected inputs. Review changes to software and defaults against the effective configuration; a source update is not permission for data import, credential replacement or a vendor upgrade. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/5d4d178daf0688c9ffc6de7770ee44c2f7d38e7a/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/5d4d178daf0688c9ffc6de7770ee44c2f7d38e7a/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/5d4d178daf0688c9ffc6de7770ee44c2f7d38e7a/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/5d4d178daf0688c9ffc6de7770ee44c2f7d38e7a/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/5d4d178daf0688c9ffc6de7770ee44c2f7d38e7a/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#node_red) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [node_red.yaml](../../../apps/node_red.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"node_red"` |
| <a id="declaration-display-name"></a>`display_name` | `"Node-RED"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web"></a>`interfaces.web` | `object` |
| <a id="declaration-interfaces-web-required"></a>`interfaces.web.required` | `true` |
| <a id="declaration-interfaces-web-accepts"></a>`interfaces.web.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-broker"></a>`interfaces.broker` | `object` |
| <a id="declaration-interfaces-broker-required"></a>`interfaces.broker.required` | `false` |
| <a id="declaration-interfaces-broker-accepts"></a>`interfaces.broker.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web"></a>`listeners.web` | `object` |
| <a id="declaration-listeners-web-service"></a>`listeners.web.service` | `"node_red"` |
| <a id="declaration-listeners-web-namespace"></a>`listeners.web.namespace` | `"host"` |
| <a id="declaration-listeners-web-interface"></a>`listeners.web.interface` | `"web"` |
| <a id="declaration-listeners-web-bind"></a>`listeners.web.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-protocol"></a>`listeners.web.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-port"></a>`listeners.web.port` | `1880` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web"></a>`endpoints.web` | `object` |
| <a id="declaration-endpoints-web-listener"></a>`endpoints.web.listener` | `"web"` |
| <a id="declaration-endpoints-web-protocol"></a>`endpoints.web.protocol` | `"http"` |
| <a id="declaration-endpoints-web-via"></a>`endpoints.web.via` | `"web"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-data"></a>`storage.data` | `object` |
| <a id="declaration-storage-data-target"></a>`storage.data.target` | `"/data"` |
| <a id="declaration-storage-data-read-only"></a>`storage.data.read_only` | `false` |
| <a id="declaration-storage-data-required"></a>`storage.data.required` | `true` |
| <a id="declaration-storage-data-kind"></a>`storage.data.kind` | `"directory"` |
| <a id="declaration-storage-config"></a>`storage.config` | `object` |
| <a id="declaration-storage-config-target"></a>`storage.config.target` | `"/config"` |
| <a id="declaration-storage-config-read-only"></a>`storage.config.read_only` | `false` |
| <a id="declaration-storage-config-required"></a>`storage.config.required` | `true` |
| <a id="declaration-storage-config-kind"></a>`storage.config.kind` | `"directory"` |
| <a id="declaration-storage-settings"></a>`storage.settings` | `object` |
| <a id="declaration-storage-settings-target"></a>`storage.settings.target` | `"/runtime-settings.js"` |
| <a id="declaration-storage-settings-read-only"></a>`storage.settings.read_only` | `true` |
| <a id="declaration-storage-settings-required"></a>`storage.settings.required` | `false` |
| <a id="declaration-storage-settings-kind"></a>`storage.settings.kind` | `"file"` |
| <a id="declaration-storage-healthcheck"></a>`storage.healthcheck` | `object` |
| <a id="declaration-storage-healthcheck-target"></a>`storage.healthcheck.target` | `"/healthcheck.js"` |
| <a id="declaration-storage-healthcheck-read-only"></a>`storage.healthcheck.read_only` | `true` |
| <a id="declaration-storage-healthcheck-required"></a>`storage.healthcheck.required` | `false` |
| <a id="declaration-storage-healthcheck-kind"></a>`storage.healthcheck.kind` | `"file"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-broker"></a>`connections.broker` | `object` |
| <a id="declaration-connections-broker-type"></a>`connections.broker.type` | `"mqtt"` |
| <a id="declaration-connections-broker-required"></a>`connections.broker.required` | `false` |
| <a id="declaration-connections-broker-readiness"></a>`connections.broker.readiness` | `["start"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "node_red-images"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "node_red"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-authentication"></a>`authentication` | `"node-red-retained-oidc"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-api-token"></a>`secrets.api_token` | `object` |
| <a id="declaration-secrets-api-token-required"></a>`secrets.api_token.required` | `false` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-data"></a>`backup.include.data` | `object` |
| <a id="declaration-backup-include-data-category"></a>`backup.include.data.category` | `"state"` |
| <a id="declaration-backup-include-data-capture"></a>`backup.include.data.capture` | `"application-export"` |
| <a id="declaration-backup-include-config"></a>`backup.include.config` | `object` |
| <a id="declaration-backup-include-config-category"></a>`backup.include.config.category` | `"state"` |
| <a id="declaration-backup-include-config-capture"></a>`backup.include.config.capture` | `"application-export"` |
| <a id="declaration-backup-include-settings"></a>`backup.include.settings` | `object` |
| <a id="declaration-backup-include-settings-category"></a>`backup.include.settings.category` | `"configuration"` |
| <a id="declaration-backup-include-settings-capture"></a>`backup.include.settings.capture` | `"files"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `object` |
| <a id="declaration-backup-exclude-healthcheck"></a>`backup.exclude.healthcheck` | `"rebuildable"` |
