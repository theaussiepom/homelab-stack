# HomeLab Stack documentation

[Project overview](../README.md)

Start with the services you want and turn them into your own Proxmox configuration. The supported base is Debian 13 LXC; each application profile states its creation, data and hardware requirements. You can work offline before completing the host and deployment prerequisites.

## Learn and reach a first service

1. [Design your homelab](guides/design-your-homelab.md) takes you through service choice, guest layout, a Proxmox facts worksheet, a complete source copy, personalisation and compiler-result checks. Add optional Home Assistant and try sharing or separating guests.
2. [Preparation, installation and service verification](guides/installation.md) carries that configuration through the distinct site-owned deployment and acceptance stages.
3. [Images and updates](guides/images-and-updates.md) explains later changes to an already owned installation.

[Start here](start-here.md) helps choose another route. [First configuration](guides/first-configuration.md) is a shorter compiler exercise using the unchanged maintained resolver, useful when you want to inspect the tools first. [Concepts](concepts.md) and the [glossary](glossary.md) explain terms as you need them.

## Choose and look up

- [Application catalogue](reference/README.md): profiles grouped by decision, with variants and their complete examples.
- [Guest templates](reference/templates.md): choose defaults, then inspect exact [Docker](reference/templates/docker.md) or [base](reference/templates/base.md) records.
- [Software and runtime](reference/software-and-runtime.md): packages, images, process security, admission budgets, health, monitoring and reusable policy fragments.
- [Declaration records](reference/declaration-records.md): how the selected values relate to site inputs and compatible framework types.
- [Complete examples](examples/README.md): canonical sources, instance IDs and evidence boundaries.

## Compose and maintain

Once you have a complete starting source, use [Compose a site](guides/compose-a-site.md) as the checklist for adding another application, then the specific relationship you need:

| Decision | Guide |
| --- | --- |
| Share capacity or isolate conflicting sockets | [Shared and separate guests](guides/shared-and-separate-guests.md) |
| Bind an app role to a guest NIC or private scope | [Multiple interfaces](guides/multiple-interfaces.md) |
| Select values, explicit readiness and credentials | [Connect apps](guides/connect-apps.md) |
| Preserve private material and data ownership | [Secrets](secrets.md) |
| Review changed images, defaults or installed inputs | [Images and updates](guides/images-and-updates.md) |
| Understand a source or operation refusal | [Troubleshooting](troubleshooting.md) |

## Extend and review

[Contributing](contributing.md) connects registration, the [documentation standard](contributing/documentation-standard.md), [profile template](templates/application-profile.md), [guest-template template](templates/guest-template.md), [tests and conformance scope](testing.md), and the [public boundary](public-boundary.md). A checked declaration catalogue is not complete procedural-rule coverage or native qualification.

Existing entry routes remain usable: [composition](composition.md), [database tools](database-tools.md), [MQTT Explorer](mqtt-explorer.md), [public images](public-images.md) and [adoption](adoption.md).
