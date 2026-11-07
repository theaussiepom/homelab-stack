# Design your homelab

[Documentation index](../README.md) · [Application catalogue](../reference/README.md)

Turn a list of services you want into your own checked configuration for Debian 13 LXC guests on Proxmox. You will choose supported applications, place them on guests, collect your host facts, edit a complete local copy, and inspect what the compiler would prepare. The first result is a valid configuration and a concrete list of deployment prerequisites; these commands do not contact Proxmox or install a service.

You need basic YAML editing, Git, and Python 3.12 or 3.13 with `venv` and pip. You can complete the exercise with synthetic values before you have a Proxmox host. Keep your eventual real configuration in your own private site repository, separate from this reusable library.

## 1. Start with the services you want

Write down the outcome first, then choose the matching [profile](../reference/README.md). A **profile** is the library's reusable application recipe; an **instance** is your named selection of it; a **guest** is the LXC container that runs one or more instances. A guest **template** supplies defaults such as memory and security, without selecting applications. Your **site** connects these choices to a particular host, network and storage pool.

| Desired outcome | Supported starting choice | What you must know before selecting it |
| --- | --- | --- |
| Learn recursive DNS configuration without existing application data | [Unbound](../reference/apps/unbound.md), `lifecycle: fresh` | Can create its configuration from empty. It publishes only `127.0.0.1:5335` inside its guest; it is not a LAN-facing DNS service. This is the first exercise below. |
| Run Home Assistant with a new configuration | [Home Assistant public](../reference/apps/homeassistant-public.md), `lifecycle: fresh` | Can create its configuration subdirectory on a declared volume, provided the subdirectory does not already exist. [Add it below](#7-add-home-assistant-if-you-want-it); no MQTT, database or Node-RED is required. Vendor onboarding and integrations still happen after deployment. |
| Give LAN clients filtering DNS | [Pi-hole](../reference/apps/pihole.md) with an explicitly selected upstream | Needs prepared Pi-hole configuration; the library does not provide a complete procedure for a new installation on an empty host. The [complete local DNS composition](../examples/local-dns.md) shows how to configure an installation that HomeLab already manages and connect it to Unbound on the same guest. Do not use that retained example as a fresh-install recipe. |
| Run a different supported service | Its [catalogue entry](../reference/README.md#complete-registered-catalogue) and complete example | Read **First installation**, required storage/secrets/connections, and **Later deployments** before choosing it. A registered profile can require prepared data, accounts or hardware. |

This library targets supported Debian LXC application profiles. It is not a general VM installer, a Home Assistant OS image installer, or a way to run any arbitrary Compose file. A missing profile or capability needs a separately implemented and tested contract; see [contributing](../contributing.md).

`fresh` permits the profile's supported creation when its resource is absent and remains appropriate for later updates to the same HomeLab-managed instance. `retained` requires genuine existing HomeLab ownership and refuses creation. Neither imports an unrelated installation. Choose these policies for the actual starting state, not to get past a refusal; see [installation](installation.md#first-installation).

## 2. Decide which applications share a guest

Begin with one `resolver` guest and one `recursive_dns` instance. The optional Home Assistant step adds a second guest, `home-app`, and instance, `home`. Giving services separate guests separates their resource allocation and deployment jobs. Sharing a guest reduces the number of guest allocations but combines their capacity and guest-level maintenance effects.

| Layout | Source choices | Result to expect |
| --- | --- | --- |
| Resolver alone | Select `resolver` and `recursive_dns` | One LXC allocation and a loopback resolver. |
| Resolver and Home Assistant separately | Add `home-app` and `home` | Two allocations; HA advertises the second guest's address on port 8123. There is no connection between the apps. |
| Both on one new guest | Use the [shared-guest variation](#8-try-a-different-supported-layout) | One allocation with the combined resource budget and HA data volume; HA uses that guest's address and DNS remains loopback-only. |

The compiler checks combined memory reservations, sockets, data bindings and identities. Passing those checks is not a measurement of your workload: choose capacity for expected use. The [placement guide](shared-and-separate-guests.md) explains repeatable profiles and fixed listening addresses and ports. These variations design new instances; they do not migrate an installed app between guests.

## 3. Collect your Proxmox facts

Keep the synthetic values for an offline rehearsal. For your own configuration, collect the following from your Proxmox inventory and network/storage records before editing. Proxmox page labels can vary; the exact identities matter more than the UI route. No discovery or allocation happens during compilation.

The file names below are relative to the copy you create in step 4. `lab`, `services` and `local` are your source lookup names, not literal Proxmox names. For example, `root_storage: local` selects the `storage.local` entry, whose `pool` must be a real Proxmox storage ID.

| Fact to obtain and where to find it | File and exact field to edit | Required relationship |
| --- | --- | --- |
| Target node name from the Proxmox resource tree | `site.yaml`: `contexts.lab.node` | Choose the node on which these guests should run. |
| Proxmox API host/address from your management endpoint and its verified certificate | `site.yaml`: `external_endpoints.proxmox.address` | Keep the selected `https` protocol and port `8006`; use a host/address without a URL scheme or path. |
| Existing DNS server reachable during guest preparation, from router/DHCP/network records | `site.yaml`: `external_endpoints.resolver.address` | Use an IPv4 DNS endpoint on port 53. Do not point this at the new loopback-only Unbound instance. |
| Deployment runner's source IPv4 as seen by the guest network | `site.yaml`: `external_endpoints.runner.address` | The deployment policy allows inbound SSH from this value. NAT/routing can make it differ from the runner's local address. |
| Existing bridge, from the node's network configuration; subnet, gateway and VLAN from your network plan | `site.yaml`: `networks.services.bridge`, `.cidr`, `.gateway`, `.vlan` | CIDR uses the network address, such as `198.18.20.0/24`. Set `vlan: null` for an untagged network, or the actual tag. The source does not create the bridge, VLAN, router or DHCP reservation. |
| Storage ID enabled on the chosen node for LXC root/data volumes, from Datacenter storage and node storage inventory | `site.yaml`: `storage.local.pool` | This is the Proxmox storage ID, not a filesystem mount path. Check capacity and supported content on the node. |
| Existing Debian 13 LXC template volume ID, from the node storage's CT templates | `guests/resolver.yaml`: `template_file_id` | Use the complete `<storage-id>:vztmpl/<filename>` identity. An ISO or a guest-template name such as `base` is a different thing. |
| Unused VMID checked across the cluster, chosen hostname and unused MAC | `guests/resolver.yaml`: `identity.vmid`, `identity.hostname`, `interfaces.primary.mac` | VMID and MAC must be unique; a hostname starts with a lowercase letter and uses lowercase letters, digits or hyphens. Reserve these identities before deployment. |
| Unused/reserved guest IPv4 within the chosen subnet | `guests/resolver.yaml`: `interfaces.primary.address.value` | Keep `mode: static` and `default_route: true` for this one-NIC exercise. The network supplies its gateway. Check your address inventory; successful compilation cannot detect an address already used on the LAN. |
| Desired capacity and host headroom | `guests/resolver.yaml`: optional `resources` | Omission inherits the [base template](../reference/templates/base.md). Override only the required fields; values use cores, MiB and GiB. Selected app reservations plus the OS reserve must fit. |
| Optional HA allocation, using the same sources above | `guests/home-app.yaml`: node-independent identity, template, NIC, `resources` and `volumes.apps` | Its VMID, MAC and IP must differ from the resolver. The data volume uses `storage: local`; its `path` is inside the guest. |

The [framework context](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/contexts.md), [network](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/networks.md), [guest](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/guests.md) and [storage](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md) references give the exact types and limits. Use [multiple interfaces](multiple-interfaces.md) if your desired layout needs more than this one-NIC design.

Trust, credentials, backup storage and runner setup are also required before deployment, but need not exist to finish the offline exercise. [Step 9](#9-finish-with-a-deployment-preparation-list) maps every remaining placeholder to its owner so you can finish the configuration without inventing those facts.

## 4. Make a complete configuration of your own

Start a Bash-compatible shell in the root of a clean, reviewed library checkout at the revision whose documentation you are reading. The following setup defines all variables used below, fetches the framework selected by this library's [phase workflow](../../.github/workflows/phase.yml), and installs its hash-locked Python dependencies in a new local environment. If you already completed [First configuration](first-configuration.md#1-prepare-an-isolated-source-environment) in this same shell, reuse its variables and skip this setup block.

```sh
STACK="$(pwd -P)"
STACK_REVISION="$(git rev-parse HEAD)"
FRAMEWORK_REVISION=52913d4ba03f85e7d734a85b08c93e73f320455d
WORK_ROOT="$(mktemp -d)"
WORK_ROOT="$(cd "$WORK_ROOT" && pwd -P)"
FRAMEWORK="$WORK_ROOT/homelab"
test -f "$STACK/stack.json"
git clone --no-checkout https://github.com/theaussiepom/homelab.git "$FRAMEWORK"
git -C "$FRAMEWORK" checkout --detach "$FRAMEWORK_REVISION"
python3 -m venv "$WORK_ROOT/venv"
PYTHON="$WORK_ROOT/venv/bin/python"
"$PYTHON" -m pip install --require-hashes -r "$FRAMEWORK/requirements.lock.txt"
```

The revision above quotes this version's workflow; the workflow remains the authority. Keep `STACK_REVISION` with your configuration notes. Do not combine the example with an unrelated framework checkout.

Now create a separate working copy. The directory holds the complete maintained source, including the optional HA files; it has no references back into the library's examples directory.

```sh
SITE_ROOT="$(mktemp -d)"
SITE_ROOT="$(cd "$SITE_ROOT" && pwd -P)"
cp -R "$STACK/examples/personalisation/." "$SITE_ROOT/"
printf 'Edit your configuration in %s\n' "$SITE_ROOT"
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$SITE_ROOT/site.yaml" --check
```

Expect `All component guests compile offline; no credentials or targets accessed.` before making changes. This checks the copied files, not the library's starter. Keep this directory for the exercise; after review, move the whole directory into your private site repository so temporary-directory cleanup cannot remove your authored work.

| Copied file | Job in your configuration |
| --- | --- |
| [site.yaml](../../examples/personalisation/site.yaml) | Shared provider/network/storage/policy facts and the maps selecting guest/app source files. |
| [guests/resolver.yaml](../../examples/personalisation/guests/resolver.yaml) | Your resolver's LXC identity, network, template and policy selections. |
| [apps/recursive_dns.yaml](../../examples/personalisation/apps/recursive_dns.yaml) | One fresh Unbound instance assigned to `resolver`. |
| [guests/home-app.yaml](../../examples/personalisation/guests/home-app.yaml) | Optional separate HA guest, resources and provider data volume. It is not selected yet. |
| [apps/home.yaml](../../examples/personalisation/apps/home.yaml) | Optional fresh public HA instance and config-volume binding. It is not selected yet. |

Every `source:` path is relative to the directory containing `site.yaml`. Each selected source file is complete and typed with its own `schema` and `kind`; it is not a partial overlay. Keep the whole directory tree when moving the site. See [source composition](compose-a-site.md#4-keep-source-files-complete) for other supported splits.

## 5. Put your choices into the source

Open `site.yaml` and `guests/resolver.yaml` in your editor. Replace the fields from your worksheet, keeping the surrounding structure. Keep the source lookup keys (`lab`, `services`, `local`, `resolver`, `recursive_dns`, `primary`) initially: changing the host facts does not require renaming these keys. The app keeps `service: {scope: guest-loopback}` and `private: {scope: app-network, network: default}`; changing those to a physical NIC would exceed this profile's support.

For a second offline practice configuration, make the following exact edits. These are alternative synthetic facts, not recommended allocations for a real network; you can use your collected facts instead.

| File | Field | Practice replacement |
| --- | --- | --- |
| `site.yaml` | `contexts.lab.node` | `practice-node` |
| `site.yaml` | `networks.services.cidr` | `198.19.30.0/24` |
| `site.yaml` | `networks.services.bridge` | `vmbr-practice` |
| `site.yaml` | `networks.services.vlan` | `null` |
| `site.yaml` | `networks.services.gateway` | `198.19.30.1` |
| `site.yaml` | `external_endpoints.runner.address` | `198.19.30.2` |
| `site.yaml` | `storage.local.pool` | `practice-pool` |
| `guests/resolver.yaml` | `identity.vmid` | `810` |
| `guests/resolver.yaml` | `identity.hostname` | `practice-resolver` |
| `guests/resolver.yaml` | `template_file_id` | `practice:vztmpl/debian.tar.zst` |
| `guests/resolver.yaml` | `interfaces.primary.mac` | `02:00:00:30:00:10` |
| `guests/resolver.yaml` | `interfaces.primary.address.value` | `198.19.30.10` |

### If you want your own names

Names are references, and some become generated runtime identities. Keep the original names through steps 7–8 so their fragments can be copied literally, then make any naming changes before first deployment. For example, rename guest key `resolver` to `dns-box` under `site.yaml` → `guests`, then change every selected app assigned to it (`apps/recursive_dns.yaml` and, in the shared layout, `apps/home.yaml`) → `guest` to `dns-box`. The leaf filename can stay `guests/resolver.yaml`. Use `--guest dns-box` in the packet command. To rename the app, change its `site.yaml` → `apps` key; any [connections](connect-apps.md), policy endpoint bindings or exposures that select that app must use the new key as well. The resolver-only baseline has none.

If you rename `services`, update every guest NIC's `network`; if you rename `local`, update `root_storage` and every selected volume's `storage`; if you rename `primary`, update `control_interface` and app physical role bindings such as HA's `interfaces.web.interface`. A `lab` context rename also changes the guest, network and storage `context` fields. Renaming an already installed instance is not an ordinary way to relocate or adopt it.

## 6. Check the configuration and inspect its result

Compile your edited copy after each coherent change:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$SITE_ROOT/site.yaml" --check
```

Then generate a packet: a JSON file containing the deployment inputs for the guest you chose. The output directory is new on each run because packet writes deliberately refuse an existing output file. If you renamed the guest, change `GUEST` to its site map key.

```sh
GUEST=resolver
PACKET_ROOT="$(mktemp -d)"
PACKET_ROOT="$(cd "$PACKET_ROOT" && pwd -P)"
PACKET="$PACKET_ROOT/$GUEST.json"
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" --stack "$STACK" --site "$SITE_ROOT/site.yaml" --guest "$GUEST" --output "$PACKET"
"$PYTHON" - "$PACKET" <<'PYCODE'
import json, pathlib, sys
packet = json.loads(pathlib.Path(sys.argv[1]).read_text())
config = json.loads(packet['files']['site.json'])
runtime = json.loads(packet['files']['component-runtime.json'])
print('Guest:', packet['guest'])
print('Provider:', config['site'])
print('Allocation:', {key: config['guest'][key] for key in
                     ('vmid', 'hostname', 'memory_mib', 'storage_id', 'template_file_id')})
print('NICs:', config['guest']['interfaces'])
print('Volumes:', config['guest']['volumes'])
print('Network rules:', config['guest']['rules'])
print('Phases:', config['deployment']['phases'])
for name, app in runtime['applications'].items():
    print('App:', name, 'profile:', app['profile'])
    print('Role addresses:', app['role_addresses'])
    print('Listeners:', app['listeners'])
    print('Data:', {role: value['source'] for role, value in app['storage_paths'].items()})
PYCODE
```

Compare the provider node, VMID, hostname, storage, template and NIC values against your worksheet. With the practice edits, the resolver should use node `practice-node`, VMID `810`, pool `practice-pool` and address `198.19.30.10`. Its phases are `preparation`, then `recursive_dns`. Both DNS listeners publish on `127.0.0.1:5335`, not the NIC address; its data bindings are empty. Unedited source instead has VMID `610` and address `198.18.20.10`. Review the policy selections in `site.yaml` as well: the example permits runner SSH, outbound package/image HTTP(S), and outbound recursive TCP/UDP DNS. It does not create upstream network access.

Generated packets contain runtime documents and, when personalised, private path/allocation metadata. Keep them local and inspect them; edit the authored YAML rather than the generated JSON. A successful result proves that your chosen source resolves and generates deployment files with these revisions. It does not prove host capacity, trust files, routing, data ownership or a running service.

### Fix a refused configuration

| Symptom or diagnostic | What to inspect | Supported correction |
| --- | --- | --- |
| `component.source` after copying or moving the site | The file named by `source:` and its directory tree | Copy all selected leaves under the site directory, preserve case and safe relative paths, and keep each leaf's schema/kind. |
| `component.invalid` after changing a subnet | `site.yaml` → `networks.services.cidr` and `guests/resolver.yaml` → `interfaces.primary.address.value` | Use a canonical network CIDR and an unused guest address inside it; also update the gateway. This resolver diagnostic has no field path, so compare the last edits to the worksheet. |
| `component.invalid` after binding Unbound's `service` to `primary` | `apps/recursive_dns.yaml` → `interfaces.service` | Restore `scope: guest-loopback`; use the prepared Pi-hole route when you need client DNS. This is another pathless resolver diagnostic, not a different named interface error. |
| `component.memory-budget` after adding HA | The containing guest's `resources.memory_mib`, selected app reservations and OS reserve | Allocate sufficient supported capacity, or separate the apps. The guide's HA example allocates 3072 MiB. |
| `component.storage-initialization-volume` while lowering fresh HA | `apps/home.yaml` → `storage.config` and its guest's `volumes.apps` | Bind a nonempty `subpath` under the declared provider volume, as in the maintained example. A root path or empty subpath cannot replace that initializer contract. |
| Generic `Component compilation refused; no credentials or targets accessed.` on packet output | Whether `$PACKET` already exists and whether `GUEST` matches a selected map key | Use a new output path and the actual guest key; preserve the earlier packet for comparison. |

The documentation tests exercise the specific invalid-address, interface, capacity and initializer cases with the selected compiler. Other symptoms may have a different cause; follow [troubleshooting](../troubleshooting.md) and inspect the reported phase before editing a different field.

## 7. Add Home Assistant if you want it

For a fresh Home Assistant configuration, choose `homeassistant-public`. The similarly named `homeassistant` profile has different prepared-input requirements. The public variant creates a configuration subdirectory only if it is absent and HomeLab has verified ownership of the containing volume. It does not change the file owner of an existing directory tree or import an old HA directory. Read its [first installation contract](../reference/apps/homeassistant-public.md#first-installation).

In `site.yaml`, replace the existing `guests` and `apps` maps with the following two maps; leave all other root fields in place. These are **site map replacements**, not a whole site or additional duplicate YAML keys. Both optional files were copied in step 4.

### Separate-guest selections

```yaml
guests:
  resolver:
    source: guests/resolver.yaml
  home-app:
    source: guests/home-app.yaml
apps:
  recursive_dns:
    source: apps/recursive_dns.yaml
  home:
    source: apps/home.yaml
```

Edit `guests/home-app.yaml` using the same worksheet: choose its own VMID, hostname, MAC and address; use your template file ID. If you followed the practice changes, set VMID `811`, hostname `practice-home`, MAC `02:00:00:30:00:11`, address `198.19.30.11`, and template `practice:vztmpl/debian.tar.zst`. It inherits the shared `lab`, `services` and `local` facts from your site. The complete guest already allocates 3072 MiB, an 8 GiB root and a 4 GiB data volume mounted at `/srv/example/apps`. You can choose a supported data path and capacity for a new guest; keep `apps/home.yaml` → `storage.config.volume: apps` and `subpath: homeassistant` connected to that volume.

Run step 6 again, then run its packet block with `GUEST=home-app`. Expect `preparation`, then `home`; a web listener on host port `8123`; and config data at `/srv/example/apps/homeassistant`. The printed `web` role address follows the guest's primary NIC (`198.19.30.11` for the practice values). A wildcard host listener can cover more than one NIC; a role binding is not an ingress firewall rule. Add the following narrow browser policy to finish a source design for direct HTTP access from one selected client.

### Browser policy

Add this **named network-policy entry** beneath the existing `site.yaml` → `policies.network` map, alongside `deployment`, `downloads` and `recursive_dns`. It allows one synthetic client's source IPv4 to the selected HA endpoint. Replace `198.18.20.50` with that client's actual source address as seen by the guest; for the practice subnet use `198.19.30.50`. Do not replace the whole `policies` map.

```yaml
home_browser:
  rules:
  - direction: in
    proto: tcp
    source: 198.18.20.50
    destination:
      endpoint: web
    port:
      endpoint: web
    interface: lan
    comment: Home Assistant from selected browser
```

### Browser policy binding

Append the following **one-item list fragment** to `guests/home-app.yaml` → `network_policy`, keeping its existing deployment/download/DNS entries. `web` and `lan` are local roles in this policy; they are bound to the selected app endpoint and this guest's primary NIC here. If you renamed the HA app or NIC, use those names.

```yaml
- policy: home_browser
  interfaces:
    lan: primary
  endpoints:
    web:
      app: home
      endpoint: web
```

Recompile and inspect the `home-app` packet using step 6. Under `Network rules`, find `Home Assistant from selected browser`: expect inbound TCP from your chosen client, destination equal to HA's primary address with a `/32` host suffix, destination port `8123`, and interface `net0`. The endpoint reference makes the destination follow the chosen HA guest. With practice values, the desired browser URL after authorized deployment is `http://198.19.30.11:8123`. Router reachability, upstream firewall policy and native enforcement still need their own verification; compilation does not turn any of them on. This direct HTTP exercise does not configure HTTPS, managed DNS, MQTT/recorder, USB or mDNS. Use the [profile's supported bindings](../reference/apps/homeassistant-public.md) and [connection guide](connect-apps.md) when those are part of your goal.

To keep only HA before first deployment, remove `recursive_dns` from the site's `apps` map and `resolver` from its `guests` map. Keep the existing external preparation DNS endpoint. Recheck and generate `home-app` again; there is no required DNS-app companion.

## 8. Try a different supported layout

To place the two fresh apps on a single new guest, start from step 7, remove only `home-app` from `site.yaml` → `guests`, and change `apps/home.yaml` → `guest` from `home-app` to `resolver`. Keep both app selections. Append the [browser policy binding](#browser-policy-binding) to `guests/resolver.yaml` → `network_policy` so access follows the new containing guest. Add the following fields to `guests/resolver.yaml`, replacing any existing `resources` or `volumes` map rather than duplicating the keys. It is a **guest fragment**, not a complete guest.

### Shared-guest additions

```yaml
resources:
  cpu_cores: 2
  memory_mib: 3072
  root_gib: 8
  os_reserve_mib: 256
volumes:
  apps:
    storage: local
    slot: 0
    path: /srv/example/apps
    size_gib: 4
```

Run step 6 with `GUEST=resolver`. Expect a single guest packet containing both `recursive_dns` and `home`, 3072 MiB and the config volume. HA's printed `web` address and the browser rule's destination now follow the resolver's primary NIC (`198.19.30.10` for the practice values), while Unbound still publishes loopback port 5335. The apps still have no connection to each other and neither waits for the other to become ready. Deployment phase order within the generated packet is not evidence that one application uses the other.

This verifies a materially different supported source layout. For repeated resolvers with distinct loopback ports and multiple networks, continue with [shared and separate guests](shared-and-separate-guests.md) and the maintained [alternate site](../../examples/site.second.yaml). Each added app needs an independent identity, compatible sockets, sufficient capacity and its own required data/connection bindings.

## 9. Finish with a deployment preparation list

You now have your own coherent source, its copied dependencies, the selected source revisions and inspectable packets. If you used real facts, this is a personalised configuration; if you used the practice values, it is a repeatable rehearsal. Preserve the source and review it before completing the following inputs in your private site repository.

| Remaining input | Where it belongs | Evidence needed before deployment |
| --- | --- | --- |
| Provider trust and SSH host trust | `site.yaml` → `contexts.lab.trust.ca_file`, `.known_hosts` | The actual CA certificate and known-hosts file must exist on the controller with the required file ownership and permissions. Verify that they identify the intended provider and hosts; a path alone does not establish trust. |
| Provider API credential and controller SSH key | `site.yaml` → `secret_sources.api.path`, `secret_sources.ssh.path`; referenced by `contexts.lab.credentials` | Protected credential files must grant the required API and SSH permissions. Do not paste credential values into YAML or this library. See [secrets](../secrets.md). |
| Guest login public key and existing protected VMIDs | `site.yaml` → `contexts.lab.ssh_public_keys`, `.protected_guests` | Genuine Ed25519 public key selection and the actual protected allocation list. An empty public-key list is only an offline fixture. |
| State files and backups | `site.yaml` → `contexts.lab.paths.state_root`, `.backup_directory`, `.backup_mount`, `.backup_source` | The state directory must already be owned by the controller account. Check that the backup mount uses the declared source and that its destination directory meets the required ownership, permissions and access checks. These paths are on the controller, not in a guest data volume. |
| Node, guest template, storage pool, network interfaces and allowed traffic | The worksheet fields, `policies.network` and each guest's `network_policy` | Check that the node resources exist and the selected identities are reserved. Preparation must be able to reach DNS, the runner must have its required access, and packages and images must be reachable. Declare the intended client access explicitly. Rules do not create router routes or upstream firewall permissions. |
| Application-specific data, accounts and integrations | The selected profile's storage, secrets, connections and properties | Its **First installation** requirements and, after deployment, vendor onboarding and checks of the actual endpoint, authentication and integrations. Retained resources additionally require genuine matching ownership records. |
| Reviewed source selection and execution setup | Your deployment repository's exact framework and library revisions, generated workflows, protected environment, runner and forwarded secrets | Follow the selected framework's [deployment prerequisites](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/operations/deployment.md#prerequisites) and its [compiler/workflow commands](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/cli.md). No consumer runner or universal deployment trigger is supplied by this example. |

Continue with [preparation, first installation and service verification](installation.md). Source admission, an authorized protected deployment and real service verification are separate steps. This guide has not performed any of them on your host. Keep `fresh` for later updates to the same HomeLab-managed instance and use [images and updates](images-and-updates.md) when changing selected software or defaults.
