# HomeLab Stack

Choose reusable application profiles and compose them into Debian LXC guests on Proxmox. Each profile describes the application's interfaces, storage, connections, software and runtime requirements. Your site chooses the instances, placement, allocations and access policy.

Start with one resolver, combine compatible apps on a guest, or place them separately. Supporting containers stay with their owning app; selecting a product does not select unrelated applications.

| Your next decision | Start here |
| --- | --- |
| Understand and try the model | [Learn with an offline resolver](docs/guides/first-configuration.md) |
| Choose a profile or variant | [Application catalogue](docs/reference/README.md) |
| Join profiles into a site | [Composition workflow](docs/guides/compose-a-site.md) |
| Prepare or maintain an installation | [Preparation, installation and service verification](docs/guides/installation.md), then [updates](docs/guides/images-and-updates.md) |
| Extend the reusable library | [Contributor workflow](docs/contributing.md) |

The [documentation index](docs/README.md) connects these journeys to the complete reference and examples.

## Three owners

| Owner | Responsibility |
| --- | --- |
| This library | [Registered profiles](docs/reference/README.md), [guest defaults](docs/reference/templates.md), [shared software/runtime choices](docs/reference/software-and-runtime.md) and complete synthetic compositions |
| [HomeLab framework](https://github.com/theaussiepom/homelab) | Typed grammar, resolution, compilation, infrastructure/configuration engines and supported execution boundaries |
| Your consuming site | Concrete allocations, trust, credentials, data ownership, protected CD and authority to operate |

The [library index](stack.json) and [image catalogue](images.json) remain authoritative. The [phase workflow](.github/workflows/phase.yml) selects the compatible framework; a newer framework checkout is not automatically compatible.

## Know what has been established

The offline examples resolve and lower with the selected real framework. They use synthetic inputs and need no host, Docker daemon or credential values. This establishes source compatibility, not installation or service availability.

Profiles state what first installation needs and what later deployments preserve or refuse. Protected CD and actual endpoint, authentication, persistence and integration checks belong to the consuming site. See the [working agreement](AGENTS.md) for contribution boundaries.
