# Glossary

[Documentation index](README.md)

| Term | Meaning |
| --- | --- |
| Adapter | Framework code that validates one supported app, generates its configuration and handles the supported installation and update operations |
| App instance | A site's named use of a reusable profile, placed on a guest |
| App profile | Reusable requirements and defaults declared in this library's `apps/` directory |
| Binding | A setting that connects an app requirement, such as a network or storage role, to a resource in the site |
| CD | Continuous deployment: the protected workflow that applies a reviewed configuration to its intended hosts |
| Component | A reusable framework type with defined fields, validation rules and behavior |
| Context | The provider, trusted identities, credential references and execution environment selected for a guest |
| Custody / ownership receipt | A private record proving which existing resource HomeLab manages; declaring a flag in source cannot replace this evidence |
| Endpoint | A named address, protocol and port advertised to consumers, or a supported internal application endpoint |
| Exposure | Explicit managed DNS publication or HTTP routing selection |
| Fresh | A policy that allows supported creation when a resource is absent, then updates the same HomeLab-managed resource on later deployments; it cannot adopt existing data |
| Guest | The selected Debian LXC container, including its stable identity and allocated resources |
| Guest loopback | The guest's `127.0.0.1`, distinct from a container's private namespace |
| HOLD | A protected marker recording an unresolved operation and blocking normal continuation; a source update cannot clear it |
| Listener | The address, port and network namespace where a service accepts connections, including any port published on the guest |
| Packet | A generated JSON file containing the configuration and other inputs used to deploy one guest; it can contain private metadata |
| Readiness | An explicit requirement to wait for another app or guest to reach a supported stage; a value reference alone creates no wait |
| Retained | A policy that updates an existing HomeLab-managed resource while preserving data and identity; it cannot create or import a resource |
| Runtime profile | A named set of resource limits, process settings and security requirements selected by a guest or app |
| Source-only | Reads and validates configuration source without contacting or changing a deployment target |
