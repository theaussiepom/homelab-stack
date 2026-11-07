# Choose images and update safely

[Documentation index](../README.md) · [Software and runtime](../reference/software-and-runtime.md)

Image versions and policies belong to [images.json](../../images.json); package, software and runtime choices belong to [stack.json](../../stack.json). A site selects profiles and supported concrete archive bindings. It cannot pass arbitrary image choices, commands or environment overrides.

## Choose the right profile

| Need | Profile / policy |
| --- | --- |
| Existing custom Home Assistant image and configuration | Select homeassistant and explicitly bind its versioned image archive. |
| New standard Home Assistant image and configuration | Select homeassistant-public with the declared official image digest. |
| Existing Node-RED custom nodes, settings and OpenID Connect sign-in | Select node_red with its explicit archive and existing settings and health-check scripts. |
| New standard Node-RED data | Select node_red-public. It does not install the existing profile's OpenID Connect sign-in setup or silently replace that setup. |
| Existing Bitwarden vault | Use the exact official image digest. The `missing` policy pulls it only when it is absent locally. |
| Existing Music Assistant | Use its explicitly floating latest policy. Before an update, HomeLab checks the protected data copy and the exact image resolved from that selection. |

Public variants are different software choices, not fallbacks. Choosing a public variant does not prove that an existing custom archive, palette, configuration or credential store is compatible.

## Use a versioned custom archive

The Home Assistant and Node-RED catalogue entries require the site to supply local_id, archive and archive_sha256 through the supported images binding. The public zero values are placeholders; `--admit` refuses them. Keep the archive’s exact bytes and private path within your protected deployment setup. Do not copy an archive or a real local identity into this public repository.

There is no automatic registry substitution. Conversely, normal immutable Bitwarden uses its official digest literally; there is no local-ID mapper, duplicate instance image checksum or migration startup flag.

## Understand an ordinary update

1. Select exact compatible published framework and library revisions. Keep each authoritative selector in its existing workflow location.
2. Review what changed in the profile and software selections. Compare resolved provider identities, NICs, mounts, data owners, accounts, routes, health and app graph with the accepted source.
3. Validate the complete site configuration and regenerate through the selected framework. Run the required tests, per-file coverage checks, public/private boundary checks, source and history scans, signature checks and reviews of the current source.
4. Use the site's authorized protected CD workflow. Record the signed source revision, workflow run and deployment attempt, then verify the service and selected integrations.

Changing an image digest may cause container recreation and interruption. Changing CPU or memory changes the declared infrastructure settings; the supported native plan determines its effect. Do not promise a universal interruption-free update, rollback, import or replacement.

## Preserve ownership

Keep the same app, project, service and network identities, NIC slots and MAC addresses, writable storage and credential owners. A display label does not rename them. The fresh creation policy cannot adopt foreign state and stays unchanged for later deployments to the same HomeLab-managed instance. Both fresh-policy and retained-policy updates require current ownership, a matching backend and source history and preservation of protected private inputs. Retained refuses creation.

Ordinary source changes cannot implicitly rotate or remove a sealed credential role, even if a source ID is renamed. HomeLab creates managed credentials only once and rejects conflicting existing credentials. Active or pending HOLDs are not released by a new commit. Preserve evidence and follow the owning site's reviewed failure procedure rather than issuing a local helper, manual retry or broad chown.

Profile removal is not a generic data-deletion API. Managed DNS may retire only a genuinely previous owned name with its exact address; unrelated aliases remain. Unsupported relocation or cleanup requires its own contract and authority.
