# Complete examples

[Documentation index](../README.md)

These are maintained synthetic source inputs, not installed layouts. Complete examples compile with the selected framework; they do not contain real target acceptance or credential values.

| Scenario | Complete source | What it establishes |
| --- | --- | --- |
| Standalone recursive resolver | [site.example.yaml](../../site.example.yaml), [guest](../../examples/minimal/guests/resolver.yaml), [app](../../examples/minimal/apps/recursive_dns.yaml) | One Unbound without Pi-hole; base defaults; loopback publication; explicit policy |
| Different placement and repeated apps | [site.second.yaml](../../examples/site.second.yaml), [guest/app leaves](../../examples/second/) | Three guests, repeated resolvers with distinct publications, HA without Node-RED or unselected integrations |
| Connect filtering and recursive DNS | [Local DNS worked source](local-dns.md) | Complete synthetic retained composition, named connection/exposure and explicit same-guest readiness; no data adoption/initialization claim |

Run the first two directly using [First configuration](../guides/first-configuration.md). The local DNS page defines its source files and commands. Reference pages use clearly labelled app/property fragments and link these complete examples; a fragment alone is not a deployable site.

Source tests also exercise unsupported roles, collisions, unselected dependencies and exact inherited/default behavior. Profile-specific retained data/auth/hardware paths require their stated consumer facts; this index does not claim every listed app has a fresh commissioning tutorial.
