# Choose images and update safely

[Documentation index](../README.md) · [Software and runtime](../reference/software-and-runtime.md)

Image versions and policies belong to [images.json](../../images.json); package, software and runtime choices belong to [stack.json](../../stack.json). A site selects profiles and supported concrete archive bindings. It cannot pass arbitrary image choices, commands or environment overrides.

## Choose the right profile

| Need | Profile / policy |
| --- | --- |
| Existing custom Home Assistant image and configuration | Select `homeassistant-custom` and explicitly bind its versioned image archive. |
| New standard Home Assistant image and configuration | Select homeassistant with the declared official image digest. |
| Existing Node-RED custom nodes, settings and OpenID Connect sign-in | Select `node_red-custom` with its explicit archive and existing settings and health-check scripts. |
| New standard Node-RED data | Select node_red. It does not install the existing profile's OpenID Connect sign-in setup or silently replace that setup. |
| Existing Bitwarden vault | Use the exact official image digest. The `missing` policy pulls it only when it is absent locally. |
| Existing Music Assistant | Use its explicitly floating latest policy. Before an update, HomeLab checks the protected data copy and the exact image resolved from that selection. |

Standard and custom profiles select different installation contracts. Choosing a standard profile does not prove that an existing custom archive, palette, configuration or credential store is compatible.

## Use a versioned custom archive

Select `homeassistant-custom` or `node_red-custom` explicitly, then bind the existing catalogue ID under root `images`. This fragment uses synthetic archive identities; replace them within the protected consuming site:

```yaml
apps:
  home:
    profile: homeassistant-custom
    # Keep this instance's guest, lifecycle, identity and prepared storage bindings.
images:
  homeassistant:
    local_id: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    archive: /var/lib/homelab-inputs/private-images/homeassistant.tar
    archive_sha256: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
```

This is a selection fragment, not a complete site. The [existing automation example](../../examples/catalogue/existing-automation.yaml) supplies all required bindings. For Node-RED the archive catalogue ID is `node_red`, and its custom profile additionally requires the prepared config/settings/health-check and retained OIDC inputs described in [its reference](../reference/apps/node_red-custom.md). Changing only an image is not a way to remove those requirements.

The `images` map replaces only a declared custom archive record with another `{local_id, archive, archive_sha256}` record. It cannot replace an official registry image or choose a different software bundle. `software` appends to a profile and rejects conflicting image roles; it is not an override. Custom archive placeholders contain zero values and fail deployment admission. Unused site image bindings fail compilation with `component.image-binding-unused`, so leaving an old archive binding behind cannot silently select upstream software.

The standard profiles' directory initializers are separate from image policy and only support new subdirectories on verified owned volumes. Custom profiles require prepared paths and do not gain an initializer from an archive binding. Neither image choice creates an exposure or changes a listener binding. Do not add arbitrary environment, image or command fields to work around these contracts.

There is no automatic registry substitution. Conversely, normal immutable Bitwarden uses its official digest literally; there is no local-ID mapper, duplicate instance image checksum or migration startup flag.

## Migrate an existing consumer

Before selecting this library/framework pair, inventory app profiles, image bindings and exposure source files:

| Previous selection | Preserve the same installation with |
| --- | --- |
| `homeassistant` with a custom archive | `homeassistant-custom`; keep `images.homeassistant` and all prepared storage, runtime, identity and credential inputs |
| `node_red` with custom nodes and OIDC | `node_red-custom`; keep `images.node_red`, config/settings/health-check, authentication and private inputs |
| `homeassistant-public` | `homeassistant`; keep instance/guest identities, lifecycle, storage subpath and initializer ownership unchanged |
| `node_red-public` | `node_red`; keep instance/guest identities, lifecycle, storage subpath and initializer ownership unchanged |
| `homeassistant-bound` or `node_red-bound` | Keep the profile and its custom archive/prepared-input contract; listener isolation is unchanged |
| HTTP or DNS exposure outer `endpoint` | Rename the outer field to `target`; update exported connection names, such as `web_endpoint` and `https_endpoint`, while retaining domains and policy selections |

If a site explicitly appends software registrations, replace `homeassistant-images` / `node_red-images` with `homeassistant-custom-images` / `node_red-custom-images`, and `homeassistant-public-images` / `node_red-public-images` with `homeassistant-upstream-images` / `node_red-upstream-images`. These are still additive selections, not image overrides. Library extensions referring directly to the old official catalogue IDs use `homeassistant_upstream` / `node_red_upstream`; site archive IDs remain `homeassistant` / `node_red`.

The removed `*-public` definitions have no aliases. Existing custom consumers must make an explicit profile migration; the standard names now select official immutable upstream images. Keep custom archive catalogue IDs unchanged. An ordinary update still requires genuine prior receipts, sealed payloads, matching source/backend generations, unchanged persistent ownership and protected private inputs. A new initializer or a different storage shape is an ownership change, not permission to adopt old data. Switching from a custom installation to upstream needs its own compatibility and data plan; this naming migration does not perform it.

Pin the compatible published pair together and inspect changed routes, records and app packets. Unchanged instance names keep their runtime namespace; renaming an app to follow a profile name would change identity. These source changes do not update a consumer's pins or deploy anything.

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

All maintained profiles also distinguish application interface roles, listeners and exported connections by suffix. Follow the [network naming contract](../reference/declaration-records.md#network-names-identify-their-kind) when updating site app role keys and every reference. Guest NIC names, policy-local aliases, runtime service identities, storage and credential names keep their own scope.
