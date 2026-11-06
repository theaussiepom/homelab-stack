[Documentation](../../README.md) / [Reference](../README.md)

# Music Assistant

Run an existing Music Assistant installation without resetting its provider/account settings or data.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: music_assistant` |
| Adapter | `music_assistant` |
| Owned containers | `music_assistant` |
| Multiple instances | Fixed host player/web sockets prevent an identical co-located instance; use another guest. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [music_assistant.yaml](../../../apps/music_assistant.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The `public` role is optional in profile metadata, but current packet generation requires its explicit HTTPS connection and canonical origin for the owned route check. The connection source must be the physical web role. Independent selection therefore still needs the declared ingress relationship.

Player/web addresses derive from the selected web role. The existing helper checks settings through the selected data root before startup; it does not reset streaming providers. The declared latest image policy is intentional and remains distinct from digest-pinned profiles.

## First installation

Brand-new Music Assistant commissioning is not implemented by this retained profile. The example requires an already HomeLab-managed installation and its valid existing settings/data.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/music.yaml).

```yaml
apps:
  music:
    profile: music_assistant
    guest: media
    lifecycle: retained
```

### Practical complete example

Use app `music` in [examples/catalogue/music.yaml](../../../examples/catalogue/music.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/music.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `music_assistant` / `host` | `interface` via `web` | `8095/tcp` | None; listener remains in its declared namespace |
| `stream` | `music_assistant` / `host` | `interface` via `web` | `8097/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |
| `stream` | `http` | `stream` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/data` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `public` | `https` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit explicit public HTTPS connection or canonical origin | Real packet health generation refuses. |
| Bind the HTTPS source to a different address than the web role | Refuses the source-address requirement. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `music_assistant-images`. Runtime selections: `container-host`, `music_assistant`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `music_assistant` | `music_assistant` | Declared floating latest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `music_assistant` | 1536 | 2 | 512 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the existing settings/data and verifies the core listener, stream listener and selected HTTPS route. It does not commission providers, replace authentication or repair vendor state. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#music_assistant) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
