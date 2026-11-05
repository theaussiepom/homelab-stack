[Documentation](../../README.md) / [Reference](../README.md)

# MQTT Explorer

Provide MQTT Explorer behind its owned file-only gateway, with a saved broker connection and a required existing authentication outpost.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: mqtt_explorer` |
| Adapter | `mqtt_explorer` |
| Owned containers | `mqtt_explorer`, `explorer_gateway` |
| Fresh / update | Fresh data creation is accepted only with the same-phase created-directory proof or an existing genuine owner receipt. Saved profiles and unrelated settings are preserved; no adoption or password rotation. |
| Multiple instances | Namespace-aware helper tests cover independent instances with distinct services, project, data, runtime and custody paths/publications. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [mqtt_explorer.yaml](../../../apps/mqtt_explorer.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The broker connection must select TCP port 1883, a saved hostname and either an explicit same-guest managed mqtt-client account or an explicit existing credential. Managed access is read-write-all (all topics). The required HTTP outpost target is the existing Authentik service on port 9000; it is not a newly created identity provider. Only the gateway is published. Saved profile passwords are plaintext at rest; startup log suppression keeps them out of console output. The derived backend alias applies only to Explorer, not managed DNS or the broker.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |
| `broker` | Yes | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `explorer_gateway` / `app-network` | `wildcard` via `private` | `4180/tcp` | `guest-interface` 80 via `web` |
| `explorer` | `mqtt_explorer` / `app-network` | `wildcard` via `private` | `3000/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/app/data` | directory / writable | Create-only 1001:1001 mode 0700 |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | Yes | `start` | `mqtt-client` |
| `outpost` | `http` | Yes | None | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct `app.secrets` role is declared; selected authentication, account or connection capabilities may have their own private inputs.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update. Saved GUI credentials, where used, are plaintext at rest in their protected workspace.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| connection_name | Required string | Nonempty single line, at most 100 characters. The broker hostname comes from the selected connection; the canonical HTTPS origin is explicit. |

## Software and resource policy

Software selections: `docker`, `curl`, `mqtt_explorer-images`. Runtime selections: `container-host`, `mqtt_explorer`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `mqtt_explorer` | `mqtt_explorer` | Immutable registry digest |
| `explorer_gateway` | `traefik` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `mqtt_explorer` | 256 | 1 | 128 |
| `explorer_gateway` | 128 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Gateway and saved-profile behavior

Every app and Socket.IO request passes through the named existing outpost; callback routing goes to that outpost separately. The file-only gateway has no ACME, dashboard/API, Docker socket or infrastructure provider. No identity-provider registration is performed.

The version1 saved profile preserves unrelated settings and profiles. No fixed client ID, autoconnect, public demo broker or AI key is chosen. Managed account creation verifies the parent-mounted password file before atomic addition/HUP; ordinary GUI changes target only owned services. Health checks the app/gateway/backend alias, while actual sign-in, read/publish and existing-client continuity are later service acceptance checks.

## Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/93f22ea190110d1952ac6d05c7db4a4df44073c4/proxmox/applications/component_runtime.py).
