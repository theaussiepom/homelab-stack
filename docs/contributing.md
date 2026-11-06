# Add or maintain a profile

[Documentation index](README.md) · [Working agreement](../AGENTS.md)

This repository owns reusable profiles, templates and version/runtime declarations. The framework owns schemas, reference resolution, compiler/render/deployment engines and security/lifecycle helpers. A site owns allocations, access policy, protected references and placement.

Apply the selected [framework documentation standard](https://github.com/theaussiepom/homelab/blob/4d926e82869f5fc2b497577f341ff82c3e7f619b/docs/contributing/documentation.md). Use the [application-profile documentation template](templates/application-profile.md) for every new or changed profile page. It requires concrete syntax, conditional properties, complete tested examples, First installation, Later deployments and invalid cases; empty boilerplate is not a substitute.

## Extend an existing capability

1. Check the [catalogue](reference/README.md) and [framework contract](https://github.com/theaussiepom/homelab/blob/4d926e82869f5fc2b497577f341ff82c3e7f619b/docs/reference/README.md). Reuse an adapter rather than introducing a fixed guest bundle or private parser.
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

## Backup classification

Classify every app storage role in its `backup.include` or `backup.exclude` map, and document native configuration, external database associations, consistency requirements and secret custody in the [coverage catalogue](reference/backup-coverage.md). Follow [PBS preparation](backup.md); no producer or restore qualification is inferred from a profile. Keep new roles and examples covered by definition and real compiler tests.
