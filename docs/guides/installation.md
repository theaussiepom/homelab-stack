# Preparation, installation and service verification

[Documentation index](../README.md) · [Offline tutorial](first-configuration.md) · [Profile catalogue](../reference/README.md)

Use this page after an offline source result, or before changing an already owned installation. The result of preparation is a qualified consuming site and an identified supported creation or update path. This library does not supply a universal commissioning command.

## Prepare a consuming site

Start with the exact [profile and variant](../reference/README.md), its **First installation** section and the selected framework's [support boundaries](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md). Determine which configuration, data, accounts and private records already need to exist. A prepared MQTT broker, for example, needs [three bound directories and an existing file probe](../reference/apps/mqtt.md#mqtt-probe); the profile does not generate broker configuration or ACLs.

The consuming site owns provider identity and trust, qualified runner access, protected state/backup storage, credential custody, network policy, package/image availability and the authority to deploy. Its real values replace the tutorial's synthetic inputs. Keep them outside this public repository. Use the framework's [deployment guide](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/operations/deployment.md) for the selected execution interface and [lifecycle contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md) for ownership requirements.

Before execution, resolve the real desired source through its selected framework/library tuple and inspect guest placement, identities, resource budgets, listener scope, generated dependencies and intended changes. An endpoint reference supplies a value; it does not establish [readiness or access](connect-apps.md). A frontend hostname does not prove backend transport or authentication.

## First installation

Select `lifecycle: fresh` only where the guest/app's supported creation path can create an absent owned resource. It remains the policy for ordinary later deployments; do not toggle it after one run. A fresh app on a retained guest still needs free, independent identity/storage and supported capacity. `retained` requires genuine existing HomeLab ownership and refuses creation; it cannot import a foreign installation.

The [public HA/Node-RED variants](../public-images.md), [Unbound](../reference/apps/unbound.md), [native database profiles](../database-tools.md) and other documented creation cases have complete synthetic sources. Passing those sources establishes resolver/lowerer acceptance. It does not prove vendor onboarding, hardware reachability, restored data or an installation in your environment.

Use the consuming site's reviewed protected CD path. OpenTofu owns infrastructure/state; Ansible owns configuration/services. A refused plan, ownership mismatch or HOLD needs its supported diagnosis and separate authority; editing generated files or deleting records is not ordinary installation.

## Verify the intended service

After an authorized deployment, record the actual revisions/environment and inspect each relevant result:

| Result | Evidence to obtain |
| --- | --- |
| Infrastructure and configuration applied | Actual protected job result and owned runtime state |
| Service responds on the intended socket | Protocol check from the intended source network; distinguish router/frontend from backend |
| Authentication and authorization work | Intended accepted principal and relevant refused access, without logging secrets |
| Data and identity are continuous | Expected existing data, account ownership and persistence after the supported operation |
| Selected integration works | Real producer/consumer behavior, not only a generated URL or healthy process |

A library source test cannot obtain this evidence. Unknown hardware, vendor commissioning, replacement, migration or recovery behavior remains unknown until qualified through its actual owner. Use [troubleshooting](../troubleshooting.md) for a refusal and [updates](images-and-updates.md) for later deployments.

## Later deployments

Review changes against each profile's **Later deployments** section and [template inheritance](../reference/templates.md#override-and-change-effects). Changed defaults affect inheriting instances; explicit direct-key overrides remain explicit. Preserve identity, state, data and private-material continuity. A permitted source value is not a promise that the execution policy admits resizing, replacement, relocation or credential rotation.
