# Start here

[Documentation index](README.md)

If your goal is your own Proxmox configuration, start with [Design your homelab](guides/design-your-homelab.md). It helps you choose services, collect the exact host facts, edit a complete source copy and inspect its result. Begin with synthetic facts or your own inventory; you do not need a running target to compile it.

You need basic Git, YAML and networking knowledge, plus Python 3.12 or 3.13 with `venv`/pip. The shorter compiler tutorial needs no Docker daemon, Proxmox host, identity provider or credential values.

## Choose a path

| Goal | Next page |
| --- | --- |
| Produce my own supported configuration | [Design your homelab](guides/design-your-homelab.md) |
| Try the compiler with an unchanged example | [First configuration](guides/first-configuration.md) |
| Choose an application | [Profile catalogue](reference/README.md) |
| Compose existing apps | [Compose a site](guides/compose-a-site.md) |
| Understand a NIC or connection | [Interfaces](guides/multiple-interfaces.md), then [connections](guides/connect-apps.md) |
| Change an installed application | [Images and updates](guides/images-and-updates.md) |
| Add a reusable profile | [Contributing](contributing.md) |

## Select compatible source

Begin in a clean Git checkout of this library at a reviewed, published commit. Use the documentation at that same revision. A consumer records its immutable library selection; this library's [phase workflow](../.github/workflows/phase.yml) contains the sole authoritative framework selection. Do not combine unrelated tips of branches or substitute an unreviewed `main`.

Both tutorials define every shell variable, fetch the selected published framework revision and install its hash-locked dependencies into a new isolated environment. The stated framework revision must match this version's phase workflow; the manifest remains authoritative. Reuse the setup in the same shell when moving between the two tutorials.

Authored site and app-instance files are YAML. The library index remains `stack.json`; generated packets, runtime documents and receipts remain JSON. The safe YAML subset rejects duplicate keys, custom tags, anchors, aliases and merge keys.

## Continue through preparation, installation and verification

The [installation journey](guides/installation.md) gives each stage an observable result and its owning procedure. Return to the selected profile before choosing a creation path.

### Know the boundary before deploying

The first tutorial is source-only. Moving to deployment requires a real consuming site with qualified provider/trust/SSH inputs, infrastructure/state and recovery prerequisites, supported lifecycle/data bindings, a protected runner/workflow, selected secrets and current source review. Those facts cannot be supplied by the synthetic example.

OpenTofu owns infrastructure/state. Ansible owns configuration/services. A successful workflow is followed by actual endpoint, authentication and integration verification. Source publication does not grant target access, a merge, an account privilege, a retry or hold removal.
