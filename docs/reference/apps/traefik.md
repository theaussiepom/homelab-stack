[Documentation](../../README.md) / [Reference](../README.md)

# Traefik

Provide the selected HTTP and HTTPS ingress with its declared provider, ACME, trust and routing inputs.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: traefik` |
| Adapter | `traefik` |
| Owned containers | `traefik` |
| Multiple instances | Each instance must own distinct listener addresses and ports. This page does not establish support for an arbitrary second ingress instance on the same guest. |

This profile runs on Debian LXC on Proxmox. Compilation checks the configuration, and local helper tests check the controller code. Neither check verifies a deployed service.

The complete reusable declaration is [traefik.yaml](../../../apps/traefik.yaml). Select it for an app in your site configuration. Your site supplies the VMID, network-interface address and credentials, and controls permission to deploy. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Although secret roles and properties are structurally conditional, the current supported runtime binds both provider and ACME and requires the proxmox_token role for the provider and the cloudflare_dns_token role for ACME. No Docker socket, arbitrary provider or raw route file override is exposed.

The optional `cloudflare-source` exposure policy adds the framework-owned local middleware and requires `cloudflare_origin_token`. Bind the existing token through a protected secret source; normal CD mounts its bytes as a root-owned read-only file rather than exposing them through Traefik dynamic configuration or API output; its header name and internal allowlist belong to site policy. The plugin checks socket sources, sanitizes visitor headers and bounds address-feed refresh/failure behavior. See the framework [middleware contract](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/policies.md#cloudflare-source-boundary).

Deploy route restrictions before opening the ingress frontend firewall in a later deployment. Validate the actual selected Traefik image, internal access, public TLS and visitor identity after CD; source checks alone do not establish service acceptance.

## First installation

Before installing, prepare its certificate workspace, existing provider reader and DNS API credentials. The profile does not create a Proxmox token, discovery owner, DNS zone or account. The practical example maintains HomeLab-managed ingress; those first-use prerequisites are separate from container creation.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/edge-management.yaml).

```yaml
apps:
  edge:
    profile: traefik
    guest: edge
    lifecycle: retained
```

### Practical complete example

Use app `edge` in [examples/catalogue/edge-management.yaml](../../../examples/catalogue/edge-management.yaml). Check the dependencies and inputs that must already exist before using this example. Entries with `retained` require resources that HomeLab already manages; they cannot import another installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/edge-management.yaml" --check
```

The command should compile every selected guest without reading credentials or contacting a guest, container or device. The integration test also generates each guest’s deployment files and checks its resources, identities, application files and health-check definitions.

The [Cloudflare policy fragment](../../examples/cloudflare-ingress.md) explains its site-owned allowlist and retained-token prerequisites. A real compiler integration combines the exact fragment with the complete edge-management base, a route and explicit backend permissions. It also tests an environment-backed secret through generated workflows; neither variant provisions or rotates the secret.

## Interfaces

