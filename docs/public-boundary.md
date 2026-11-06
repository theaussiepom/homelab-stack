# Public source policy

This repository owns reusable app profiles, guest templates, supported defaults
and logical relationships. Sites own concrete allocations, identity, storage,
trust, credentials and access policy. Library definitions contain no implicit
site graph. Separate examples use reserved addresses, synthetic MACs and example
names; source compilation does not admit those values for real deployment.

Only reviewed declarations, public vendor assets and bounded supported component
settings belong here. Do not import private receipts, backup hashes, captures,
observations, application data, configuration secrets, radio state or image
archives. A supported external secret reference belongs to the consuming site;
its value remains outside Git. Public assets retain their exact bytes and hash.

Official image digests are public source selections. Retained archive catalogue
entries keep their explicit policy; a consuming site supplies the exact retained
local ID, archive path and hash. Separately declared public profile variants
select official images for supported fresh paths. There is no silent registry
fallback, policy override or image substitution. See [image options](guides/images-and-updates.md).

The shared selected-framework boundary checker is mandatory. Source publication
and a public-source merge do not authorize native changes. Deployments use the
consuming site's protected CD and its current ownership, trust, state and review
gates; service acceptance is recorded separately.
