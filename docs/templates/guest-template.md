# Guest-template documentation template

[Contributing](../contributing.md) · [Documentation standard](../contributing/documentation-standard.md) · [Template catalogue](../reference/templates.md)

This is an authoring form, not executable configuration. Replace instructions with facts from the registered template and the resolver in the compatible framework; do not ship empty headings.

Write for a reader who is new to HomeLab: name who does what, explain necessary terms when first used, and state the concrete result before internal terminology. Keep exact identifiers and technical requirements intact. After editing, reread the complete page, obtain an independent readability review, and revise the prose before calling it complete. Keep each prose paragraph on one source line.

## Purpose and selection

Name the selection ID and complete definition, explain when to choose the template, and list the guest fields that the site must still supply. A template must not imply an application bundle or allocate an identity on the provider.

## Field records

Use the [declaration-record convention](../reference/declaration-records.md) for every supplied object and nested field. State the type, whether a value is required, any default, the units and the permitted range. Explain separately what happens when a value is omitted, null or empty, and which direct keys or sequence entries take precedence. Link the framework type that defines the field and each selected shared software, runtime or monitoring definition from the relevant record. Source declarations remain authoritative for values and defaults; test mappings must contain pointers rather than copies of those values.

## Inherited and override examples

Link a complete canonical guest declaration in its site, show a useful partial override labelled as a fragment, and use the selected framework to compare the inherited values with the actual changed result. State which output is generated, and distinguish declared reserve from requirements enforced by the selected runtime.

## First installation

Explain that a template has no independent installation, secrets or service health. Link the creation prerequisites and ownership limits for guests and apps that use it.

## Later deployments

Describe which inheriting guests change and which explicit overrides persist. Classify infrastructure effects, possible interruption and actual execution refusals; do not infer that resizing, replacement or adoption is supported merely because the syntax is accepted.

## Invalid cases and review

Provide meaningful invalid variations, the actual error code and context for each, and the supported correction. Reuse real component evidence and preserve the distinction between source checks and verification on a target. Update registration, table mappings, examples and [conformance checks](../testing.md#documentation-conformance) together, then review links and rendering.
