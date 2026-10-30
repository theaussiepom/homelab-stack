# Set up and test locally

You need Git, Python 3.12+, and the framework's pinned Python requirements. Native
execution additionally needs the already admitted Linux runner with OpenTofu,
Ansible, trusted PVE CA, SSH known-hosts, shared persistent state and NAS recovery
mount. Do not run the phase runner on your laptop to test source changes.

DNS guest 6101 keeps DHCP allocation: `ipv4` is `dhcp`, `gateway` is null, and
`ipv4_endpoint` records the independently qualified assigned address and prefix.
The public `${addresses.dns}/24` endpoint is a synthetic fixture. The private site
must supply its qualified endpoint; this metadata does not request a static lease
or change DHCP. It keeps SSH, backend bindings and identity checks concrete.
Static NICs keep their existing `ipv4` CIDR without `ipv4_endpoint`.

1. Clone the stack and selected framework into sibling folders. Read the one
   framework SHA from `.github/workflows/phase.yml`, then check out that SHA in
   `../homelab`. A fork can change the workflow owner and revision deliberately.
2. Create a private site from `site.example.json`. Keep its actual `site.json`
   private and all credential values outside Git. Supply central values and only
   the overrides that differ. Lists replace whole lists.
3. Review all guest NICs, volumes, UID/GID and application requirements. The public
   network addresses are benchmark examples. The database backend bridges vmbr31,
   vmbr32 and vmbr33 have no uplink, host IP, gateway or UniFi VLAN by design.
   Firewall declarations do not prove host enforcement is enabled.
4. Run source checks. These commands never use target credentials:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r ../homelab/requirements.lock.txt
python3 ../homelab/blueprints/workflows.py --stack . --check
python3 ../homelab/blueprints/compile.py --stack . --site site.example.json --check
HOMELAB_FRAMEWORK=../homelab python3 -m unittest discover -s tests
```

When changing blueprint phases/display names or `stack.json` dependencies,
regenerate the checked-in workflow graph before reviewing the source diff:

```sh
python3 ../homelab/blueprints/workflows.py --stack .
python3 ../homelab/blueprints/workflows.py --stack . --check
```

This manages all thirteen composition workflows: `deploy.yml`, the eleven permanent
`guest-*.yml` files and `phase.yml`. Generation preserves the single deliberate
framework selection in `phase.yml` while checking its declarations and forwarding
contract. `ci.yml` keeps source validation.
The private site's optional disabled list and adopted stack pin remain explicit. There are
no compatibility formats or transition flags. Obsolete managed paths must be
removed explicitly; the generator never silently deletes another workflow.

Compilation also checks both guest firewalls for each published service route and
internal DNS connection. If an endpoint, NIC, DNS selection or firewall override
changes, update the corresponding narrow allowances together. External client
policies stay explicit. Passing compilation does not prove router reachability,
NAT behavior or enforcement on the target host.

Guests on the same declared node, bridge and VLAN need distinct IPv4 and MAC
identities. Credential binding also verifies that the retained private SSH key
matches an approved guest public key before infrastructure can run. Changes to
foundation runtime files recreate their application bundle; an unchanged copy
does not force recreation.

For an inspectable non-secret preview, add `--guest dns --output /tmp/dns-preview.json`
instead of `--check`. All guest packets participate by default; compilation itself
never deploys them. `--disabled '["zigbee2mqtt"]'` explicitly excludes that leaf
guest. The optional workflow input `disabled` uses the same JSON list and defaults
to `[]`. Dependencies of active guests cannot be disabled. Unknown names,
duplicates and the removed `--enabled` option are rejected.
`--admit` additionally requires selected guest dependency closure, prerequisite
acceptance, real keys, writer fencing and removal of image/runtime placeholders.
Only the private workflow uses that admission path. Compiling a preview does not
prove its target state, packages, network, health checks or credentials.

The image entries retain the source selection. A null tag means no tag was recorded;
the digest remains authoritative. HA/Node-RED custom image entries are placeholders
until the private site supplies the original local image IDs and verified archives.
Bitwarden retains its existing operator-selected latest policy and separately checks
the observed image ID. Do not change image policy as part of stack adoption.

Local commits use the same staged security guard and SSH signing policy as the
framework. Configure `.githooks` as `core.hooksPath`, supply gitleaks 8.30.1 through
`hooks.gitleaksPath` or `GITLEAKS_BIN`, and use your existing signing identity.
The exact reviewed vendor-key fingerprints in `.githooks/reviewed-findings.json`
are public signing-key hashes, not secret exceptions. No scanner bypass is needed.

For report-only Python coverage of the stack suite against its selected framework:

```sh
python3 ../homelab/tools/measure_coverage.py --suite stack --stack . --output .work/stack-coverage
```

Use a fresh output directory and provide the pinned scanner through `GITLEAKS_BIN`.
The report includes this repository's source guards and the selected framework's
blueprint/application code, retaining unexecuted production files. CI enforces 100% line and branch coverage per production file and writes the
summary to the job log. Detailed reports remain temporary runner files and are not
uploaded as artifacts. The framework
README documents `--all` for every Python component across all three repositories.

Docker guest profiles inherit `restart: always` from the framework container policy.
Keep `restart` omitted to use that convention; the current stack has no overrides.
Native database guests use systemd rather than Docker.
