# Test the library

[Documentation index](README.md) · [Contributing](contributing.md)

Use the clean selected source checkouts and isolated Python environment from [First configuration](guides/first-configuration.md). That page defines STACK, FRAMEWORK, WORK_ROOT and PYTHON. Commands below work from that same shell; no target/Docker operation is required for the library source suite.

## Test the owning boundary

- Framework component units own type/default/reference/path/ownership/transport failure matrices.
- App units mock conforming shared contracts and test app-specific capability/binding behavior.
- Guest units mock app results and test placement, aggregation, budgets, identities and selected dependencies.
- Library units check registration, profile requirements and manifest choices without implementing another validator.
- Focused compiler integration exercises actual supported components and distinct/repeated app compositions.
- End-to-end means authorized CD followed by actual deployed service verification. Compile/render, mocked native calls and image startup fixtures are different evidence.

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

Expect passing current tests with no skipped security cases and 100% executable lines/branches for **each** production Python file in the stack scope. Read summary.json/summary.md in the new output directory. Reports are local private artifacts, not public uploads. Plain unittest success does not replace coverage.

For focused definition work, after the scanner is available:

```sh
HOMELAB_FRAMEWORK="$FRAMEWORK" GITLEAKS_BIN="$GITLEAKS_BIN"   "$PYTHON" -m unittest discover -s "$STACK/tests" -p test_component_definitions.py
```

## Preserve the complete gates

```sh
"$PYTHON" "$STACK/.github/scripts/check_history.py" --root "$STACK"   --framework "$FRAMEWORK" --scanner "$GITLEAKS_BIN"
git -C "$STACK" diff --check
```

Use complete Git history. Normal staged/push hooks, trusted signature verification, workflow lint, security/dependency checks and genuine current source reviews remain required. The [source workflow](../.github/workflows/validate-stack.yml) is authoritative for the actual selected setup and gates; do not hand-patch generated files or thresholds.

Composition integration covers standalone Unbound, HA without unselected integrations, different placement, repeated instances, fresh/retained ownership, explicit readiness and source splits/groups. It checks identity, data/credential references, policy order and generated jobs. Native lifecycle/hardware/protocol acceptance remains at its separately qualified boundary.

After a replacement qualifies, inventory callers and retire obsolete definitions/tests/scaffolding and duplicate guidance. Keep immutable history and current regressions; a compatibility branch needs a concrete supported caller. Documentation changes move examples and tests together and do not authorize target actions.

## Documentation conformance

The normal source suite collects `DocumentationConformance` and `DocumentationConformanceMechanism` in `tests/test_documentation_examples.py`, together with the existing real profile/example integrations and navigation tests. Run them using the same selected `FRAMEWORK`/locked `PYTHON` setup above:

```sh
HOMELAB_FRAMEWORK="$FRAMEWORK" "$PYTHON" -m unittest discover -s "$STACK/tests" -p 'test_documentation*.py' -v
HOMELAB_FRAMEWORK="$FRAMEWORK" "$PYTHON" -m unittest discover -s "$STACK/tests" -p test_profile_examples.py -v
```

The denominator comes from the real registered library and loaded definitions, not the mapping. At this source revision it comprises 23 app/template definitions, 1,306 supplied object/leaf paths, 64 shared named registrations, and the selected MQTT validator’s one accepted optional property. Tests derive these counts/surfaces from source rather than freezing those numbers as acceptance criteria. The checked scope is every registered app/profile variant and guest template's supplied object/leaf path, every registered shared software/runtime/health/authentication/monitoring/asset/network-policy name, and canonical profile complete examples. `tests/documentation_records.py` contains definition source/document pointers, shared registration identifiers and explicit MQTT validator-owner pointers; it does not repeat the 1,306 field paths; `tests/documentation_contracts.py` parses the deliberately simple reference table and compares actual typed values. Tables are independently enumerated, so new orphan rows fail as well as source fields without a documentation row. Empty/duplicate/unclassified inventories refuse.

The semantic pilot resolves/lowers the real MQTT composition, checks its complete excerpt, endpoint values, the actual accepted optional-property inventory, and missing/non-file probe floor, and asserts exact property refusals. Docker checks actual omission inheritance, the documented partial resource override and precise invalid-memory/protection refusals. Mechanism fixtures prove missing/stale definition pointers and missing/stale/orphan field records, source/document drift, strict types, ambiguous cells/anchors, stale excerpts, wrong or absent refusals and empty scopes fail. No target/process access is permitted in these integrations; credential references remain metadata.

This is full **supplied declaration** coverage, not an inventory of every optional framework input or every procedural rule. Shared nested declarations and lifecycle/conditional prose still need source-backed human review. Compatibility is the actual library-selected framework, not an unrelated current checkout. Source/coverage success does not prove hosted scheduling, required-check enforcement, installation or service acceptance. Preserve the independently collected required-module/class checks and all existing security/history/signature/review gates.
