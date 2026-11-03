# Working agreement

- Compose homelab capabilities into reusable guest profiles, services,
  resource requirements, images and deployment dependencies.
- Describe logical network relationships. Obtain concrete addresses, VLANs,
  bridges, VMIDs, MACs, hostnames, domains, storage bindings and local access
  policy from the consuming site.
- Keep site allocations, secrets, private repository names, local setup
  instructions and operating histories out of public source.
- Keep runnable public examples explicitly synthetic and separate from
  reusable definitions. Production admission must reject missing site bindings
  and unresolved example identities.
- Put reusable capability changes in homelab. Do not duplicate framework
  compilation, validation or deployment engines.
- Do not add migration, cutover or one-off site repair executors.
- Keep versions and hashes in their declared authoritative manifests or
  workflow references. Follow declared image policies, including intentional
  floating selections; do not invent a blanket immutable-image requirement.
- Preserve guest dependencies and selection behavior. Keep one deployment
  job per guest, named for that guest, with short, readable steps.
- Validate generated workflows and compile the composition against distinct
  synthetic sites to expose hidden local assumptions.
- Preserve validation, coverage, security and review gates. Consumers own
  deployment authorization and actual service acceptance.
