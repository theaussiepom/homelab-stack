# HomeLab application library

Compose independent applications into Debian LXC guests on Proxmox. Choose a profile, give each app a stable identity, and bind its networks, storage and integrations in a site. The shared framework compiles that source and drives OpenTofu infrastructure and Ansible configuration through protected CD.

You can run a standalone resolver, place several apps together, or separate them across guests. There is no fixed guest list and no mandatory Home Assistant/Node-RED, Pi-hole/Unbound or MQTT/Explorer bundle.

## Start here

- **New to the project:** [Start here](docs/start-here.md), then [compile your first configuration](docs/guides/first-configuration.md). The tutorial needs no Proxmox host, Docker daemon or credentials.
- **Choose an app:** [Browse all 21 profiles](docs/reference/README.md), including explicit public-image and MariaDB-admin variants.
- **Build a site:** [Compose a site](docs/guides/compose-a-site.md), [bind interfaces](docs/guides/multiple-interfaces.md), and [connect apps](docs/guides/connect-apps.md).
- **Maintain or extend it:** [Images and updates](docs/guides/images-and-updates.md), [contributing](docs/contributing.md), [tests](docs/testing.md), and [troubleshooting](docs/troubleshooting.md).

The [documentation index](docs/README.md) links the full guide and reference suite.

## What is in the library?

Home Assistant, Node-RED, Bitwarden, CloudBeaver, Pi-hole, Unbound, Authentik, InfluxDB, Traefik, MariaDB, Zabbix, Mosquitto, MQTT Explorer, Music Assistant, PegaProx, PostgreSQL, Zigbee2MQTT and WiNet. Supporting containers stay with their owning app. Profile pages state fresh/update limits; a listed product is not a promise of unrestricted first-install or hardware support.

| Source | Owns |
| --- | --- |
| [stack.json](stack.json) | Profile/template registration, named software, runtime, health and policy declarations |
| [apps/](apps/) | Complete reusable app profiles |
| [templates/](templates/) | Guest defaults |
| [images.json](images.json) | Authoritative image selections and policies |
| [assets/](assets/) | Hash-bound public vendor material |
| [site.example.yaml](site.example.yaml) | Small standalone Unbound source example |
| [examples/site.second.yaml](examples/site.second.yaml) | Different placement, repeated resolvers and independent HA |

The library owns reusable choices. A consuming site owns actual allocations, trust, credentials, identities and access policy. The framework owns validation, rendering and deployment capabilities. See [the model](docs/concepts.md) and [working agreement](AGENTS.md).

## What a successful source check means

A successful compiler check proves the selected declarations can be resolved. It does not create a guest, load private credentials, change firewall/routing policy or verify a running service. The examples use synthetic addresses and are intentionally unsuitable for real deployment admission.

Ordinary updates preserve current receipts, state, private material and data ownership. Unsupported initialization, identity conflicts and unresolved holds refuse. Deployment and service verification belong to the consuming site's separately authorized protected CD path.
