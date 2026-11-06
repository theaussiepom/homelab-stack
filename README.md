# HomeLab Stack

Describe the services you want on Proxmox, choose supported application profiles, and build your own configuration for Debian 13 LXC guests. This library supplies reusable application recipes and guest defaults. You choose the applications, which guests they share, and your host, network and storage allocations.

**New here? [Design your homelab](docs/guides/design-your-homelab.md)** walks from desired services to a complete editable configuration: collect your Proxmox facts, check a fresh recursive resolver, optionally add Home Assistant, and compare separate or shared guests. You finish with inspected compiler output and the exact remaining deployment inputs. The resolver starts on guest loopback; the guide explains the additional prepared-input boundary for LAN filtering DNS.

| Your next decision | Start here |
| --- | --- |
| Create your first personalised configuration | [Design your homelab](docs/guides/design-your-homelab.md) |
| Try the compiler before designing a site | [Compile an offline resolver](docs/guides/first-configuration.md) |
| Choose a profile or variant | [Application catalogue](docs/reference/README.md) |
| Join profiles into a site | [Composition workflow](docs/guides/compose-a-site.md) |
| Prepare or maintain an installation | [Preparation, installation and service verification](docs/guides/installation.md), then [updates](docs/guides/images-and-updates.md) |
| Extend the reusable library | [Contributor workflow](docs/contributing.md) |

The [documentation index](docs/README.md) connects these journeys to the complete reference and examples.

Supporting containers stay with their owning app; choosing one profile does not choose unrelated applications. The supported catalogue has explicit creation, data and integration requirements. Arbitrary VM operating systems and unregistered Compose applications are outside this library's application path.

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
