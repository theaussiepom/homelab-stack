# Application library documentation

Start with a small source-only result, then look up the profile and binding you need. This library supports Debian LXC on Proxmox; runtime and hardware support remains adapter-specific.

## Learn

1. [Start here](start-here.md): prerequisites, version selection and reader paths.
2. [First configuration](guides/first-configuration.md): compile the complete synthetic resolver example without a host.
3. [Concepts](concepts.md): library, site, guest, app and the source-to-service path.
4. [Glossary](glossary.md): short definitions used in the guides.

## Do a task

- [Compose a site](guides/compose-a-site.md)
- [Share or separate guests](guides/shared-and-separate-guests.md)
- [Bind multiple interfaces](guides/multiple-interfaces.md)
- [Connect apps and select readiness](guides/connect-apps.md)
- [Choose images and update safely](guides/images-and-updates.md)
- [Configure PBS backups](backup.md) and review [application recovery coverage](reference/backup-coverage.md)
- [Keep secrets and data owned](secrets.md)

## Look something up

- [Profile catalogue](reference/README.md): every registered ordinary profile and variant.
- [Guest templates](reference/templates.md): exact defaults and partial overrides.
- [Software and runtime](reference/software-and-runtime.md): package/image roles, security, budgets, health, monitoring and optional policy fragments.
- [Complete examples](examples/README.md): maintained source files and what they test.

The [framework configuration guide](https://github.com/theaussiepom/homelab/blob/0094e1c5fc0b8c461e3a7be98de7fb6203a17b45/docs/reference/README.md) owns the language and deployment API. Library pages explain which of those capabilities each profile selects.

## Maintain and contribute

- [Testing](testing.md): fully defined commands and existing gates.
- [Contributing](contributing.md): create/register a profile and keep docs/examples/tests together.
- [Troubleshooting](troubleshooting.md): binding, image, ownership, workflow and service failures.
- [Public source boundary](public-boundary.md): what belongs in this repository.

Older entry pages remain navigation pointers: [composition](composition.md), [database tools](database-tools.md), [MQTT Explorer](mqtt-explorer.md), [public images](public-images.md) and [update checks](adoption.md).