A role describes a network connection the app needs. Its [binding](../declaration-records.md#follow-the-selected-field-to-its-effect) selects an interface or network inside the app’s guest. [Interface composition](../../guides/multiple-interfaces.md) explains physical interfaces, guest loopback and private app networks.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `frontend_interface` | Yes | `guest-interface` |
| `management_interface` | No; selected capability can require it | `guest-interface` |
| `backend_interface` | No; selected capability can require it | `guest-interface` |
| `metrics_interface` | No; selected capability can require it | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `http_listener` | `traefik` / `host` | `interface` via `frontend_interface` | `80/tcp` | None; listener remains in its declared namespace |
| `https_listener` | `traefik` / `host` | `interface` via `frontend_interface` | `443/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `http_endpoint` | `http` | `http_listener` via `frontend_interface` |
| `https_endpoint` | `https` | `https_listener` via `frontend_interface` |
| `dashboard_endpoint` | `internal` | `dashboard` (requires selected internal capability) |

Listeners use the declared interface or network namespace. Endpoints tell consumers where to connect; they do not permit traffic or make consumers wait for the service.

## Storage

The target is the path the app uses. Its [site binding](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/storage.md#app-storage-bindings) selects the HomeLab-managed data on the guest. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `certs` | Yes | `/var/traefik/certs` | directory / writable | None |

Bind each storage role to a guest volume and subpath, or to a supported path on the guest’s root filesystem. HomeLab checks existing data without changing its file owner or moving it. Where a profile supports initialization, it creates only a new app subdirectory on a volume whose provider ownership has been verified. It does not initialize an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `provider` | `https` | No | None | None |

The readiness column lists the ordering options you can choose. Set `readiness` explicitly on the site connection to make one app wait for another. Referencing a value alone creates no wait and permits no network traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `cloudflare_dns_token` | Optional until its capability requires it |
| `cloudflare_origin_token` | Required when an exposure selects `cloudflare-source`; preserve its existing value |
| `proxmox_token` | Optional until its capability requires it |

Keep secret values outside Git. A file or environment reference identifies where to obtain a secret; it does not contain the value. An ordinary update cannot silently replace the secret.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter defines the [accepted fields, types and constraints](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| dashboard | Optional boolean, default false | Enables only the internal dashboard endpoint; it does not publish port 8080. An exposure still requires its TLS and authentication policies. |
| provider | Required by current runtime | context and token_id select the existing HTTPS provider. Optional discovery uses local_directory, mirror_directory, owner_sha256 and guests. HomeLab checks that the discovery files still belong to the expected writer before using them. |
| acme | Required by current runtime | Supply email and 1..3 named DNS endpoint references. Optional propagation_timeout_seconds accepts 120..2100. The selected existing DNS credential role is required. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit current provider or ACME inputs or their secret roles | The adapter rejects missing provider or ACME inputs, including their required secret roles, even though profile metadata marks them optional. |
| Expose dashboard without the required authentication middleware | Refuses the dashboard exposure. |

The framework validates these requirements. [Testing guide](../../testing.md) explains which checks validate the source configuration and which require a deployed service.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`traefik-images`](../software-and-runtime.md#registration-software-traefik-images), [`network-tools`](../software-and-runtime.md#registration-software-network-tools). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`traefik`](../software-and-runtime.md#registration-runtime-profiles-traefik).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `traefik` | `traefik` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `traefik` | 512 | 1 | 256 |

These reservations and limits determine whether the workloads fit on a guest. They do not measure how much traffic the service can handle. Guest memory must also leave enough capacity for the operating system’s effective reserve. Security and process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

HomeLab regenerates the selected static configuration and route inputs and reconciles the HomeLab-managed ingress service. Certificate data, provider reader identity and selected protected inputs stay protected; exposure changes do not provision a new DNS zone or API account.

Both `fresh` and `retained` can update an instance that HomeLab already manages. Keep `fresh` after creating an instance with that policy; do not change it after each deployment. `retained` requires an existing HomeLab-managed instance and cannot create one.

### Check and update

Keep the same app, service and project identities, writable storage paths and credential owners. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Before an ordinary update, HomeLab checks the current ownership records, matching deployment state and preserved private inputs. Selecting a profile cannot clear a HOLD left by an unresolved operation or adopt data that HomeLab does not manage.

Follow [Start here](../../start-here.md) to set up the commands, then run the [library checks](../../testing.md). After an authorized deployment, check the service’s endpoint, authentication and selected integrations. Compilation alone does not verify them.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/43db8ff1a15516e101c442004db954c878483554/proxmox/applications/component_runtime.py).

## Backup coverage

See the [storage classifications and capture requirements](../backup-coverage.md#traefik) and [PBS backup guide](../../backup.md). A declared classification does not prove that a backup is installed or that a restore has succeeded.

## Declaration records

These are the complete supplied fields in [traefik.yaml](../../../apps/traefik.yaml), including named role objects. An `object` row introduces the fields below it; `{}` means an explicitly empty mapping. Quoted values are strings, and lists preserve declaration order. These are **profile definition values**. Site apps can change only the inputs their contract accepts. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare this table with the loaded profile definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"traefik"` |
| <a id="declaration-display-name"></a>`display_name` | `"Traefik"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-frontend-interface"></a>`interfaces.frontend_interface` | `object` |
| <a id="declaration-interfaces-frontend-interface-required"></a>`interfaces.frontend_interface.required` | `true` |
| <a id="declaration-interfaces-frontend-interface-accepts"></a>`interfaces.frontend_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management-interface"></a>`interfaces.management_interface` | `object` |
| <a id="declaration-interfaces-management-interface-required"></a>`interfaces.management_interface.required` | `false` |
| <a id="declaration-interfaces-management-interface-accepts"></a>`interfaces.management_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-backend-interface"></a>`interfaces.backend_interface` | `object` |
| <a id="declaration-interfaces-backend-interface-required"></a>`interfaces.backend_interface.required` | `false` |
| <a id="declaration-interfaces-backend-interface-accepts"></a>`interfaces.backend_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-metrics-interface"></a>`interfaces.metrics_interface` | `object` |
| <a id="declaration-interfaces-metrics-interface-required"></a>`interfaces.metrics_interface.required` | `false` |
| <a id="declaration-interfaces-metrics-interface-accepts"></a>`interfaces.metrics_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-http-listener"></a>`listeners.http_listener` | `object` |
| <a id="declaration-listeners-http-listener-service"></a>`listeners.http_listener.service` | `"traefik"` |
| <a id="declaration-listeners-http-listener-namespace"></a>`listeners.http_listener.namespace` | `"host"` |
| <a id="declaration-listeners-http-listener-interface"></a>`listeners.http_listener.interface` | `"frontend_interface"` |
| <a id="declaration-listeners-http-listener-bind"></a>`listeners.http_listener.bind` | `"interface"` |
| <a id="declaration-listeners-http-listener-protocol"></a>`listeners.http_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-http-listener-port"></a>`listeners.http_listener.port` | `80` |
| <a id="declaration-listeners-https-listener"></a>`listeners.https_listener` | `object` |
| <a id="declaration-listeners-https-listener-service"></a>`listeners.https_listener.service` | `"traefik"` |
| <a id="declaration-listeners-https-listener-namespace"></a>`listeners.https_listener.namespace` | `"host"` |
| <a id="declaration-listeners-https-listener-interface"></a>`listeners.https_listener.interface` | `"frontend_interface"` |
| <a id="declaration-listeners-https-listener-bind"></a>`listeners.https_listener.bind` | `"interface"` |
| <a id="declaration-listeners-https-listener-protocol"></a>`listeners.https_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-https-listener-port"></a>`listeners.https_listener.port` | `443` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-http-endpoint"></a>`endpoints.http_endpoint` | `object` |
| <a id="declaration-endpoints-http-endpoint-listener"></a>`endpoints.http_endpoint.listener` | `"http_listener"` |
| <a id="declaration-endpoints-http-endpoint-protocol"></a>`endpoints.http_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-http-endpoint-via"></a>`endpoints.http_endpoint.via` | `"frontend_interface"` |
| <a id="declaration-endpoints-https-endpoint"></a>`endpoints.https_endpoint` | `object` |
| <a id="declaration-endpoints-https-endpoint-listener"></a>`endpoints.https_endpoint.listener` | `"https_listener"` |
| <a id="declaration-endpoints-https-endpoint-protocol"></a>`endpoints.https_endpoint.protocol` | `"https"` |
| <a id="declaration-endpoints-https-endpoint-via"></a>`endpoints.https_endpoint.via` | `"frontend_interface"` |
| <a id="declaration-endpoints-dashboard-endpoint"></a>`endpoints.dashboard_endpoint` | `object` |
| <a id="declaration-endpoints-dashboard-endpoint-internal"></a>`endpoints.dashboard_endpoint.internal` | `"dashboard"` |
| <a id="declaration-properties"></a>`properties` | `object` |
| <a id="declaration-properties-dashboard"></a>`properties.dashboard` | `false` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-certs"></a>`storage.certs` | `object` |
| <a id="declaration-storage-certs-target"></a>`storage.certs.target` | `"/var/traefik/certs"` |
| <a id="declaration-storage-certs-read-only"></a>`storage.certs.read_only` | `false` |
| <a id="declaration-storage-certs-required"></a>`storage.certs.required` | `true` |
| <a id="declaration-storage-certs-kind"></a>`storage.certs.kind` | `"directory"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-provider"></a>`connections.provider` | `object` |
| <a id="declaration-connections-provider-type"></a>`connections.provider.type` | `"https"` |
| <a id="declaration-connections-provider-required"></a>`connections.provider.required` | `false` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "traefik-images", "network-tools"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "traefik"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-cloudflare-dns-token"></a>`secrets.cloudflare_dns_token` | `object` |
| <a id="declaration-secrets-cloudflare-dns-token-required"></a>`secrets.cloudflare_dns_token.required` | `false` |
| <a id="declaration-secrets-cloudflare-origin-token"></a>`secrets.cloudflare_origin_token` | `object` |
| <a id="declaration-secrets-cloudflare-origin-token-required"></a>`secrets.cloudflare_origin_token.required` | `false` |
| <a id="declaration-secrets-proxmox-token"></a>`secrets.proxmox_token` | `object` |
| <a id="declaration-secrets-proxmox-token-required"></a>`secrets.proxmox_token.required` | `false` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-certs"></a>`backup.include.certs` | `object` |
| <a id="declaration-backup-include-certs-category"></a>`backup.include.certs.category` | `"state"` |
| <a id="declaration-backup-include-certs-capture"></a>`backup.include.certs.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
