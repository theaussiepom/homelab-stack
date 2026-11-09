# Docker guest template

[Templates](../templates.md) · [Reference index](../README.md) · [Complete source](../../../templates/docker.yaml)

Select Docker packages and container-host requirements explicitly. Select with `guests.<id>.template: docker`. The template is a default declaration, not a guest instance or an app bundle. Site-owned required fields remain in the [guest composition guide](../../guides/compose-a-site.md#2-give-each-guest-its-facts).

## Field meaning and constraints

The compatible [guest contract](https://github.com/theaussiepom/homelab/blob/26df0cb41901cb8c9ca064d87b6eb34ca54ada74/docs/reference/guests.md) and [actual scalar validators](https://github.com/theaussiepom/homelab/blob/26df0cb41901cb8c9ca064d87b6eb34ca54ada74/blueprints/component_types.py) determine which values are accepted. The following explanations accompany the exact declaration records below:

| Field group | Meaning, presence and constraints |
| --- | --- |
| `resources` | Complete in a template, partial in a guest. Actual integers only: CPU 1..2147483647, memory 256..2147483647 MiB, root 4..2147483647 GiB, reserve 0..2147483647 MiB. Resolved reserve must be less than memory; the [effective floor](../templates.md#override-and-change-effects) can be higher. |
| `startup` | Complete typed map. `started` and `start_on_boot` are booleans; `boot_order` is an integer 0..2147483647. The saved-plan guard still refuses an inactive planned guest even if `started: false` resolves. |
| `security` | Four booleans. `unprivileged` and `protection` must remain true. `nesting` must satisfy selected runtime requirements; the Docker runtime requires true. A false `keyctl` requirement means the runtime does not require that capability; it does not force every guest override to false. |
| `software`, `runtime` | Sequences of registered IDs, resolved in [shared declarations](../software-and-runtime.md). Guest additions append; they do not erase template selections. These fields do not accept arbitrary packages or commands outside the registered selections. |
| `monitoring` | Named reference whose `profile` resolves in [monitoring declarations](../software-and-runtime.md#health-and-monitoring). Guest selection replaces the reference; omission inherits. Root monitoring capability is selected separately. |

The validator for the selected type rejects unknown keys. Null is not omission. Empty guest resource, startup and security maps inherit the template values; empty software and runtime lists add nothing. See [inheritance and effects](../templates.md#override-and-change-effects) for which values take precedence and which guests a change affects.

## Partial override

This is a **guest fragment** replacing only the template and resource portion of a complete guest:

```yaml
template: docker
resources:
  memory_mib: 3072
```

The [standalone resolver source](../../../site.example.yaml) and its [guest](../../../examples/minimal/guests/resolver.yaml) provide the complete context. With this substitution, the selected compiler preserves every other inherited resource, startup and security value while replacing memory. The documentation test resolves the Docker case and generates its deployment files, comparing inheritance directly with the actual template instead of another default table. It does not resize an installed guest.

## First installation

There is no template-specific installation. The guest and apps need a supported creation path. A new guest requires its backend and ownership records to be absent. For a new app, the selected services and runtime identities must be free of conflicting existing use. Any runtime directory or app subdirectory that HomeLab creates must be absent on first creation. Other configuration, data and credential inputs may need to exist already; the selected profile defines those prerequisites and their ownership checks. The site’s other [deployment prerequisites](../../guides/installation.md#prepare-a-consuming-site) must also be checked. Choosing a template is not evidence of ownership.

## Later deployments

Changed template fields affect inheriting guests and selected runtime requirements can change which guest configurations pass deployment checks. [Execution limits](../templates.md#installation-and-later-changes) still refuse disk-block changes and unsupported changes to identities or data. CPU, memory and startup changes may interrupt service. Compare the resolved result and follow your site's protected workflow. Successful source checks do not verify the resulting guest or services.

## Invalid cases

| Change | Enforcing boundary and correction |
| --- | --- |
| `resources.memory_mib: 255` | Structural `component.integer` at `guests.resolver`; use a valid integer and enough capacity for selected reservations. |
| `security.protection: false` | Structural `component.invalid` at `guests.resolver`; protection is required. |
| Docker runtime with `security.nesting: false` | Resolution refuses `component.runtime-requirement`; preserve the selected runtime's requirement. |

The documentation integration test checks the first two invalid cases against a complete Docker guest configuration. Its diagnostic identifies the guest, not a more specific field path. Other deployment restrictions rely on their framework source and tests; this documentation test does not exercise those restrictions on a running guest.

## Declaration records

Exact values from [templates/docker.yaml](../../../templates/docker.yaml), registered in [stack.json](../../../stack.json). `object` introduces the child rows. The [record convention](../declaration-records.md) distinguishes supplied definition fields from site overrides and requirements enforced by the selected runtime.

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
