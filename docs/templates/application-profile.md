# Application-profile documentation template

[Contributing](../contributing.md) · [Profile catalogue](../reference/README.md) · [Framework documentation standard](https://github.com/theaussiepom/homelab/blob/dbca1f93f434c70d97f99df845972a3c467f6fc3/docs/contributing/documentation.md)

Use this checklist when creating or changing a profile page. It is an authoring template, not a configuration to execute. Replace the instructions with concrete facts from the selected profile, adapter and maintained complete example; delete irrelevant guidance. Do not publish blank sections, invented defaults or unsupported examples.

## Purpose and choice

Explain what the application does and when to select this profile rather than another variant. Name its adapter and owned supporting containers. State important external prerequisites in plain language before explaining internal ownership proofs.

## Syntax and properties

Show the smallest useful app-selection fragment, label it **fragment**, and link its exact app ID in a complete maintained synthetic composition. State which fields belong to the reusable profile and which belong to the consuming site.

For each property or binding, document:

- Required, optional or conditional presence, including the actual current adapter floor.
- Type, default when one exists, bounds/allowed values and important invalid values.
- Named references and their effects. Distinguish values, readiness, access intent, publication, trust and account privilege.
- Interfaces, listeners/publications, storage/access/initialization, secrets/authentication, software and resource requirements.

An absent topic should say “None” or “Not applicable” briefly. Do not add a readiness-column explanation without a table, GUI-password warnings to unrelated apps or fictional secret roles.

## Minimal and practical examples

Link at least one complete canonical YAML source that passes the real selected resolver **and** packet lowerer with the real library profile. Keep the body in one source file/location; documentation excerpts must be checked against it. A catalogue/profile file alone is not a complete usage example.

Provide fully defined validation commands, or link the setup that defines their shell variables. Explain expected output, relevant app/guest IDs and what the example establishes. Mark a retained source-only example as requiring an already HomeLab-managed installation; never present it as an installer or import procedure.

Include a practical relationship or variant example where it explains the profile: explicit upstream, managed account, auth gateway, multiple interfaces, repeated instances or a deliberate resource override. Explain required companion services without implying every profile is dependency-free.

## First installation

Use this exact heading. Say plainly whether this profile can create the supported new service/data or whether creation is not implemented. Separate supported source/controller behavior from unverified target installation, vendor onboarding and separately prepared infrastructure/accounts/configuration.

For a supported creation path, link its complete example and list its actual prerequisites. Explain that `lifecycle: fresh` is a creation policy which stays unchanged for ordinary later deployments. It is not a one-run switch.

## Later deployments

Use this exact heading. Describe what ordinary deployment maintains and preserves, and which changes may be applied, refused or require a separately reviewed procedure. Distinguish public configuration changes from persistent identity, data and credential changes. `retained` requires an already managed installation; it does not import a foreign one.

State the effect of software/image/default updates. Keep version declarations in their existing manifest; do not copy a version policy into a site example or promise automatic upgrade/data migration.

## Invalid cases and validation

Give at least two relevant invalid examples and the intended refusal layer. Trace conditional constraints to the actual source/adapter. Reuse upstream negative matrices; add a focused library integration only when it protects a documented composition or known caller floor.

Maintain profile-to-example coverage in the library's documentation tests. Run the source suite, real example compiles, navigation/anchors and existing coverage/security/history/signature gates. Distinguish compile/render integration from authorized CD and actual service acceptance.

## Related guidance

Link the profile declaration, complete example, related variant, shared lifecycle/reference and task guides. Preserve useful existing anchors or canonical pointers when replacing old guidance. Review the complete page as a new user before publication.

## Backup coverage

List every storage role as authoritative configuration/state/database or explicitly transient/rebuildable. Link the exact disposition and capture requirement in the recovery catalogue. Explain native configuration, individually owned runtime inputs, database associations, required secret/key custody and what has actually been qualified. Client installation, raw engine files and warm SQLite copies are not application recovery proof.
