# Public source policy

This public repository contains an executable, sanitized version of Ben's selected guest composition. Public
source uses benchmark networks (198.18.0.0/15), example.invalid names, synthetic
MACs and a placeholder SSH public key. Central values describe topology once.
These example identities are not approved deployment identities.

Only declarative infrastructure shape, package selections, bounded health checks,
resource limits, reusable app settings and public vendor keys may be ported from
private preparation. Review each field before publishing. Replace site addresses,
domains, PVE node, runner storage endpoints and MACs with central example values.
Do not copy credential values, restore receipts, backup hashes, capture paths,
observations, application data, HA or Node-RED configuration, Zigbee state, radio
backups or exported custom images. A path to an external secret file may be
specified; its content must stay outside Git.

Official image digests are source selections, not credentials. A missing recorded
tag is null, never invented. Custom HA and Node-RED images remain external:
public entries are explicit placeholders; the private overlay must supply their
retained local IDs, archive paths and archive hashes before admission. This work
does not update or convert those images.

The private site supplies actual central values and approved identity overrides.
A public-source merge runs CI only. Live adoption requires a deliberate private
stack selection, prerequisite acceptance, readiness changes and reviewed main merge.
