# Docker guest template

[Templates](../templates.md) · [Reference index](../README.md) · [Complete source](../../../templates/docker.yaml)

Select Docker packages and container-host requirements explicitly. Select with `guests.<id>.template: docker`. The template is a default declaration, not a guest instance or an app bundle. Site-owned required fields remain in the [guest composition guide](../../guides/compose-a-site.md#2-give-each-guest-its-facts).

## Field meaning and constraints

The compatible [guest contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/guests.md) and [actual scalar validators](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_types.py) own acceptance. These rules apply to the exact declaration records below:

| Field group | Meaning, presence and constraints |
| --- | --- |
| `resources` | Complete in a template, partial in a guest. Actual integers only: CPU 1..2147483647, memory 256..2147483647 MiB, root 4..2147483647 GiB, reserve 0..2147483647 MiB. Resolved reserve must be less than memory; the [effective floor](../templates.md#override-and-change-effects) can be higher. |
| `startup` | Complete typed map. `started` and `start_on_boot` are booleans; `boot_order` is an integer 0..2147483647. The saved-plan guard still refuses an inactive planned guest even if `started: false` resolves. |
| `security` | Four booleans. `unprivileged` and `protection` must remain true. `nesting` must satisfy selected runtime requirements; the Docker runtime requires true. A false `keyctl` requirement is non-demanding and does not force every guest override false. |
| `software`, `runtime` | Sequences of registered IDs, resolved in [shared declarations](../software-and-runtime.md). Guest additions append; they do not erase template selections. No arbitrary package/command override bag. |
| `monitoring` | Named reference whose `profile` resolves in [monitoring declarations](../software-and-runtime.md#health-and-monitoring). Guest selection replaces the reference; omission inherits. Root monitoring capability is selected separately. |

Unknown keys refuse at the selected typed owner. Null is not omission. Empty guest resource/startup/security maps inherit; empty software/runtime lists add nothing. See [inheritance and effects](../templates.md#override-and-change-effects) for exact precedence and blast radius.

## Partial override

This is a **guest fragment** replacing only the template/resource portion of a complete guest:

```yaml
template: docker
resources:
  memory_mib: 3072
```

The [standalone resolver source](../../../site.example.yaml) and its [guest](../../../examples/minimal/guests/resolver.yaml) provide the complete context. With this substitution, the real selected resolver must preserve every other inherited resource/startup/security value while replacing memory. The documentation test resolves and lowers the Docker case, comparing inheritance directly with the actual template instead of another default table. It does not resize an installed guest.

## First installation

There is no template-specific installation. Its guest/app needs a supported creation path, absent owned resources where required, and [qualified site prerequisites](../../guides/installation.md#prepare-a-consuming-site). Choosing a template is not evidence of ownership.

## Later deployments

Changed template fields affect inheriting guests and selected runtime requirements can change effective admission. [Execution limits](../templates.md#installation-and-later-changes) still refuse disk-block changes and unsupported identity/data transitions. CPU/memory/startup changes may interrupt service. Compare the resolved result and follow the consuming site's protected workflow; source success is not target acceptance.

## Invalid cases

| Change | Enforcing boundary and correction |
| --- | --- |
| `resources.memory_mib: 255` | Structural `component.integer` at `guests.resolver`; use a valid integer and enough capacity for selected reservations. |
| `security.protection: false` | Structural `component.invalid` at `guests.resolver`; protection is required. |
| Docker runtime with `security.nesting: false` | Resolution refuses `component.runtime-requirement`; preserve the selected runtime's requirement. |

The bounded documentation integration executes the first two against a complete Docker guest. Its refusal context identifies the guest rather than inventing a field-specific error path. Other execution limits retain their framework test/source boundary.

## Declaration records

Exact values from [templates/docker.yaml](../../../templates/docker.yaml), registered in [stack.json](../../../stack.json). `object` introduces the child rows. The [record convention](../declaration-records.md) distinguishes supplied definition fields from site overrides and effective runtime floors.

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-resources"></a>`resources` | `object` |
| <a id="declaration-resources-cpu-cores"></a>`resources.cpu_cores` | `1` |
| <a id="declaration-resources-memory-mib"></a>`resources.memory_mib` | `1024` |
| <a id="declaration-resources-root-gib"></a>`resources.root_gib` | `8` |
| <a id="declaration-resources-os-reserve-mib"></a>`resources.os_reserve_mib` | `256` |
| <a id="declaration-startup"></a>`startup` | `object` |
| <a id="declaration-startup-started"></a>`startup.started` | `true` |
| <a id="declaration-startup-start-on-boot"></a>`startup.start_on_boot` | `true` |
| <a id="declaration-startup-boot-order"></a>`startup.boot_order` | `50` |
| <a id="declaration-security"></a>`security` | `object` |
| <a id="declaration-security-unprivileged"></a>`security.unprivileged` | `true` |
| <a id="declaration-security-protection"></a>`security.protection` | `true` |
| <a id="declaration-security-nesting"></a>`security.nesting` | `true` |
| <a id="declaration-security-keyctl"></a>`security.keyctl` | `false` |
| <a id="declaration-software"></a>`software` | `["docker"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host"]` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"linux-agent"` |
