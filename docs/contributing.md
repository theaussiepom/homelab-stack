# Add or maintain a profile

[Documentation index](README.md) · [Working agreement](../AGENTS.md)

This repository owns reusable profiles, templates and version/runtime declarations. The framework owns schemas, reference resolution, compiler/render/deployment engines and security/lifecycle helpers. A site owns allocations, access policy, protected references and placement.

Apply the local [documentation standard](contributing/documentation-standard.md) to profile, template and composition documentation. The compatible [framework documentation policy](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/contributing/documentation.md) owns the language and deployment contract. Use the [application-profile template](templates/application-profile.md) or [guest-template template](templates/guest-template.md), then review the result against the standard's rubric. A filled checklist does not prove completeness.

## Extend an existing capability

1. Check the [catalogue](reference/README.md) and [framework contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/README.md). Reuse an adapter rather than introducing a fixed guest bundle or private parser.
2. Add `apps/<profile>.yaml` with schema homelab-components-v1 and kind app-profile. Declare exact interfaces, listeners, endpoints, storage, connection requirements, software/runtime/health and conditional inputs. Supporting containers stay owned by the app.
3. Register that complete definition in stack.json. Keep image/version policy in images.json and named runtime policy in stack.json. No raw command, environment, extra-mount or Compose override bag is a replacement for a missing typed capability.
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

Review adapter/property changes for semantic requirements that structural inventory cannot discover. Preserve the MQTT file-probe floor even while metadata says optional, and distinguish declared template defaults from actual inheritance and execution policy. Use the real selected framework, compare excerpts with canonical source, and assert the intended refusal code/context.

Follow README → catalogue → property/type → complete example → diagnostic → later deployments as a reader. Check rendered Markdown as well as local links. Run [required gates](testing.md), report the checked denominator and remaining semantic/native limits, and do not equate local source success with hosted merge enforcement or service acceptance.
