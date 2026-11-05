# Choose images and update safely

[Documentation index](../README.md) · [Software and runtime](../reference/software-and-runtime.md)

Image versions and policies belong to [images.json](../../images.json); package/software/runtime choices belong to [stack.json](../../stack.json). A site selects profiles and supported concrete archive bindings. It does not gain an arbitrary image/command/environment override bag.

## Choose the right profile

| Need | Profile / policy |
| --- | --- |
| Existing custom Home Assistant image/config | homeassistant with its explicit versioned archive binding |
| New standard Home Assistant image/config | homeassistant-public with the declared official digest |
| Existing Node-RED custom nodes/settings/OIDC | node_red with its explicit archive and retained wrappers |
| New standard Node-RED data | node_red-public; no silent retained auth strategy substitution |
| Existing Bitwarden vault | Literal immutable official digest with common missing pull policy |
| Existing Music Assistant | Explicit floating latest policy with its protected data-copy/resolved-image checks |

Public variants are different software choices, not fallbacks. Choosing a public variant does not prove that an existing custom archive, palette, configuration or credential store is compatible.

## Use a versioned custom archive

The HA/Node-RED catalogue entries deliberately require concrete local_id, archive and archive_sha256 supplied through the supported site images binding. Zero-valued public sentinels are unresolved; `--admit` refuses them. Keep the exact archive bytes and private path at the consumer boundary. Do not copy an archive or a real local identity into this public repository.

There is no automatic registry substitution. Conversely, normal immutable Bitwarden uses its official digest literally; there is no local-ID mapper, duplicate instance image checksum or migration startup flag.

## Understand an ordinary update

1. Select exact compatible published framework/library source. Keep each authoritative selector in its existing workflow location.
2. Review the actual profile/software delta. Compare resolved provider identities, NICs, mounts, data owners, accounts, routes, health and app graph with the accepted source.
3. Validate the complete consuming site and regenerate through the selected framework. Run the required tests, per-file coverage, boundaries, source/history scans, signatures and current reviews.
4. Use the consuming site's authorized protected CD. Observe its actual signed source/run/attempt and then verify the selected service/integrations.

Changing an image digest may cause container recreation and interruption. Changing CPU/memory affects infrastructure desired state; the supported native plan determines its effect. Do not promise a universal interruption-free update, rollback, import or replacement.

## Preserve ownership

Stable app/project/service/network identities, NIC slots/MACs, writable storage and credential owners remain bound. A display label does not rename them. The fresh creation policy cannot adopt foreign state and stays unchanged for later owned deployments. Both fresh-policy and retained-policy updates require current ownership, matching backend/source ancestry and protected material continuity. Retained refuses creation.

Ordinary source changes cannot implicitly rotate or remove a sealed credential role, even if a source ID is renamed. Existing managed credentials are create-once and collisions refuse. Active or pending HOLDs are not released by a new commit. Preserve evidence and follow the owning site's reviewed failure procedure rather than issuing a local helper, manual retry or broad chown.

Profile removal is not a generic data-deletion API. Managed DNS may retire only a genuinely previous owned name with its exact address; unrelated aliases remain. Unsupported relocation or cleanup requires its own contract and authority.
