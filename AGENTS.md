# Working agreement

- Own reusable app profiles, guest templates and supported defaults. homelab owns contracts, compilation and deployment capabilities.
- Compose existing components; do not duplicate validators or deployment engines.
- Profiles declare interfaces, endpoints, storage, connections and capabilities. Sites supply concrete allocations, credentials and access policy.
- Keep apps independently selectable. Supporting containers belong to their app. Do not impose a fixed guest bundle.
- Add profiles through the library index. Document required bindings, supported placement, first installation and later deployment behavior and explicit dependencies.
- Keep examples synthetic. Test individual definitions and bindings, then use focused real compiler integrations with different layouts and repeated apps.
- Keep versions and image policies in their authoritative manifests.
- Generate one deployment job per guest, named only for that guest, with short application steps.
- Remove obsolete definitions, tests and references after replacement proof. Preserve all existing quality gates.
- Read docs/README.md for guides/reference and docs/testing.md for checks.
- Keep profile docs, maintained examples and tests aligned with public contracts.
- Follow docs/contributing/documentation-standard.md and docs/templates/application-profile.md (or the guest-template template). Write direct explanations for new readers, define necessary terms, and review complete pages for readability as well as technical accuracy.
- Update canonical records, test-local source/document pointers, complete examples and relevant checks with each contract/default change. Keep real configuration/validators authoritative; never mirror defaults in test mappings.
- Validate against the library-selected real framework. Report source, integration, hosted enforcement, deployment and service evidence separately.
