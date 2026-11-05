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
| Fresh / update | The current runtime binder requires explicit provider and ACME capabilities and their inputs. Source/rendering is not certificate issuance, provider permission or externally verified TLS. |
| Multiple instances | Listener address/port ownership must be distinct. An arbitrary second same-guest ingress is not qualified here. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [traefik.yaml](../../../apps/traefik.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Although secret roles and properties are structurally conditional, the current supported runtime binds both provider and ACME and requires their proxmox_token/cloudflare_dns_token roles. No Docker socket, arbitrary provider or raw route file override is exposed.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `frontend` | Yes | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |
| `backend` | No; selected capability can require it | `guest-interface` |
| `metrics` | No; selected capability can require it | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

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

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

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

## Software and resource policy

Software selections: `docker`, `curl`, `traefik-images`, `network-tools`. Runtime selections: `container-host`, `traefik`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `traefik` | `traefik` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `traefik` | 512 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
