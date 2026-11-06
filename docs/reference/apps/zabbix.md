[Documentation](../../README.md) / [Reference](../README.md)

# Zabbix

Run the monitoring server and web frontend. Root Zabbix selection owns the generated monitoring credentials and selected guest-agent relationship.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: zabbix` |
| Adapter | `zabbix` |
| Owned containers | `zabbix_server`, `zabbix_web` |
| Multiple instances | Select one root monitoring server explicitly when several exist. Independent same-guest server installations are not qualified here. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [zabbix.yaml](../../../apps/zabbix.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Select root zabbix to activate the existing generated monitoring credential owner. database_password is structurally optional in the profile; the current ordinary caller uses monitoring-owned material and refuses an arbitrary supplied scalar. SAML is optional through the named policy. Local web8081 is the bounded setup path, not a second user-facing exposure.

## First installation

The current ordinary deployment path requires explicit root monitoring, its already configured provider/credential owner and a selected owned PostgreSQL app. The example uses this path; an outside-root password is structurally accepted but does not satisfy the ordinary materializer. Root monitoring does not by itself commission a new fleet or prove schema readiness/administrator login.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/identity-monitoring.yaml).

```yaml
apps:
  monitoring:
    profile: zabbix
    guest: monitoring
    lifecycle: retained
```

### Practical complete example

Use app `monitoring` in [examples/catalogue/identity-monitoring.yaml](../../../examples/catalogue/identity-monitoring.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/identity-monitoring.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `server` | Yes | `guest-interface` |
| `postgresql` | Yes | `guest-interface` |
| `metrics` | No; selected capability can require it | `guest-interface` |
| `management` | No; selected capability can require it | `guest-interface` |
| `private` | Yes | `app-network` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `server` | `zabbix_server` / `app-network` | `wildcard` via `private` | `10051/tcp` | `guest-interface` 10051 via `server` |
| `web` | `zabbix_web` / `app-network` | `wildcard` via `private` | `8080/tcp` | `guest-interface` 8080 via `web` |
| `local_web` | `zabbix_web` / `app-network` | `wildcard` via `private` | `8080/tcp` | `guest-loopback` 8081 |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |
| `server` | `tcp` | `server` via `server` |

Wildcard binding remains inside the declared app network. Only explicit publications map a socket onto the guest. Endpoints do not grant traffic or add readiness waits.

## Storage

No app storage role is declared. Generated private runtime files retain their separate owned paths.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `database` | `postgresql` | Yes | `start` | None |
| `public` | `https` | No | `start` | None |
| `proxmox` | `https` | No | None | None |
| `metrics` | `influxdb` | No | None | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `database_password` | Optional until its capability requires it |

Authentication requirement: `zabbix-saml` (optional), selected by a named site authentication policy.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| database | Required mapping | name and user use [a-z][a-z0-9_]{0,62}, excluding postgres/template0/template1. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Select root monitoring and also supply database_password | Refuses duplicate credential ownership. |
| Bind database to the wrong protocol/port | Refuses the PostgreSQL binding. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `zabbix-images`. Runtime selections: `container-host`, `zabbix`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `zabbix_server` | `zabbix_server` | Immutable registry digest |
| `zabbix_web` | `zabbix_web` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `zabbix_server` | 768 | 1 | 256 |
| `zabbix_web` | 512 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the selected root server, member inventory and ordinary agent configuration while preserving existing monitoring credential/PSK identities and history. Root selection is an explicit monitoring capability, not an instruction to rebuild a fleet. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#zabbix) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
