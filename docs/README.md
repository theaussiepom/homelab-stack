# HomeLab Stack documentation

[Project overview](../README.md)

This suite answers three questions: which reusable profile fits, how its requirements bind to a site, and what evidence is needed before operating it. The supported base is Debian LXC on Proxmox; adapter-specific hardware and lifecycle limits are explicit in each profile.

## Learn and reach a first service

1. [Start here](start-here.md) identifies prerequisites and compatible source.
2. [First configuration](guides/first-configuration.md) resolves a complete offline resolver example.
3. [Concepts](concepts.md) explains how profiles, instances, guests and services relate; the [glossary](glossary.md) supplies short definitions.
4. [Preparation, installation and service verification](guides/installation.md) separates the next three stages and identifies their owning procedures.

## Choose and look up

- [Application catalogue](reference/README.md): profiles grouped by decision, with variants and their complete examples.
- [Guest templates](reference/templates.md): choose defaults, then inspect exact [Docker](reference/templates/docker.md) or [base](reference/templates/base.md) records.
- [Software and runtime](reference/software-and-runtime.md): packages, images, process security, admission budgets, health, monitoring and reusable policy fragments.
- [Declaration records](reference/declaration-records.md): how the selected values relate to site inputs and compatible framework types.
- [Complete examples](examples/README.md): canonical sources, instance IDs and evidence boundaries.

## Compose and maintain

Follow [Compose a site](guides/compose-a-site.md), then the specific relationship you need:

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
