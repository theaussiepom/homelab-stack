# Use and extend the library

Start with [Design your homelab](guides/design-your-homelab.md) to turn desired services and Proxmox facts into a complete personalised configuration. The [documentation suite](README.md) connects that journey to component references and advanced operations.

## Use a profile

Choose a supported service in [Design your homelab](guides/design-your-homelab.md#1-start-with-the-services-you-want). When extending an existing source, use [Compose a site](guides/compose-a-site.md) and the [profile catalogue](reference/README.md) for exact required and conditional bindings.

## Bind a connection

[Connect apps](guides/connect-apps.md) explains value references, explicit readiness, accounts, transport and separately selected access policy. [Multiple interfaces](guides/multiple-interfaces.md) explains the NIC/role/listener/endpoint chain.

## Add a reusable profile

[Contributing](contributing.md) covers creating, registering, documenting and testing profiles within repository ownership.

## Generate the selected composition

Follow [Design your homelab](guides/design-your-homelab.md#6-check-the-configuration-and-inspect-its-result) to compile and inspect your edited copy, or [First configuration](guides/first-configuration.md) for the unchanged example. [Testing](testing.md) contains the complete library gates. The consumer generates from its own site; the starter is not an installed graph.
