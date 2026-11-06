[Documentation](../../README.md) / [Reference](../README.md)

# Home Assistant

Run Home Assistant with an explicitly supplied custom image archive and existing configuration. Recorder, metrics and MQTT are independent optional integrations.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: homeassistant` |
| Adapter | `homeassistant` |
| Owned containers | `homeassistant` |
| Multiple instances | Fixed host TCP 8123 prevents two identical listeners on one guest. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [homeassistant.yaml](../../../apps/homeassistant.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The custom archive needs concrete local_id/archive/archive_sha256 site bindings. Zero-valued public catalogue entries are unresolved sentinels, not usable image identities. The retained mDNS startup capability is explicit; hardware access is not inferred.

## First installation

This selection requires the declared custom archive and prepared Home Assistant configuration. It does not build that archive or provide a brand-new custom installation. For the supported public-image creation path, choose [homeassistant-public](homeassistant-public.md).

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/existing-automation.yaml).

```yaml
apps:
  homeassistant:
    profile: homeassistant
    guest: homeassistant
    lifecycle: retained
```

### Practical complete example

Use app `homeassistant` in [examples/catalogue/existing-automation.yaml](../../../examples/catalogue/existing-automation.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/existing-automation.yaml" --check
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
| `config` | Yes | `/config` | directory / writable | None |
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
| Select mDNS without its physical role/startup binding and explicit runtime requirement | Refuses the selected capability. |
| Replace the retained archive with the public variant silently | Changes software authority; no fallback is implemented. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `homeassistant-images`. Runtime selections: `container-host`, `homeassistant`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `homeassistant` | `homeassistant` | Versioned local archive; concrete site binding required |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `homeassistant` | 2048 | 2 | 512 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the existing configuration and explicit custom archive binding. Preserve selected integrations and optional mDNS/startup requirements; a profile update does not rebuild the archive or replace private configuration. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#homeassistant) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
