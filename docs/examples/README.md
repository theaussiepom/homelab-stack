# Complete examples

[Documentation index](../README.md)

These maintained examples use synthetic values. They compile with the selected framework, but do not describe an installed site, include real credentials or verify a running service.

| Scenario | Complete source | What it establishes |
| --- | --- | --- |
| Design and personalise your own site | [Design your homelab](../guides/design-your-homelab.md), [complete copy](../../examples/personalisation/) | A self-contained fresh resolver source, exact fact-to-field edits, optional fresh HA and separate/shared guest layouts |
| Standalone recursive resolver | [site.example.yaml](../../site.example.yaml), [guest](../../examples/minimal/guests/resolver.yaml), [app](../../examples/minimal/apps/recursive_dns.yaml) | One Unbound without Pi-hole; base defaults; loopback publication; explicit policy |
| Different placement and repeated apps | [site.second.yaml](../../examples/site.second.yaml), [guest/app leaves](../../examples/second/) | Three guests, repeated resolvers with distinct publications, HA without Node-RED or unselected integrations |
| Connect filtering and recursive DNS | [Local DNS worked source](local-dns.md) | Complete synthetic retained composition, named connection/exposure and explicit same-guest readiness; no data adoption/initialization claim |

Use the design journey for your own source. Run the standalone and alternate examples directly using [First configuration](../guides/first-configuration.md). The local DNS page defines its source files and commands. Reference pages use clearly labelled app/property fragments and link these complete examples; a fragment alone is not a deployable site.

Source tests also exercise unsupported roles, collisions, unselected dependencies and exact inherited/default behavior. Profiles that retain data, authentication or hardware settings require the existing resources listed on their reference pages. Not every app has a tutorial for a new installation.

## Every profile, including variants

The [complete profile-composition index](../../examples/catalogue/README.md) maps all 21 registered selections to a canonical YAML file and app ID. Those sources are tested through real resolution and packet generation. They show specific dependencies and retained prerequisites; independent selection does not mean dependency-free installation.

## PBS client preparation

[`site.backup.example.yaml`](../../site.backup.example.yaml) is a complete synthetic resolver site selecting the root backup feature. It compiles the client software, recovery inventory, PBS agent step and a fully bound operational schedule without contacting a server. Deployment requires the real protected inputs; compilation does not run a backup. See [the guide](../backup.md).

## Cloudflare ingress

[`cloudflare-ingress.yaml`](../../examples/catalogue/cloudflare-ingress.yaml) is a complete retained example with the framework-owned socket-source gate, protected origin-token reference and explicit backend access. Internal clients remain independently allowlisted. Deploy middleware and internal route restrictions before any later frontend firewall opening; source compilation does not verify Cloudflare, TLS or application acceptance.
