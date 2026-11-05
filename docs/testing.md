# Test component definitions and compositions

Keep tests at their owning boundary. Repeating a shared validator's entire
negative matrix through every application makes failures harder to interpret.

## Unit tests

- Framework component contracts test their own success and invalid-input cases.
  Filesystem, secret, ownership, transport and lifecycle guards belong there.
- Application units test their own bindings, requirements and behavior, mocking
  shared component helpers. Exercise app-specific failures without retesting the
  resource or image parser for every app.
- Guest units mock application components and test placement, aggregation,
  explicit interfaces, budgets, identity and selected dependencies.
- Library definition tests check registration, references, declared roles and
  software/policy selections. Mock framework component contracts where that is
  the unit boundary; the library must not implement another validator.

Each component needs successful compilation coverage and meaningful refusals.
Unsupported inputs must fail explicitly; a test must not change just to hide an
implementation failure. Keep useful regressions when replacing their old caller.

## Real composition integration

Use the actual compiler, lowerer and renderer for focused integration cases:

- The retained composition preserves current resource, runtime, data, credential
  and evidence identities.
- A materially different layout changes placement and app selection, not only
  addresses.
- Standalone apps omit unselected integrations. Repeated profiles have distinct
  runtime, listener and storage ownership.
- Real conflicts, missing required bindings, unsupported overrides and invalid
  dependency selections refuse.
- Workflow generation uses the actual site, one job per guest, app-only step
  labels and the existing explicit secret subsets.
- Typed guest/app source splits resolve like their complete inline bodies.
  File pins change with the source layout; provider/runtime values and the graph
  remain equal. Mutating a referenced app must still fail the generated selector's
  source-model check.
- Named address groups retain ordered membership, duplicates and explicit policy
  bindings. Fragment renames preserve rule objects, comments and expansion order.

Compile/render is integration. End-to-end means an authorized CD followed by
verification of the deployed service. An image fixture, parsed plan, green CI or
generated graph does not establish native acceptance.

## Run source checks

Use the selected framework and its locked requirements. The source workflow runs
these checks; keep that workflow authoritative as interfaces change:

```sh
python3 "$FRAMEWORK/tools/check_boundaries.py" --mode stack --root .
python3 "$FRAMEWORK/blueprints/compile.py" --stack . --site site.example.yaml --check
python3 "$FRAMEWORK/blueprints/compile.py" --stack . --site examples/site.second.yaml --check
python3 "$FRAMEWORK/blueprints/workflows.py" --stack . --site site.example.yaml --check
HOMELAB_FRAMEWORK="$FRAMEWORK" python3 -m unittest discover -s tests
```

For direct unittest/security runs, set `GITLEAKS_BIN` to the verified Gitleaks
8.30.1 executable and require zero skips. The coverage runner resolves the same
scanner from that variable, `hooks.gitleaksPath` or `PATH`.

Run the required coverage gate as well; plain unittest success does not replace
per-file line and branch coverage:

```sh
STACK_TEST_OUTPUT="$(mktemp -d)"
python3 "$FRAMEWORK/tools/measure_coverage.py" --suite stack --stack . \
  --fail-under 100 --output "$STACK_TEST_OUTPUT"
```

History, signatures, source boundaries, security, dependency checks and current
source review remain required. A scanner exception needs its existing narrow
justification and exact source binding; do not relax a gate for a bootstrap.

## Retire a replacement's old path

Record its current callers and replacement, prove the new integration, then
remove obsolete definitions, tests, scaffolding and references. Do not keep a
dead guest bundle or duplicate validator solely to make old tests pass. Preserve
required records, immutable history and regressions that still protect the
current contract. Any public compatibility path needs a concrete caller or
supported contract justification.
