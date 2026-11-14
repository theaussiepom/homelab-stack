# Test the library

[Documentation index](README.md) · [Contributing](contributing.md)

Use the clean selected source checkouts and isolated Python environment from [First configuration](guides/first-configuration.md). That page defines STACK, FRAMEWORK, WORK_ROOT and PYTHON. Commands below work from that same shell; no target or Docker operation is required for the library source suite.

## Test the owning boundary

- Framework component unit tests check types, defaults, references, paths, ownership and transport, including invalid combinations.
- App unit tests use mocks that satisfy shared contracts, then check the app’s own capabilities and bindings.
- Guest unit tests mock app results and check placement, combined requirements, budgets, identities and selected dependencies.
- Library units check registration, profile requirements and manifest choices without implementing another validator.
- Focused compiler integration exercises actual supported components and compositions containing distinct apps or repeated instances.
- End-to-end means authorized CD followed by actual deployed service verification. Compilation, configuration generation, mocked calls to target systems and image startup tests are different evidence.

Preserve useful current guards when porting an obsolete test. Establish whether a failure is a product defect or an old fixture assumption before changing it.

## Run source and example checks

```sh
"$PYTHON" "$FRAMEWORK/tools/check_boundaries.py" --mode stack --root "$STACK"
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK"   --site "$STACK/site.example.yaml" --check
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK"   --site "$STACK/examples/site.second.yaml" --check
"$PYTHON" "$FRAMEWORK/blueprints/workflows.py" --stack "$STACK"   --site "$STACK/site.example.yaml" --check
```

Expect zero boundary findings and unchanged generated workflows. The [example index](examples/README.md) identifies complete maintained sources; fragments are labelled and backed by actual complete cases where supported.

## Install the verified scanner

The source workflow uses the selected framework's pinned scanner installer. This downloads a verified development tool into the disposable workspace, not onto a guest:

```sh
SCANNER_ROOT="$WORK_ROOT/source-tools"
"$PYTHON" "$FRAMEWORK/.github/scripts/install_gitleaks.py" "$SCANNER_ROOT"
GITLEAKS_BIN="$SCANNER_ROOT/gitleaks"
export GITLEAKS_BIN
"$GITLEAKS_BIN" version
```

Require the selected installer/version and zero security-test skips. Direct tests and hooks use GITLEAKS_BIN; the coverage runner can also resolve the configured hooks.gitleaksPath or PATH. Do not treat a skipped scanner as a passing security check.

## Run tests and per-file coverage

The output directory must be **new and nonexistent**. mktemp creates only its parent:

```sh
COVERAGE_PARENT="$(mktemp -d)"
COVERAGE_PARENT="$(cd "$COVERAGE_PARENT" && pwd -P)"
COVERAGE_OUTPUT="$COVERAGE_PARENT/stack-coverage"
HOMELAB_FRAMEWORK="$FRAMEWORK" GITLEAKS_BIN="$GITLEAKS_BIN"   "$PYTHON" "$FRAMEWORK/tools/measure_coverage.py" --suite stack --stack "$STACK"   --fail-under 100 --output "$COVERAGE_OUTPUT"
```

Expect passing current tests with no skipped security cases and 100% executable lines and branches for **each** production Python file in the stack scope. Read summary.json and summary.md in the new output directory. Reports are local private artifacts, not public uploads. Plain unittest success does not replace coverage.

For focused definition work, after the scanner is available:

```sh
HOMELAB_FRAMEWORK="$FRAMEWORK" GITLEAKS_BIN="$GITLEAKS_BIN"   "$PYTHON" -m unittest discover -s "$STACK/tests" -p test_component_definitions.py
```

## Preserve the complete gates

```sh
"$PYTHON" "$STACK/.github/scripts/check_history.py" --root "$STACK"   --framework "$FRAMEWORK" --scanner "$GITLEAKS_BIN"
git -C "$STACK" diff --check
```

Use complete Git history. Normal staged and push hooks, trusted signature verification, workflow lint, security and dependency checks and genuine review of the current sources remain required. The [source workflow](../.github/workflows/validate-stack.yml) is authoritative for the actual selected setup and gates; do not hand-patch generated files or thresholds.

Composition integration covers standalone Unbound, HA without unselected integrations, different placement, repeated instances, fresh and retained ownership, explicit readiness, separate source files and address groups. It checks identity, data and credential references, policy order and generated jobs. Lifecycle transitions, hardware access and protocols still need their own tests against a running target.

After tests establish that a replacement meets its requirements, identify its callers and remove obsolete definitions, tests, scaffolding and duplicate guidance. Keep immutable history and current regressions; a compatibility branch needs a concrete supported caller. Documentation changes move examples and tests together and do not authorize target actions.

## Documentation conformance

The normal source suite collects `DocumentationConformance` and `DocumentationConformanceMechanism` in `tests/test_documentation_examples.py`, together with the existing integrations using real profiles and examples and navigation tests. Run them using the same selected `FRAMEWORK`/locked `PYTHON` setup above:

