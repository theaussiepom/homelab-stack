[Documentation](../../README.md) / [Reference](../README.md)

# PostgreSQL

Configure the supported native PostgreSQL package service and conventional existing cluster data directory.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: postgresql` |
| Adapter | `postgresql` |
| Owned containers | None; native package service |
| Multiple instances | One native PostgreSQL cluster/unit per guest. PostgreSQL + InfluxDB numeric-group namespace conflicts refuse. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [postgresql.yaml](../../../apps/postgresql.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The native data path is the supported conventional cluster path; arbitrary relocation refuses. Explicit client_access base HBA rows are separate from managed-admin and monitoring hooks. Do not add SUPERUSER through a connection reference.

## First installation

The native package/configuration creation path can be selected with `lifecycle: fresh` on a supported new guest. It does not infer application databases, user grants or data import. The creation source compiles; no live database commissioning was performed for this example.

Complete creation-policy source: [examples/catalogue/new-native-databases.yaml](../../../examples/catalogue/new-native-databases.yaml), app `postgresql`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/native-databases.yaml).

```yaml
apps:
  postgresql:
    profile: postgresql
    guest: postgresql
    lifecycle: retained
```

### Practical complete example

Use app `postgresql` in [examples/catalogue/native-databases.yaml](../../../examples/catalogue/native-databases.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

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
| `database` | `postgresql` / `host` | `interface` via `service` | `5432/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `backend` | `tcp` | `database` via `service` |

Listeners bind their declared interface or namespace. An endpoint advertises a value; it does not grant traffic or add a readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/var/lib/postgresql` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

No connection role is declared.

No direct app secret role is declared.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| client_access | Optional list, default empty | At most128 explicit rows. source is {app,interface}; database:all, user:all and method:scram-sha-256 are the only current values. Rows preserve authored order; connections never infer grants. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Relocate data away from the supported conventional native path | Refuses the native data-path capability. |
| Co-locate PostgreSQL and InfluxDB with conflicting fixed numeric groups | Refuses native namespace ownership. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `postgresql`. Runtime selections: `native-postgresql`.

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| Native service | 1792 | Guest allocation | Native service |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates native package/configuration while preserving the conventional cluster data and account owners. Explicit base client-access rows keep their authored order; managed administration and monitoring remain separate selected capabilities. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/proxmox/applications/component_runtime.py).
