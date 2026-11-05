# Guest templates

[Documentation index](../README.md) · [Reference index](README.md)

A template provides a complete resource/startup/security default declaration. A site selects it with `guests.<id>.template`, then supplies provider identity, interfaces, storage and lifecycle. A template does not allocate a VMID, address or volume and does not impose an app set.

## Registered templates

| Template | Source | CPU cores | Memory MiB | Root GiB | OS reserve MiB |
| --- | --- | --- | --- | --- | --- |
| `base` | [base.yaml](../../templates/base.yaml) | 1 | 1024 | 4 | 256 |
| `docker` | [docker.yaml](../../templates/docker.yaml) | 1 | 1024 | 8 | 256 |

Both templates use the following explicit startup/security defaults:

| Block | Property | Value |
| --- | --- | --- |
| startup | started | `true` |
| startup | start_on_boot | `true` |
| startup | boot_order | `20` |
| security | unprivileged | `true` |
| security | protection | `true` |
| security | nesting | `true` |
| security | keyctl | `false` |

| Template | Software | Runtime | Monitoring |
| --- | --- | --- | --- |
| `base` | None | None | `linux-agent` |
| `docker` | `docker` | `container-host` | `linux-agent` |


`base` does not itself select Docker packages. A container app can select the required Docker software/runtime through its profile, as the minimal Unbound example does. `docker` selects the named Docker software and container-host requirements directly. Native apps still need their own package/runtime selections.

## Override only what changes

This is a **partial guest fragment**:

```yaml
resources:
  memory_mib: 3072
```

It replaces only memory. CPU, root size and reserve inherit from the selected template. The complete [HA example guest](../../examples/second/guests/home-app.yaml) shows the surrounding identity/interfaces/storage. The framework applies template defaults followed by explicit guest fields; it does not merge arbitrary source overlays.

| Resource | Complete template | Guest override | Syntax constraint |
| --- | --- | --- | --- |
| cpu_cores | Required | Optional | Integer 1..2147483647 |
| memory_mib | Required | Optional | Integer 256..2147483647 MiB |
| root_gib | Required | Optional | Integer 4..2147483647 GiB |
| os_reserve_mib | Required | Optional | Integer 0..2147483647 and less than memory_mib |

The effective runtime reserve has a 256 MiB floor and is raised by any selected runtime requirement. PegaProx currently requires 512 MiB. Native plus container memory reservations must fit after that reserve. These are admission policies, not measured capacity; syntactic bounds do not mean a host can supply those resources.

## Startup, security and update effects

`started` and `start_on_boot` are booleans; boot_order is an integer 0..2147483647. Security fields are explicit booleans; unprivileged and protection must remain true. Selected runtime requirements must be compatible with the guest security choices. In particular, HA's retained mDNS NET_ADMIN capability is an explicit app runtime selection, not a privilege inherited by every Docker guest.

Changing CPU/memory/startup affects desired infrastructure. The supported provider plan determines actual interruption. Shrink/move/protection/identity changes are not universally supported replacements. Preserve current NIC slots/MACs, data/volume identity, accounts, state and holds. Read [Images and updates](../guides/images-and-updates.md) before modifying an installed guest.

Templates are source defaults, not ownership evidence. A retained guest still requires a genuine current component success and matching backend. A fresh guest cannot adopt an existing backend or data tree.
