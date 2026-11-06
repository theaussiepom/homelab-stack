[Documentation](../../README.md) / [Reference](../README.md)

# Node-RED — `node_red-public`

Start Node-RED with the declared official public image and its standard data directory, independently of Home Assistant.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: node_red-public` |
| Adapter | `node_red` |
| Owned containers | `node_red` |
| Multiple instances | Fixed host TCP 1880; use separate guests. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [node_red-public.yaml](../../../apps/node_red-public.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

No retained OIDC strategy or wrapper is selected by this variant. Choose access/authentication policy deliberately before a real exposure; this is not a silent auth downgrade for an existing instance.

## First installation

Can create a new data directory beneath the declared provider volume and start the public image. This variant does not install the retained OIDC wrapper or import existing flows/credentials.

Complete creation-policy source: [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml), app `node_red`. It must pass both resolution and packet generation; it is not proof of a deployed service.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/new-automation.yaml).

```yaml
apps:
  node_red:
    profile: node_red-public
    guest: node_red-public
    lifecycle: fresh
```

### Practical complete example

Use app `node_red` in [examples/catalogue/new-automation.yaml](../../../examples/catalogue/new-automation.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/new-automation.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `broker` | No; selected capability can require it | `guest-interface` |

Bind each selected role to a named guest NIC with `{interface: NIC_ID}`. A role names an application requirement; it does not create another NIC. See [Multiple interfaces](../../guides/multiple-interfaces.md).

## Listeners and endpoints

| Listener | Owned service / namespace | Bind | Container/native socket | Publication |
| --- | --- | --- | --- | --- |
| `web` | `node_red` / `host` | `wildcard` via `web` | `1880/tcp` | None; listener remains in its declared namespace |

| Endpoint | Protocol | Resolves through |
| --- | --- | --- |
| `web` | `http` | `web` via `web` |

A wildcard host listener can cover more than the advertised NIC. An endpoint is a value; it is not a firewall rule, HTTPS route or readiness wait.

## Storage

| Role | Required | Target | Type / access | Fresh initializer |
| --- | --- | --- | --- | --- |
| `data` | Yes | `/data` | directory / writable | Create-only 1000:1000 mode 0700 |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

No direct app secret role is declared.

## Application properties

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Select the retained authentication strategy/settings wrapper | Refuses the fresh public runtime contract. |
| Reuse a foreign data directory as an initializer | Refuses ownership/adoption. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `node_red-public-images`. Runtime selections: `container-host`, `node_red`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `node_red` | `node_red_public` | Immutable registry digest |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `node_red` | 1024 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Updates the same instance with its existing data/flows. It does not substitute the retained OIDC profile or import another installation’s credentials. Both `fresh` and `retained` support ordinary owned updates. Keep `fresh` on an instance created through that policy; it is not a per-deployment toggle. `retained` refuses creation and requires an already HomeLab-managed instance.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/4d926e82869f5fc2b497577f341ff82c3e7f619b/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/4d926e82869f5fc2b497577f341ff82c3e7f619b/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/4d926e82869f5fc2b497577f341ff82c3e7f619b/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/4d926e82869f5fc2b497577f341ff82c3e7f619b/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/4d926e82869f5fc2b497577f341ff82c3e7f619b/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#node_red-public) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
