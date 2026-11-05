[Documentation](../../README.md) / [Reference](../README.md)

# Traefik

Provide the selected HTTP/HTTPS ingress with its declared provider, ACME, trust and routing inputs.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

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

Software selections: `docker`, `curl`, `traefik-images`, `network-tools`. Runtime selections: `container-host`, `traefik`.

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

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/692c87d23a5238d38cbe92b19d71f3d9e5b5797c/proxmox/applications/component_runtime.py).