```sh
HOMELAB_FRAMEWORK="$FRAMEWORK" "$PYTHON" -m unittest discover -s "$STACK/tests" -p 'test_documentation*.py' -v
HOMELAB_FRAMEWORK="$FRAMEWORK" "$PYTHON" -m unittest discover -s "$STACK/tests" -p test_profile_examples.py -v
```

The tests discover what to check from the registered library and loaded definitions, not from the documentation mapping. The registered definitions determine the supplied object and nested-field inventory; shared registrations and the selected MQTT validator determine their respective inventories. The checks derive these sets from source rather than requiring rolling totals in this guide or hard-coded counts.

The scope includes every supplied field path in each registered app profile, variant, guest template and backup profile, plus every registered shared software, runtime, health, authentication, monitoring, asset and network-policy name. It also includes the complete canonical examples for those profiles.

`tests/documentation_records.py` points to each definition’s source and documentation, lists shared registration identifiers, and identifies the MQTT validator responsible for its property contract. It stores source/document pointers rather than repeating the derived field paths. `tests/documentation_contracts.py` parses the reference tables and compares their actual typed values with source. The checker independently reads every row, so it rejects extra rows without a source field as well as source fields missing from documentation. Empty inventories, duplicates and unclassified entries also fail.

The MQTT behavior tests resolve the complete composition and generate its deployment files. They check the complete excerpt, endpoint values and accepted optional property, then verify that missing probes, non-file probes and invalid property values produce the exact expected errors. The Docker tests check inheritance when a value is omitted, the documented partial resource override, and the exact errors for invalid memory and protection settings.

The PBS checks compare every recovery-catalogue role, mount target, category, capture method and exclusion with the loaded profiles. They also exercise the guide’s preparation and volume fragments, compare its operational job excerpt with the maintained complete example, and check the documented refusal codes and contexts. Source, packet and file checks remain distinct from an actual scheduled backup or restore. The independent CI collection guard names each new PBS documentation check.

Separate fixtures test the checking mechanism itself. They require failures for missing or stale definition pointers; missing, stale or extra field records; differences between source and documentation; incorrect value types; ambiguous cells or anchors; missing or stale backup-profile pointers; changed recovery classifications or targets; stale excerpts; wrong or missing expected errors; and empty scopes. These integration tests cannot contact targets or start processes. They use credential references without reading credential values.

The [Design your homelab journey](guides/design-your-homelab.md) is exercised by `PersonalisationWalkthrough` in `tests/test_documentation_personalisation.py`. It copies the complete maintained source, reads the practice worksheet and optional app, layout and policy fragments from the actual guide, invokes the real compiler CLI entry point and packet inspector, and checks changed allocations, scoped browser access, HA data and independent app selection across separate and shared guests. Exact negative cases check source, address, interface, memory and storage-initializer refusals; create-only output and unchanged input are checked too. The independent CI collection guard names the class and both layout cases so silently deleting them fails. These tests establish that the printed source and tutorial commands work, not a claim that an unfamiliar human has completed the journey or that a service has been deployed.

This is full **supplied declaration** coverage, not an inventory of every optional framework input or every procedural rule. Shared nested declarations, lifecycle explanations and conditional requirements still need source-backed human review. Compatibility is the actual library-selected framework, not an unrelated current checkout. Passing source and coverage checks does not prove hosted scheduling, required-check enforcement, installation or service acceptance. Preserve the independently collected checks that required modules and classes are collected, along with all existing security, history, signature and review requirements.

The `home-web.yaml` composition checks the standard Home Assistant selection, an owned-volume initializer, named HTTP endpoint, HTTPS route and changed guest address. The same integration boundary checks the documented explicit custom archive syntax and preservation of custom Node-RED authentication, storage and runtime inputs. It refuses retired profile names, old exposure fields, unknown endpoints, conflicting software, upstream image overrides and unused archive bindings. These tests are independently required by the collection guard; compiler evidence is distinct from the framework’s genuine-receipt ownership tests and from target verification.

The source workflow checks out the immutable pull-request head (or the pushed commit on main) with complete history and no persisted credentials. History identity checks apply to authored commits; GitHub’s synthetic PR merge can use the account display name and must not replace that authored revision. The workflow test requires this exact selection while preserving all scanner, coverage and identity rules.

## Actual Renovate catalogue manager

With Node 24.15.0, run `npm ci --prefix tests/renovate --no-audit --no-fund` and `npm test --prefix tests/renovate`. The locked Renovate dependency validates `renovate.json`, extracts every registry record from the actual catalogue and applies its real replacement engine. Cases cover digest-only entries, tag changes, new entries, digest pins and preservation of private archives. CI runs these alongside the Python source gates. They make no registry query or GitHub mutation and do not establish CE server startup or successful live PR creation.
