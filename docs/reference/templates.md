# Guest templates

[Documentation index](../README.md) · [Reference index](README.md)

Choose a template for reusable guest defaults. A site still supplies context/provider identity, lifecycle, VMID/hostname, template image, root storage, NICs/control interface and any app data/project bindings. Templates allocate none of those values and select no app bundle.

## Choose a template

| Selection | Intended use | Complete default records |
| --- | --- | --- |
| `base` | Minimal guest defaults; selected apps contribute their own software/runtime requirements | [Base](templates/base.md) |
| `docker` | Guest explicitly selects Docker software and container-host runtime before apps are added | [Docker](templates/docker.md) |

A container app can select Docker through its profile even on `base`, as the [standalone resolver](../../site.example.yaml) demonstrates. Template selection is separate from application lifecycle or ownership.

## Override and change effects

The resolver copies the template's `resources`, `startup` and `security` maps, then replaces **direct keys** supplied by the guest. An absent or empty partial map inherits; null is not an empty map. Guest software/runtime sequences append to template selections; an empty list adds nothing and does not remove inherited selections. Guest monitoring replaces the whole reference mapping; omission inherits, while an empty/null mapping is not a disable operation.

A template change reaches every inheriting guest. An explicit guest field remains authoritative for that field. Compare resolved output before adopting a library change. See the [Docker partial override](templates/docker.md#partial-override) for a checked example and [composition guide](../guides/compose-a-site.md#2-give-each-guest-its-facts) for complete surrounding inputs.

The effective OS reserve has at least a 256 MiB runtime floor and may be raised by selected requirements, including PegaProx. Native and container reservations must fit after that reserve. Resource values are admission policy, not measured capacity.

## Installation and later changes

A template has no independent installation or service health operation. Its consuming guest/app follows the selected [lifecycle](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md). `fresh` is a supported creation policy retained for later owned updates; `retained` requires genuine HomeLab ownership and refuses creation.

CPU/memory/startup affect desired infrastructure and may interrupt running state/reachability under the selected provider path. The [saved-plan guard](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/plan_policy.py) requires an active planned guest and refuses changes to the existing disk block, including root growth and shrink. Accepted scalar syntax does not authorize replacement, data relocation, protection removal or adoption. Read [updates](../guides/images-and-updates.md) and [installation verification](../guides/installation.md) before operating.
