[Documentation](../../README.md) / [Reference](../README.md)

# WiNet

Run the independent WiNet poller with explicit inverter, MQTT and private options bindings. It does not require Zigbee2MQTT.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: winet` |
| Adapter | `winet` |
| Owned containers | `winet` |
| Multiple instances | Independent of Zigbee; same-guest duplicate WiNet operation is not qualified here. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [winet.yaml](../../../apps/winet.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

Private options are supplied by the selected options role and validated against inverter/MQTT metadata. Existing inverter and broker credentials stay inside that protected record; neither is copied into Git.

## First installation

Requires an already configured inverter and valid protected vendor options/credentials. The profile can reconcile its container, but does not commission an inverter or generate those credentials. The example uses an existing managed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/messaging-radio.yaml).

```yaml
apps:
  telemetry:
    profile: winet
    guest: telemetry
    lifecycle: retained
```

### Practical complete example

Use app `telemetry` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `broker` | Yes | `guest-interface` |
| `inverter` | Yes | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

No listener is declared by this profile.

No endpoint is advertised.

## Storage

No app storage role is declared. Generated private runtime files retain their separate owned paths.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | Yes | `start` | None |
| `inverter` | `https` | Yes | None | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `options` | Required |

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| mqtt_prefix | Required string | 1..128 characters: initial letter/digit followed by letters/digits/slash/underscore/hyphen. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Omit the protected options role | Refuses the selected private input. |
| Use a non-443/non-HTTPS inverter or malformed discovery prefix | Refuses the finite endpoint/property contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `winet-images`. Runtime selections: `container-host`, `winet`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `winet` | `winet` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `winet` | 256 | 1 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Reconciles the same service against its existing inverter/options owner and broker relationship. It does not reconfigure the physical inverter, replace vendor credentials or commission another device. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#winet) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
