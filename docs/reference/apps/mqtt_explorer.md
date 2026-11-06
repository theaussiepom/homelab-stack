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
| Multiple instances | Namespace-aware helper tests cover independent instances with distinct services, project, data, runtime and custody paths/publications. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [mqtt_explorer.yaml](../../../apps/mqtt_explorer.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The broker connection must select TCP port 1883, a saved hostname and either an explicit same-guest managed mqtt-client account or an explicit existing credential. Managed access is read-write-all (all topics). The required HTTP outpost target is the existing Authentik service on port 9000; it is not a newly created identity provider. Only the gateway is published. Saved profile passwords are plaintext at rest; startup log suppression keeps them out of console output. The derived backend alias applies only to Explorer, not managed DNS or the broker.

## First installation

Can create its owned data directory beneath a declared provider volume and prepare the saved profile. Requires an existing broker credential (or the separate supported same-guest managed-account capability), configured outpost and canonical HTTPS route. It does not provision the identity provider.

Complete creation-policy source: [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml), app `browser`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/messaging-radio.yaml).

```yaml
apps:
  browser:
    profile: mqtt_explorer
    guest: browser
    lifecycle: fresh
```

### Practical complete example

Use app `browser` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

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

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

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

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit broker credential/account, saved hostname or outpost | Refuses the selected broker/authentication binding. |
| Bind an unowned existing data/custody directory as fresh | Refuses adoption or mismatched ownership. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

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

## Later deployments

Maintains the same data, saved profile and custody owner. Preserve the selected broker credential/hostname and configured outpost; a source revision cannot silently rotate the saved password or adopt another profile. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/component_runtime.py).
