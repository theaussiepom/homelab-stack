# Cloudflare source policy

This is a **policy and app-binding fragment**, not a standalone site. Start with the complete retained [edge-management composition](../../examples/catalogue/edge-management.yaml), which declares Traefik app `edge` and the manager backend. Supply your own `trusted_clients` IP allowlist and an `edge_origin_token` protected secret source. Those values belong to your site; the public library does not allocate internal clients or create a token.

<!-- example: cloudflare-policy -->
```yaml
policies:
  middlewares:
    cloudflare_public:
      type: cloudflare-source
      local_allowlist: trusted_clients
      origin_header: x-origin-key
apps:
  edge:
    secrets:
      cloudflare_origin_token: edge_origin_token
```

Merge these fields into the existing declarations, preserving the provider and DNS credentials. Define an HTTP exposure for the manager endpoint through `edge.https_endpoint`, with `cloudflare_public` first in its middleware list. Bind a site domain, the ACME TLS policy and explicit proxy/backend permissions. The local allowlist must contain at most 256 ranges wholly within RFC1918 space. Bare addresses and host-bit CIDRs normalize before projection. The origin header is lowercase and its retained token is 16–4096 UTF-8 bytes. Normal CD materializes it as a protected read-only secret file; the dynamic middleware configuration contains no token value. This version rejects combining the gate with forward-auth; internal authenticated routes keep their existing separate source restrictions.

[The real composition test](../../tests/test_component_composition.py) reads this exact fragment, supplies clearly test-only private clients and protected file metadata to a copy of the complete base, then checks resolution, runtime leaves and generated scalar-secret forwarding. It does not read credentials or contact targets. Public example sites remain in reserved documentation ranges; the RFC1918 prerequisite exists only in the test fixture and your private site.

For a first installation, provision the existing credential and verify plugin/provider connectivity through the supported protected deployment. For later updates, deploy the middleware and every internal route restriction first while retaining existing firewall limits. Verify actual router coverage, then use a separate deployment for an exact frontend web-port allowance. This fragment adds no firewall allowance and does not establish Cloudflare, TLS, authentication or application acceptance.

[Example index](README.md) · [Traefik profile](../reference/apps/traefik.md)
