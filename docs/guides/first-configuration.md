# Compile your first configuration

[Documentation index](../README.md) · [Start here](../start-here.md)

This tutorial produces a resolver deployment packet from the maintained synthetic YAML example. It does not provision a guest, install a package, run a container or read the example's credential/trust paths.

## 1. Prepare an isolated source environment

Start a Bash-compatible shell in the root of a clean library Git checkout at the reviewed published revision whose documentation you are reading. Git, Python 3.12/3.13, `venv` and pip must be available. These commands define all paths; they install only local development dependencies.

```sh
STACK="$(pwd -P)"
STACK_REVISION="$(git rev-parse HEAD)"
FRAMEWORK_REVISION=0094e1c5fc0b8c461e3a7be98de7fb6203a17b45
WORK_ROOT="$(mktemp -d)"
WORK_ROOT="$(cd "$WORK_ROOT" && pwd -P)"
FRAMEWORK="$WORK_ROOT/homelab"

test -f "$STACK/stack.json"
test -f "$STACK/site.example.yaml"
git clone --no-checkout https://github.com/theaussiepom/homelab.git "$FRAMEWORK"
git -C "$FRAMEWORK" checkout --detach "$FRAMEWORK_REVISION"
python3 -m venv "$WORK_ROOT/venv"
PYTHON="$WORK_ROOT/venv/bin/python"
"$PYTHON" -m pip install --require-hashes -r "$FRAMEWORK/requirements.lock.txt"
```

`FRAMEWORK_REVISION` is the exact selection quoted from this version's [phase workflow](../../.github/workflows/phase.yml); it is not a second version policy. Keep the checkout clean and confirm that selection when using another library version. `STACK_REVISION` records the actual library revision you are testing.

## 2. Read the complete example

The source entrypoint is [site.example.yaml](../../site.example.yaml). It selects:

- One synthetic Proxmox context, storage pool and named services network.
- One [guest definition](../../examples/minimal/guests/resolver.yaml), using the `base` template and one explicit NIC/control interface.
- One [app instance](../../examples/minimal/apps/recursive_dns.yaml), selecting `unbound` independently of Pi-hole.
- Explicit deployment/download/recursive-DNS policy and one ordered internet address group.

The app's container DNS listeners are private. TCP and UDP publish on the guest's loopback port5335; this example does not advertise a LAN DNS server. The named context DNS endpoint is a value, not an inferred preparation wait.

## 3. Validate without a target

Keep the same shell and variables:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py"   --stack "$STACK" --site "$STACK/site.example.yaml" --check
"$PYTHON" "$FRAMEWORK/blueprints/workflows.py"   --stack "$STACK" --site "$STACK/site.example.yaml" --check
```

Expect successful source validation and `3 generated workflows; 0 changed.` from the generator check. `--check` verifies the committed files; it does not regenerate or deploy them.

Synthetic addresses, empty SSH-key selections and example paths are deliberate. Do not use `--admit` as a way to deploy this example. Real source admission requires concrete qualified site bindings and will reject these synthetic values.

## 4. Create and inspect one packet

The output file must not already exist. Its parent is a new disposable directory:

```sh
PACKET_ROOT="$(mktemp -d)"
PACKET_ROOT="$(cd "$PACKET_ROOT" && pwd -P)"
PACKET="$PACKET_ROOT/resolver.json"
"$PYTHON" "$FRAMEWORK/blueprints/compile.py"   --stack "$STACK" --site "$STACK/site.example.yaml"   --guest resolver --output "$PACKET"
"$PYTHON" - "$PACKET" <<'PYCODE'
import json, pathlib, sys
packet = json.loads(pathlib.Path(sys.argv[1]).read_text())
print(packet['schema'])
print(packet['guest'])
print(sorted(packet['files']))
PYCODE
```

Expect `homelab-component-guest-deployment-v1`, guest `resolver`, and the generated file names. The packet is generated JSON; authored source remains YAML. A second write to the same output path refuses rather than replacing it.

## 5. Try a different composition

The [alternate layout](../../examples/site.second.yaml) contains three guests, three independently named resolver instances and a public-image HA instance without Node-RED or database/broker/identity integrations:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py"   --stack "$STACK" --site "$STACK/examples/site.second.yaml" --check
```

The source compiles without providing a HomeLab credential or host. It does not prove that those services have been installed. Follow [Compose a site](compose-a-site.md), [interfaces](multiple-interfaces.md) and [connections](connect-apps.md) to understand the bindings before replacing synthetic facts.

For actual deployment, use a consuming site's qualified source and protected CD prerequisites. This tutorial grants no target action and does not create state, accounts, DNS records or firewall access.
