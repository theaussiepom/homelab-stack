[Documentation](../../README.md) / [Reference](../README.md)

# Traefik

Provide the selected HTTP/HTTPS ingress with its declared provider, ACME, trust and routing inputs.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update) · [Declared fields](#declaration-records)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: traefik` |
| Adapter | `traefik` |
| Owned containers | `traefik` |
| Multiple instances | Listener address/port ownership must be distinct. An arbitrary second same-guest ingress is not qualified here. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [traefik.yaml](../../../apps/traefik.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Although secret roles and properties are structurally conditional, the current supported runtime binds both provider and ACME and requires their proxmox_token/cloudflare_dns_token roles. No Docker socket, arbitrary provider or raw route file override is exposed.

## First installation

Requires its certificate workspace, existing provider reader and DNS API credentials. The profile does not create a Proxmox token, discovery owner, DNS zone or account. The practical example maintains owned ingress; those first-use prerequisites are separate from container creation.

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

Use app `edge` in [examples/catalogue/edge-management.yaml](../../../examples/catalogue/edge-management.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/edge-management.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

The [role binding contract](../declaration-records.md#follow-the-selected-field-to-its-effect) resolves each role inside the selected guest. [Interface composition](../../guides/multiple-interfaces.md) shows physical, loopback and private scope choices.

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `frontend` | Yes | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |
| `backend` | No; selected capability can require it | `guest-interface` |
| `metrics` | No; selected capability can require it | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `http` | `traefik` / `host` | `interface` via `frontend` | `80/tcp` | None; listener remains in its declared namespace |
| `https` | `traefik` / `host` | `interface` via `frontend` | `443/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `http` | `http` | `http` via `frontend` |
| `https` | `https` | `https` via `frontend` |
| `dashboard` | `internal` | `dashboard` (requires selected internal capability) |

Listeners bind their declared interface or namespace. An endpoint advertises a value; it does not grant traffic or add a readiness wait.

## Storage

A role target is an application path; its [site binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings) selects owned guest data. Read [preparation](../../guides/installation.md#prepare-a-consuming-site) before treating an existing directory as usable.

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `certs` | Yes | `/var/traefik/certs` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `provider` | `https` | No | None | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `cloudflare_dns_token` | Optional until its capability requires it |
| `proxmox_token` | Optional until its capability requires it |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

These are instance inputs under `apps.<id>.properties`, distinct from [reusable declaration values](#declaration-records). The selected adapter owns their [closed typed rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md).

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| dashboard | Optional boolean, default false | Enables the internal dashboard endpoint only; no invented port8080 publication. Exposure still needs its required TLS/auth policies. |
| provider | Required by current runtime | context and token_id select the existing HTTPS provider. Optional discovery has local_directory, mirror_directory, owner_sha256 and guests; its existing writer ownership guards remain. |
| acme | Required by current runtime | email and1..3 named DNS endpoint refs. Optional propagation_timeout_seconds:120..2100. The selected existing DNS credential role is required. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit current provider/ACME inputs or their secret roles | Refuses the current adapter floor despite optional profile flags. |
| Expose dashboard without the required authentication middleware | Refuses the dashboard exposure. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: [`docker`](../software-and-runtime.md#registration-software-docker), [`curl`](../software-and-runtime.md#registration-software-curl), [`traefik-images`](../software-and-runtime.md#registration-software-traefik-images), [`network-tools`](../software-and-runtime.md#registration-software-network-tools). Runtime selections: [`container-host`](../software-and-runtime.md#registration-runtime-profiles-container-host), [`traefik`](../software-and-runtime.md#registration-runtime-profiles-traefik).

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `traefik` | `traefik` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `traefik` | 512 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Regenerates the selected static/route inputs and reconciles the owned ingress service. Certificate data, provider reader identity and selected private material stay protected; exposure changes do not provision a new DNS zone or API account. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).

## Declaration records

These are the complete supplied fields in [traefik.yaml](../../../apps/traefik.yaml), including named role objects. `object` introduces its following child rows; `{}` is an explicitly empty mapping. Quoted values are strings, and sequences preserve declaration order. These are **profile definition values**, not an override bag for site apps. [Reading declaration records](../declaration-records.md) explains omission, binding, ownership and the compatible types. The tests compare these authored records to the real loaded definition.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"traefik"` |
| <a id="declaration-display-name"></a>`display_name` | `"Traefik"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-frontend"></a>`interfaces.frontend` | `object` |
| <a id="declaration-interfaces-frontend-required"></a>`interfaces.frontend.required` | `true` |
| <a id="declaration-interfaces-frontend-accepts"></a>`interfaces.frontend.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-management"></a>`interfaces.management` | `object` |
| <a id="declaration-interfaces-management-required"></a>`interfaces.management.required` | `false` |
| <a id="declaration-interfaces-management-accepts"></a>`interfaces.management.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-backend"></a>`interfaces.backend` | `object` |
| <a id="declaration-interfaces-backend-required"></a>`interfaces.backend.required` | `false` |
| <a id="declaration-interfaces-backend-accepts"></a>`interfaces.backend.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-metrics"></a>`interfaces.metrics` | `object` |
| <a id="declaration-interfaces-metrics-required"></a>`interfaces.metrics.required` | `false` |
| <a id="declaration-interfaces-metrics-accepts"></a>`interfaces.metrics.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-http"></a>`listeners.http` | `object` |
| <a id="declaration-listeners-http-service"></a>`listeners.http.service` | `"traefik"` |
| <a id="declaration-listeners-http-namespace"></a>`listeners.http.namespace` | `"host"` |
| <a id="declaration-listeners-http-interface"></a>`listeners.http.interface` | `"frontend"` |
| <a id="declaration-listeners-http-bind"></a>`listeners.http.bind` | `"interface"` |
| <a id="declaration-listeners-http-protocol"></a>`listeners.http.protocol` | `"tcp"` |
| <a id="declaration-listeners-http-port"></a>`listeners.http.port` | `80` |
| <a id="declaration-listeners-https"></a>`listeners.https` | `object` |
| <a id="declaration-listeners-https-service"></a>`listeners.https.service` | `"traefik"` |
| <a id="declaration-listeners-https-namespace"></a>`listeners.https.namespace` | `"host"` |
| <a id="declaration-listeners-https-interface"></a>`listeners.https.interface` | `"frontend"` |
| <a id="declaration-listeners-https-bind"></a>`listeners.https.bind` | `"interface"` |
| <a id="declaration-listeners-https-protocol"></a>`listeners.https.protocol` | `"tcp"` |
| <a id="declaration-listeners-https-port"></a>`listeners.https.port` | `443` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-http"></a>`endpoints.http` | `object` |
| <a id="declaration-endpoints-http-listener"></a>`endpoints.http.listener` | `"http"` |
| <a id="declaration-endpoints-http-protocol"></a>`endpoints.http.protocol` | `"http"` |
| <a id="declaration-endpoints-http-via"></a>`endpoints.http.via` | `"frontend"` |
| <a id="declaration-endpoints-https"></a>`endpoints.https` | `object` |
| <a id="declaration-endpoints-https-listener"></a>`endpoints.https.listener` | `"https"` |
| <a id="declaration-endpoints-https-protocol"></a>`endpoints.https.protocol` | `"https"` |
| <a id="declaration-endpoints-https-via"></a>`endpoints.https.via` | `"frontend"` |
| <a id="declaration-endpoints-dashboard"></a>`endpoints.dashboard` | `object` |
| <a id="declaration-endpoints-dashboard-internal"></a>`endpoints.dashboard.internal` | `"dashboard"` |
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
| <a id="declaration-secrets-proxmox-token"></a>`secrets.proxmox_token` | `object` |
| <a id="declaration-secrets-proxmox-token-required"></a>`secrets.proxmox_token.required` | `false` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
