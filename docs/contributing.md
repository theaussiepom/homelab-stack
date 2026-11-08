# Add or maintain a profile

[Documentation index](README.md) · [Working agreement](../AGENTS.md)

This repository owns reusable profiles, templates and version/runtime declarations. The framework owns schemas, reference resolution, compiler/render/deployment engines and security/lifecycle helpers. A site owns allocations, access policy, protected references and placement.

Apply the local [documentation standard](contributing/documentation-standard.md) to profile, template and composition documentation. The compatible [framework documentation policy](https://github.com/theaussiepom/homelab/blob/e9f3a1f17b6a23bbdb09943f2d0411d3c5da85cd/docs/contributing/documentation.md) defines the language and deployment requirements. Use the [application-profile template](templates/application-profile.md) or [guest-template template](templates/guest-template.md), then review the result against the standard's rubric. A filled checklist does not prove completeness.

## Extend an existing capability

1. Check the [catalogue](reference/README.md) and [framework contract](https://github.com/theaussiepom/homelab/blob/e9f3a1f17b6a23bbdb09943f2d0411d3c5da85cd/docs/reference/README.md). Reuse an adapter rather than introducing a fixed guest bundle or private parser.
2. Add `apps/<profile>.yaml` with schema homelab-components-v1 and kind app-profile. Declare exact interfaces, listeners, endpoints, storage, connection requirements, software/runtime/health and conditional inputs. Supporting containers stay owned by the app.
3. Register that complete definition in stack.json. Keep image/version policy in images.json and named runtime policy in stack.json. Do not work around a missing typed capability by adding arbitrary commands, environment variables, mounts or Compose settings.
4. Add/update its reference page under docs/reference/apps and catalogue index. Explain required/optional/conditional bindings, defaults, data/secret/auth ownership, first installation, later deployment and multi-instance limits. Link a real complete composition where supported; label fragments and unqualified commissioning honestly.
5. Test definitions at their owning boundary and add focused real composition checks. Use mock framework contracts in app/guest units where unrelated behavior is not under test.
6. Run [all existing gates](testing.md), review the exact diff and preserve failures until classified. Publish normal signed source; downstream sites select only actual published compatible dependencies.

If the existing adapter cannot express a capability, implement its closed contract and useful negative tests upstream first. Do not infer extra privilege, account creation, readiness, routes or firewall grants from a profile selection.

## Keep source and documentation together

Update docs, maintained examples and tests when a public profile changes. New defaults must be explicit and reviewable. Prefer named reusable declarations and complete source references over copied guest layouts. Keep synthetic examples free of private allocations, repository names, credentials, observations, history and archives.

After the replacement is integrated, inventory old callers and remove obsolete code/tests/scaffolding and duplicate guidance. Keep useful current regressions and immutable history; do not retain an unused compatibility branch solely to satisfy old tests.

AGENTS.md stays short and links the [documentation index](README.md). Security/review/coverage/history/signature requirements are preserved; documentation work is not permission to relax them.

## Maintain the checked contract

Read [conformance scope](testing.md#documentation-conformance) before changing a public control/default. Keep configuration and validators authoritative. The test-local `documentation_records.py` stores only source paths, document paths and field/registration identifiers; never add a second set of types, constraints or defaults. Update a canonical declaration table, its pointer mapping and complete example together. A new record with no accepted source, a new source field with no record, a duplicate or stale value must fail.

Review adapter/property changes for semantic requirements that structural inventory cannot discover. Preserve MQTT’s requirement for probe credentials in a file even though the metadata marks the role optional, and distinguish declared template defaults from actual inheritance and execution policy. Use the real selected framework, compare excerpts with canonical source, and assert the intended refusal code/context.

Follow README → catalogue → property/type → complete example → diagnostic → later deployments as a reader. Check rendered Markdown as well as local links. Run [required gates](testing.md), report how many items were checked, what behavior remains unreviewed and what still needs verification on a target, and do not equate local source success with hosted merge enforcement or service acceptance.

## Backup classification

Classify every app storage role in its `backup.include` or `backup.exclude` map. In the [coverage catalogue](reference/backup-coverage.md), explain the native configuration, related databases, consistency requirements and protection of credentials and keys. Follow [PBS backup preparation](backup.md); declaring a profile does not prove that capture or restore works on a target. Cover new roles and examples with definition tests and real compiler integration.
