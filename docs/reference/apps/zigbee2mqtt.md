[Documentation](../../README.md) / [Reference](../README.md)

# Zigbee2MQTT

Run the existing Zigbee network through its registered serial coordinator without commissioning or restoring a network.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: zigbee2mqtt` |
| Adapter | `zigbee2mqtt` |
| Owned containers | `zigbee2mqtt` |
| Multiple instances | One selected serial coordinator per guest. Fixed settings/identity sidecar leaves are preserved. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [zigbee2mqtt.yaml](../../../apps/zigbee2mqtt.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The coordinator device is an explicit registered serial capability with its own host/provider checks. Fixed network settings/receipt leaves remain in force; changing an app label does not initialize or rename the Zigbee network.

## First installation

New coordinator/network commissioning is not implemented. The example requires an already registered coordinator and an already HomeLab-managed Zigbee network/data directory; it does not reset or initialize the radio.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/messaging-radio.yaml).

```yaml
apps:
  radio:
    profile: zigbee2mqtt
    guest: radio
    lifecycle: retained
```

### Practical complete example

Use app `radio` in [examples/catalogue/messaging-radio.yaml](../../../examples/catalogue/messaging-radio.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `broker` | Yes | `guest-interface` |
| `private` | Yes | `app-network` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `zigbee2mqtt` / `app-network` | `wildcard` via `private` | `8099/tcp` | `guest-interface` 8099 via `web` |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/app/data` | directory / writable | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | Yes | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

| Device role | Type | Required |
| --- | --- | --- |
| `coordinator` | `serial` | Yes |

## Application properties

| Property | Presence / default | Meaning / constraint |
| --- | --- | --- |
| adapter | Required string | Lowercase safe adapter ID [a-z][a-z0-9_-]{0,62}. |
| mqtt_base_topic | Required string | 1..128 characters: initial letter/digit followed by letters/digits/slash/underscore/hyphen. |

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use lifecycle fresh or omit the registered coordinator | Refuses unsupported commissioning/device ownership. |
| Use an arbitrary serial path instead of a stable usb- by-id path | Refuses the current coordinator helper contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `zigbee2mqtt-images`, `yaml-parser`. Runtime selections: `container-host`, `zigbee2mqtt`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `zigbee2mqtt` | `zigbee2mqtt` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `zigbee2mqtt` | 512 | 2 | 128 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the existing coordinator/network identity and data. Preserve the registered by-id device, adapter, network receipt and broker relationship; ordinary deployment never commissions a new radio. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/e168b25019dc4ceff0f48821925c8c519f2d63c5/proxmox/applications/component_runtime.py).
