[Documentation](../../README.md) / [Reference](../README.md)

# Node-RED

Run an existing Node-RED installation with its explicit custom archive, settings/health wrappers and retained OIDC strategy.

[Choose](#choose-this-profile) · [Interfaces](#interfaces) · [Listeners](#listeners-and-endpoints) · [Storage](#storage) · [Inputs](#connections-accounts-and-private-inputs) · [Properties](#application-properties) · [Software](#software-and-resource-policy) · [Update](#check-and-update)

## Choose this profile

| Setting | Value |
| --- | --- |
| Site selection | `apps.<instance>.profile: node_red` |
| Adapter | `node_red` |
| Owned containers | `node_red` |
| Multiple instances | Fixed host TCP 1880; use separate guests for independent instances. |

The platform is Debian LXC on Proxmox. Compile/render and local helper tests are source/controller evidence; deployed-service verification is separate.

The complete reusable declaration is [node_red.yaml](../../../apps/node_red.yaml). Select it in a site app; the profile itself contains no VMID, NIC address, credential or deployment authority. See [Compose a site](../../guides/compose-a-site.md).

## Application requirements

The optional settings and healthcheck roles become mandatory in retained mode. The node-red-retained-oidc policy is required. Existing custom nodes, flows, secrets and strategy are neither installed nor migrated implicitly. api_token is optional until the selected API capability requires it.

## First installation

Not implemented by this retained profile: it cannot create a brand-new public Node-RED setup or its existing OIDC strategy/settings. Choose [node_red-public](node_red-public.md) for the supported new public-image path.

## Minimal usage

The following is an **app-selection fragment**, not a complete site. Its instance ID and values come from the [complete synthetic composition](../../../examples/catalogue/existing-automation.yaml).

```yaml
apps:
  node_red:
    profile: node_red
    guest: node-red
    lifecycle: retained
```

### Practical complete example

Use app `node_red` in [examples/catalogue/existing-automation.yaml](../../../examples/catalogue/existing-automation.yaml). Read every selected dependency and prepared-input requirement in that file. Retained entries require already HomeLab-managed resources; the source cannot import an arbitrary installation.

After [the source-only setup](../../guides/first-configuration.md) defines STACK, FRAMEWORK and PYTHON:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$STACK/examples/catalogue/existing-automation.yaml" --check
```

Expected: all selected component guests compile offline. No credential contents, guest, container or device is contacted. The maintained integration also lowers every selected packet, including resources, identity, generated files and health contracts.

## Interfaces

| Role | Required in profile | Accepted binding scopes |
| --- | --- | --- |
| `web` | Yes | `guest-interface` |
| `broker` | No; selected capability can require it | `guest-interface` |

A physical role binds `{interface: NIC_ID}`; loopback and app-network use explicit scopes. Roles name requirements, not additional NICs. See [Multiple interfaces](../../guides/multiple-interfaces.md).

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
| `data` | Yes | `/data` | directory / writable | None |
| `config` | Yes | `/config` | directory / writable | None |
| `settings` | Conditional / optional | `/runtime-settings.js` | file / read-only | None |
| `healthcheck` | Conditional / optional | `/healthcheck.js` | file / read-only | None |

Bind roles to explicit guest volumes/subpaths or supported root data paths. Retained data is verified, not chowned or relocated. An initializer applies only to a newly created leaf beneath a proved provider volume, never an existing directory.

## Connections, accounts and private inputs

| Connection role | Type | Required | Allowed explicit readiness | Allowed managed accounts |
| --- | --- | --- | --- | --- |
| `broker` | `mqtt` | No | `start` | None |

The readiness column lists permitted choices, **not an automatic dependency**. The site selects `readiness` on the connection explicitly. Value links alone do not wait or grant traffic. See [Connect apps](../../guides/connect-apps.md).

| App secret role | Requirement |
| --- | --- |
| `api_token` | Optional until its capability requires it |

Authentication requirement: `node-red-retained-oidc` (required), selected by a named site authentication policy.

Secrets remain outside Git. File/environment references are metadata. Private role material cannot rotate implicitly during an ordinary update.

## Application properties

No application property keys are accepted for this adapter. Unknown keys refuse; there is no command/environment/mount override bag.

## Invalid cases

| Invalid change | Intended result |
| --- | --- |
| Use lifecycle fresh with the retained OIDC selection | Refuses the incompatible fresh runtime. |
| Omit settings or healthcheck storage on a retained app | Refuses the exact retained wrapper storage contract. |

The owning framework validates these contracts; the library does not implement another validator. [Tests](../../testing.md) distinguish source integration from target acceptance.

## Software and resource policy

Software selections: `docker`, `curl`, `node_red-images`. Runtime selections: `container-host`, `node_red`.

| Image role | Authoritative catalogue ID | Selection policy |
| --- | --- | --- |
| `node_red` | `node_red` | Versioned local archive; concrete site binding required |

| Owned service | Memory MiB | CPU limit | PID limit |
| --- | --- | --- | --- |
| `node_red` | 1024 | 1 | 256 |

These are admission reservations/limits, not measured load capacity. Guest memory must also leave the effective OS reserve. Security/process defaults and package versions are listed once in [Software and runtime](../software-and-runtime.md); [templates](../templates.md) define guest defaults.

## Later deployments

Maintains the same managed instance, keeping its declared service/project identities, storage and selected protected inputs. Review software/default changes against the effective configuration; a source update is not permission for data import, credential replacement or a vendor upgrade. This profile requires `lifecycle: retained`: it updates an already HomeLab-managed instance and refuses creation or import.

### Check and update

Keep stable app/service/project, writable storage and credential identities. Read [Images and updates](../../guides/images-and-updates.md) before changing software and [Troubleshooting](../../troubleshooting.md) for a refusal. Ordinary updates require genuine current receipts, matching state and sealed private material; a profile choice does not release a HOLD or adopt data.

Use the fully defined commands in [Start here](../../start-here.md), then the [library test gate](../../testing.md). After separately authorized deployment, verify the actual selected endpoint, authentication and integration; source success is not a service check.

Framework: [lifecycle](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/lifecycle.md), [property types](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/app-properties.md), [app bindings](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/apps.md) and [support](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/docs/reference/support.md). Adapter trace: [runtime source](https://github.com/theaussiepom/homelab/blob/dcba8641270378305fa53a6979ca93f1b7fa794c/proxmox/applications/component_runtime.py).

## Backup coverage

See the [explicit storage dispositions and capture requirements](../backup-coverage.md#node_red) and [PBS client preparation](../../backup.md). Classification does not establish an installed backup or a successful restore.
