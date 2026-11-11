# Guest templates

[Documentation index](../README.md) · [Reference index](README.md)

Choose a template for reusable guest defaults. A site still supplies the provider context, lifecycle policy, VMID, hostname, template image and root storage. It also declares network interfaces, selects the control interface, and binds app data and Compose projects where needed. Templates allocate none of those values and select no app bundle.

## Choose a template

| Selection | Intended use | Complete default records |
| --- | --- | --- |
| `base` | Minimal guest defaults; selected apps contribute their own software and runtime requirements | [Base](templates/base.md) |
| `docker` | Guest explicitly selects Docker software and container-host runtime before apps are added | [Docker](templates/docker.md) |

A container app can select Docker through its profile even on `base`, as the [standalone resolver](../../site.example.yaml) demonstrates. Template selection is separate from application lifecycle or ownership.

## Override and change effects

The resolver copies the template's `resources`, `startup` and `security` maps, then replaces **direct keys** supplied by the guest. An absent or empty partial map inherits; null is not an empty map. Guest software and runtime sequences append to template selections; an empty list adds nothing and does not remove inherited selections. Guest monitoring replaces the whole reference mapping; omission inherits, while an empty mapping or null does not disable monitoring.

A template change reaches every inheriting guest. An explicit guest field remains authoritative for that field. Compare resolved output before adopting a library change. See the [Docker partial override](templates/docker.md#partial-override) for a checked example and [composition guide](../guides/compose-a-site.md#2-give-each-guest-its-facts) for complete surrounding inputs.

The runtime reserves at least 256 MiB for the operating system. Selected apps, including PegaProx, can require a higher reserve. The memory reserved for native services and containers must fit in the capacity left over. These values are deployment requirements, not measurements of service capacity.

## Installation and later changes

A template has no independent installation or service health operation. The guest and its apps follow the selected [lifecycle](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/docs/reference/lifecycle.md). `fresh` is a supported creation policy retained for later updates to the same HomeLab-managed instance; `retained` requires genuine HomeLab ownership and refuses creation.

Changing CPU, memory or startup settings changes the declared infrastructure. Depending on the supported provider operation, a change may interrupt the guest or make it temporarily unreachable. The [saved-plan guard](https://github.com/theaussiepom/homelab/blob/0a95dbea21e72fabbf337bc5d1edb8496d066176/proxmox/applications/plan_policy.py) requires an active planned guest and refuses changes to the existing disk block, including root growth and shrink. Accepted scalar syntax does not authorize replacement, data relocation, protection removal or adoption. Read [updates](../guides/images-and-updates.md) and [installation verification](../guides/installation.md) before operating.
