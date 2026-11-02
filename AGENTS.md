# Working agreement

- Compose `homelab` capabilities into reusable guest profiles, services, images
  and deployment dependencies.
- Put reusable capability fixes in `homelab`; do not duplicate framework code.
- Keep local values, secrets, private repository names and site setup out.
- Use the declared dependency and image policies.
- Preserve the guest dependency graph and selection behavior. Keep one deployment
  job per guest, with the guest name only and short, readable steps.
- Validate composition and generated workflows. Preserve existing test, security
  and review gates; consumers own deployment and service acceptance.
