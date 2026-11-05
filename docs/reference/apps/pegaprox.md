[Documentation](../../README.md) / [Reference](../README.md)

# PegaProx

Run PegaProx with the explicitly selected database key and owned data/config/log directories.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: pegaprox` |
| Adapter | `pegaprox` |
| Owned containers | `pegaprox` |
| Multiple instances | Distinct publications, runtime/key leaves and writable paths are required; no broad duplicate-instance claim is made. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [pegaprox.yaml](../../../apps/pegaprox.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The selected runtime requires at least 512 MiB OS reserve. The effective guest reserve is max(guest reserve, selected runtime requirement); it is placement policy, not measured load. The management endpoint address retains the private/benchmark-only floor.

## First installation

Requires prepared data/config/logs, its existing database key and completed administrator setup. The profile does not create a new application administrator or adopt an unrelated manager. The practical example maintains an already HomeLab-managed instance.

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

Use app `manager` in [examples/catalogue/edge-management.yaml](../../../examples/catalogue/edge-management.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/edge-management.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `pegaprox` / `app-network` | `wildcard` via `private` | `5000/tcp` | `guest-interface` 5000 via `web` |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/app/config` | directory / writable | None |
| `logs` | Yes | `/app/logs` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Required | Type | Meaning |
| --- | --- | --- | --- |
| `proxmox` | No | `https` | Selected hypervisor API; bind its endpoint and source interface explicitly. |

The complete example binds `manager_provider` to the existing external Proxmox
endpoint through the app's `web` interface and admits its API port in the guest
policy. The connection makes source traffic validation check that dependency;
it does not configure a retained PegaProx cluster or add a readiness/deployment
dependency. A site with no configured cluster can omit this role. Do not open
SSH, console or other ports just because an API connection is selected.

| App secret role | Requirement |
| --- | --- |
| `database_key` | Required |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| trusted_proxy | Required mapping | {app,interface} selecting a physical interface of the named Traefik app. It must be a distinct private address, not a hostname or arbitrary trust range. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use a public/loopback/link-local management listener | Refuses the existing private management-address floor. |
| Name an arbitrary address as trusted_proxy | Refuses; select the actual Traefik physical role. |
| Select a hypervisor connection without the corresponding outbound API policy | Refuses traffic validation. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `pegaprox-images`. Runtime selections: `container-host`, `pegaprox`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `pegaprox` | `pegaprox` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `pegaprox` | 1536 | 2 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the configured manager using the same data, config, logs and database key. Existing administrator/setup state stays protected; changing a trusted-proxy binding does not initialize a new manager. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/proxmox/applications/component_runtime.py).
