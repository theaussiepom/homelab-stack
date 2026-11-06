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

Expect passing current tests with no skipped security cases and100% executable lines/branches for **each** production Python file in the stack scope. Read summary.json/summary.md in the new output directory. Reports are local private artifacts, not public uploads. Plain unittest success does not replace coverage.

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
