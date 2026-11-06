[Documentation](../../README.md) / [Reference](../README.md)

# Bitwarden

Run the existing Bitwarden Lite vault against its selected MariaDB database, preserving installation material and numeric data ownership.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: bitwarden` |
| Adapter | `bitwarden` |
| Owned containers | `bitwarden` |
| Multiple instances | Distinct storage/project/service identities are required; same-guest multi-instance operation is not qualified here. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [bitwarden.yaml](../../../apps/bitwarden.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## First installation

Not implemented by this profile: it cannot create a brand-new vault. The example requires an already HomeLab-managed vault, database, installation keys and data.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/vault.yaml).

```yaml
apps:
  vault:
    profile: bitwarden
    guest: vault
    lifecycle: retained
```

### Practical complete example

Use app `vault` in [examples/catalogue/vault.yaml](../../../examples/catalogue/vault.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/vault.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `database` | Yes | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |
| `private` | Yes | `app-network` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `bitwarden` / `app-network` | `wildcard` via `private` | `8080/tcp` | `guest-interface` 8080 via `web` |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/etc/bitwarden` | directory / writable | None |
| `logs` | Yes | `/var/log/bitwarden` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `mariadb` | Yes | `configure`, `start` | None |
| `public` | `https` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `runtime_environment` | Required |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| issuer | Required mapping | protocol is http or https; domain names a site domains entry. This metadata is separate from the HTTPS app origin. |
| database_name | Required string | Nonempty letters/digits/underscore, matching the sealed runtime environment and selected MariaDB database. |
| data_uid / data_gid | Required positive integers | 1..2147483647, matching existing numeric data ownership and private environment values. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Select lifecycle fresh | Refuses: new-vault creation is unsupported. |
| Supply a floating/local image or an authored environment checksum | Refuses the immutable-image/closed-property contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `bitwarden-images`, `mariadb-client`. Runtime selections: `container-host`, `bitwarden`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `bitwarden` | `bitwarden` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `bitwarden` | 1536 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains an already HomeLab-managed vault, preserving its database, installation keys, data and selected protected runtime environment. Software/image changes follow the normal immutable manifest policy; no vault upgrade or credential rotation is implied. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#bitwarden) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
