[Documentation](../../README.md) / [Reference](../README.md)

# Node-RED

Run an existing Node-RED installation with its explicit custom archive, settings/health wrappers and retained OIDC strategy.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: node_red` |
| Adapter | `node_red` |
| Owned containers | `node_red` |
| Fresh / update | Retained path requires all four data/config/settings/healthcheck bindings and the selected OIDC policy, even where a role is structurally optional. It is not the public-image first-install path. |
| Multiple instances | Fixed host TCP 1880; use separate guests for independent instances. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [node_red.yaml](../../../apps/node_red.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The optional settings and healthcheck roles become mandatory in retained mode. The node-red-retained-oidc policy is required. Existing custom nodes, flows, secrets and strategy are neither installed nor migrated implicitly. api_token is optional until the selected API capability requires it.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `broker` | No; selected capability can require it | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `node_red` / `host` | `wildcard` via `web` | `1880/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/data` | directory / writable | None |
| `config` | Yes | `/config` | directory / writable | None |
| `settings` | Conditional / optional | `/runtime-settings.js` | file / read-only | None |
| `healthcheck` | Conditional / optional | `/healthcheck.js` | file / read-only | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `api_token` | Optional until its capability requires it |

Authentication requirement: `node-red-retained-oidc` (required), selected by a named site authentication policy.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Software and resource policy

Software selections: `docker`, `curl`, `node_red-images`. Runtime selections: `container-host`, `node_red`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `node_red` | `node_red` | Versioned local archive; concrete site binding required |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `node_red` | 1024 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
