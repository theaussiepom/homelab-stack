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
| Multiple instances | Fixed host TCP 8123; put another instance on another guest. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [homeassistant-public.yaml](../../../apps/homeassistant-public.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The config initializer is create-only beneath a proven provider volume with a nonempty app subpath. It does not chown an existing tree or adopt an unowned directory. Optional integrations do not make Node-RED, databases, MQTT, identity or ingress mandatory.

## First installation

Can create a new configuration directory beneath the declared provider volume and start the public image. Home Assistant onboarding and household integrations are separate user setup, not supplied configuration.

Complete creation-policy source: [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml), app `homeassistant`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/new-automation.yaml).

```yaml
apps:
  homeassistant:
    profile: homeassistant-public
    guest: homeassistant-public
    lifecycle: fresh
```

### Practical complete example

Use app `homeassistant` in [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/new-automation.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `home` | No; selected capability can require it | `guest-interface` |
| `database` | No; selected capability can require it | `guest-interface` |
| `metrics` | No; selected capability can require it | `guest-interface` |
| `broker` | No; selected capability can require it | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

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

No direct app secret role is declared.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| mdns | Optional mapping | interface and startup are declared role IDs. Retained only; select homeassistant-mdns runtime, a physical Home role and read-only /startup binding. No NET_ADMIN in the base runtime. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use a pre-existing foreign configuration directory as fresh initialization | Refuses instead of adopting/chowning it. |
| Add the retained mDNS/NET_ADMIN startup capability without its declared support | Refuses the capability/security contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `homeassistant-public-images`. Runtime selections: `container-host`, `homeassistant`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `homeassistant` | `homeassistant_public` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `homeassistant` | 2048 | 2 | 512 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates the same instance with its existing configuration directory. The initializer does not run again against existing data; household/onboarding choices remain in that owned configuration. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/090c9b82ce62eacb8e3ee5cf4901bf552d3b4a43/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#homeassistant-public) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
