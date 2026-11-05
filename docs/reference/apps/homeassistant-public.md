[Documentation](../../README.md) / [Reference](../README.md)

# Home Assistant — `homeassistant-public`

Start an independent Home Assistant using the declared official public image and create-only configuration directory.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: homeassistant-public` |
| Adapter | `homeassistant` |
| Owned containers | `homeassistant` |
| Fresh / update | Fresh source, directory creation, caller and onboarding-probe paths are tested. This is not a claim of a completed native first install. Retained repeats preserve the owned config. |
| Multiple instances | Fixed host TCP 8123; put another instance on another guest. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [homeassistant-public.yaml](../../../apps/homeassistant-public.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The config initializer is create-only beneath a proven provider volume with a nonempty app subpath. It does not chown an existing tree or adopt an unowned directory. Optional integrations do not make Node-RED, databases, MQTT, identity or ingress mandatory.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `home` | No; selected capability can require it | `guest-interface` |
| `database` | No; selected capability can require it | `guest-interface` |
| `metrics` | No; selected capability can require it | `guest-interface` |
| `broker` | No; selected capability can require it | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `homeassistant` / `host` | `wildcard` via `web` | `8123/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `config` | Yes | `/config` | directory / writable | Create-only 0:0 mode 0700 |
| `media` | Conditional / optional | `/media` | directory / writable | None |
| `community` | Conditional / optional | `/hacsfiles` | directory / writable | None |
| `startup` | Conditional / optional | `/startup` | directory / read-only | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `recorder` | `mariadb` | No | `start` | None |
| `metrics` | `influxdb` | No | `start` | None |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| mdns | Optional mapping | interface and startup are declared role IDs. Retained only; select homeassistant-mdns runtime, a physical Home role and read-only /startup binding. No NET_ADMIN in the base runtime. |

## Software and resource policy

Software selections: `docker`, `curl`, `homeassistant-public-images`. Runtime selections: `container-host`, `homeassistant`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `homeassistant` | `homeassistant_public` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `homeassistant` | 2048 | 2 | 512 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
