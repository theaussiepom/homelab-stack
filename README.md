# HomeLab stack

This library describes independent applications and reusable guest templates.
A consuming site chooses instances, placement, interfaces, storage and policy.
The selected framework resolves that composition and drives the existing
OpenTofu, Ansible and deployment workflow.

The library has no implicit guest set. Applications can share a guest or run on
separate guests. One deployment job represents each selected guest, with short
application steps inside it.

## Source layout

- `stack.json` indexes the component library and named shared declarations.
- `apps/` contains independent application profiles.
- `templates/` contains reusable resource, startup and security defaults.
- `images.json` owns image selections and their declared policies.
- `assets/` contains digest-checked, byte-preserved public vendor material.
- `site.example.yaml` is a small synthetic standalone Unbound starter.
- `examples/site.second.yaml` uses different placement and repeated instances.

Examples use reserved addresses and example identities. They demonstrate source
contracts; they do not commission a context or supply native acceptance evidence.
Real allocations, trust, secrets, image archives and admission records belong to
the consuming site.

## Independent applications

| Profile | Owned application and supporting containers |
| --- | --- |
| `homeassistant` | Home Assistant |
| `node_red` | Node-RED |
| `bitwarden` | Bitwarden |
| `cloudbeaver` | CloudBeaver and its authentication gateway |
| `pihole` | Pi-hole |
| `unbound` | Unbound |
| `authentik` | Authentik server, worker and dedicated Redis |
| `influxdb` | Native InfluxDB |
| `traefik` | Traefik |
| `mariadb` | Native MariaDB |
| `zabbix` | Zabbix server and web frontend |
| `mqtt` | Mosquitto broker |
| `mqtt_explorer` | MQTT Explorer and its authentication gateway |
| `music_assistant` | Music Assistant |
| `pegaprox` | PegaProx |
| `postgresql` | Native PostgreSQL |
| `zigbee2mqtt` | Zigbee2MQTT |
| `winet` | WiNet |

Pi-hole does not force Unbound. HA does not force Node-RED or database, MQTT,
metrics, identity or ingress integrations. WiNet does not force Zigbee or a USB
capability. Selected connections supply their actual requirements.

The explicit `homeassistant-public` and `node_red-public` variants select official
public images for new instances. They use the same independent adapters and
shared resource/health declarations. Retained profiles keep their declared
archive selections. See [public image options](docs/public-images.md).

## Compose a site

A site declares contexts, named networks/storage, guests and app instances.
Interface maps select provider slots explicitly; addresses and VLANs are declared
once on the site side. App roles refer to those interfaces. Connections name an
app and a listener endpoint, rather than copying an address or inventing a wait.

The minimal example selects Unbound with a private container listener and an
explicit guest-loopback publication. A second instance can choose another
supported publication port. Real listener, service, data, device and credential
ownership conflicts refuse compilation.

Application helpers remain owned by their app. A shared Compose project is
explicit, with stable per-app service/network identities. Updating a GUI does not
implicitly recreate another app's broker or data.

Named network policy fragments are explicitly selected and bound by the site.
Connections never create firewall rules, broaden client access or establish
isolation. Existing policy rows retain their order and comments.

## Fresh and retained state

`lifecycle: fresh` permits creation of an absent owned resource through the normal
pipeline. It does not adopt an existing resource or fabricate commissioning
proof. An unsupported initialization path refuses explicitly.

`lifecycle: retained` preserves exact guest, runtime, mount, data-owner and
credential identities. Display names are cosmetic. Typed admission references
select the original immutable evidence; raw custody strings preserve their exact
bytes and newlines. Existing holds, trust and failure rules remain enforced.

Storage bindings distinguish additional provider volumes from declared root
filesystem data paths. Neither declaration invents observed ownership, relocates
data or authorizes a broad chown. Accounts are explicit create-once selections;
there is no password reuse, rotation or inferred privilege grant.

## Root Zabbix selection

```yaml
zabbix:
```

This selects the unique configured Zabbix server capability and one agent phase
per selected guest. The site's server app and guest retain explicit identities
and bindings. If several server apps exist, select one with `zabbix: {server: ID}`.
Omission leaves the feature unselected. Monitoring workloads derive from the
actual selected applications.

## Validate and generate

Use the selected framework's safe reader, compiler and workflow generator.
Component workflow generation always names the actual site or synthetic starter:

```sh
python3 "$FRAMEWORK/blueprints/compile.py" --stack . --site site.example.yaml --check
python3 "$FRAMEWORK/blueprints/workflows.py" --stack . --site site.example.yaml --check
```

The generic `phase.yml` contains the sole immutable framework selection. A
consumer's immutable `HOMELAB_STACK_SOURCE` locator selects this library checkout;
it does not select the starter's guest graph. The framework generates the actual
consumer graph from its site, including selected app steps, dependency edges and
explicit secret subsets. Default `disabled: []` selects the composition; required
dependencies and immutable custody closure still apply to disabled selections.

Source qualification includes distinct layouts, standalone and repeated apps,
fresh/update contracts, generated workflows, exact desired-state preservation,
coverage, boundaries, history, signatures, security and current source review.
Consumers own deployment authorization and actual service acceptance.
