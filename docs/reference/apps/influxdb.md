[Documentation](../../README.md) / [Reference](../README.md)

# InfluxDB

Configure the supported native InfluxDB package service and its declared existing data path.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: influxdb` |
| Adapter | `influxdb` |
| Owned containers | None; native package service |
| Multiple instances | One native InfluxDB unit per guest. PostgreSQL + InfluxDB numeric-group namespace conflicts refuse. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [influxdb.yaml](../../../apps/influxdb.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The typed data role drives the existing native configuration. Organization, token and bucket setup are not inferred from a listener or profile name.

## First installation

The native package/configuration creation path can be selected with `lifecycle: fresh` on a supported new guest. It does not infer an organization, bucket, token or data import. Target commissioning and usable application credentials need their own verification.

Complete creation-policy source: [examples/catalogue/new-native-databases.yaml](../../../examples/catalogue/new-native-databases.yaml), app `influxdb`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/native-databases.yaml).

```yaml
apps:
  influxdb:
    profile: influxdb
    guest: influxdb
    lifecycle: retained
```

### Practical complete example

Use app `influxdb` in [examples/catalogue/native-databases.yaml](../../../examples/catalogue/native-databases.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/native-databases.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `service` | Yes | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `influxdb` / `host` | `interface` via `service` | `8086/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `service` |

Listeners bind their declared interface or namespace. An endpoint advertises a value; it does not grant traffic or add a readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/influxdb` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Co-locate with conflicting native group ownership | Refuses native namespace collision. |
| Supply arbitrary raw native config text as app properties | Refuses the closed typed property contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `influxdb`. Runtime selections: `native-influxdb`.

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 1792 | Guest allocation | Native service |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates the declared native package/configuration while preserving the selected data directory. Existing organization, bucket and token ownership remains separate; a public configuration edit does not recreate them. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/proxmox/applications/component_runtime.py).
