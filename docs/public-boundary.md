# Public source policy

This public repository contains reusable guest composition and logical network
relationships. Concrete allocations and local policy are required consumer
bindings; reusable profiles provide no site defaults. Separate runnable examples
use benchmark networks (198.18.0.0/15), example.invalid names, synthetic MACs and a
placeholder SSH public key. These examples are rejected by production admission.

Only declarative infrastructure shape, package selections, bounded health checks,
resource limits, reusable app settings and public vendor keys may be ported from
private preparation. Review each field before publishing. Move site addresses, domains, node, storage endpoints and MACs to declared
consumer bindings. Put synthetic values only in the separate examples.
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
