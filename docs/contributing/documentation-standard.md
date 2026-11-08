# HomeLab Stack documentation standard

This standard defines how to design, write and review documentation for the reusable `homelab-stack` application library. Documentation is part of the library’s public contract. Readers must be able to choose an application profile, connect its requirements to site resources through bindings, and understand the resulting behavior and limits. They must also be able to find the exact framework rules without knowing the implementation discussion or another site’s environment.

**MUST** identifies an acceptance requirement. **SHOULD** identifies the normal approach; a documented, reviewed reason may justify another approach. **MAY** identifies an option. These words govern documentation quality; they do not create capabilities in HomeLab. Examples and operational claims MUST follow the accepted implementation at the documented compatible revisions.

This is the canonical documentation policy for this library. The [contributor workflow](../contributing.md) and [application-profile template](../templates/application-profile.md) apply it to changes; [section 11](#11-contributor-and-agent-integration) defines their ownership. Existing source checks have the bounded scope described in [documentation conformance](../testing.md#documentation-conformance); adopting this standard does not verify every behavior described in prose or prove that it works on a running target.

## Contents

- [1. Purpose, audience and ownership](#1-purpose-audience-and-ownership)
- [2. Structure and page types](#2-structure-and-page-types)
- [3. The newcomer and maintenance journeys](#3-the-newcomer-and-maintenance-journeys)
- [4. Profile, template and shared declaration pages](#4-profile-template-and-shared-declaration-pages)
- [5. Property and binding records](#5-property-and-binding-records)
- [6. Contextual links and relationship navigation](#6-contextual-links-and-relationship-navigation)
- [7. Examples, failures and reproducible commands](#7-examples-failures-and-reproducible-commands)
- [8. Installation, updates and operational limits](#8-installation-updates-and-operational-limits)
- [9. Authoring, inventories and generation](#9-authoring-inventories-and-generation)
- [10. Verification and review rubric](#10-verification-and-review-rubric)
- [11. Contributor and agent integration](#11-contributor-and-agent-integration)
- [12. Worked specimen: MQTT profile](#12-worked-specimen-mqtt-profile)
- [13. Worked specimen: Docker guest template](#13-worked-specimen-docker-guest-template)
- [14. Design rationale and source use](#14-design-rationale-and-source-use)

## 1. Purpose, audience and ownership

**S1.1 — Serve decisions at the library boundary.** The suite MUST serve new users choosing an application, site authors composing instances, operators assessing supported changes, and contributors extending reusable definitions. It MUST explain both the reusable definition and how a user's site configuration applies it. A catalogue of product names alone is insufficient.

**S1.2 — Keep the three owners explicit.**

| Owner | Canonical responsibility | Documentation responsibility |
| --- | --- | --- |
| `homelab` | Defines the configuration language, resolves references, validates source, generates deployment packets (files containing deployment inputs) and performs supported deployments. | Defines general rules for fields and types, diagnostics, lifecycle behavior, and the operations that execution supports. |
| `homelab-stack` | Supplies registered app profiles, guest templates, software and image selections, runtime settings, health and monitoring defaults, and reusable policy fragments. | Explains which framework capabilities each profile selects, its effective requirements and defaults, where it can run, its variants and dependencies, and its limits. |
| User’s deployment repository | Supplies actual provider and site allocations, trust inputs, credentials, access policy, authority to operate, and checks of the intended environment. | Documents preparation, installation, service checks and operating procedures for that site. |

Library pages MUST NOT make consumers adopt a fixed environment or publish private repository identities, real allocations, credentials, local operator paths, operational history or recovery artefacts. Standard runtime target paths that are part of a public adapter contract are legitimate reference information; an author's local checkout path is not.

**S1.3 — Compose, do not duplicate authority.** Reuse an existing component and link its owning contract. Do not create another validator in prose, reimplement an execution engine in a guide, or document unrestricted overrides for environment variables, commands, mounts or Compose configuration. A missing typed capability requires a separately scoped contract change before it can appear as supported usage.

**S1.4 — Preserve independence.** A profile MUST state actual companion requirements without imposing unrelated applications. Supporting containers belong to their owning app. A guest template MUST NOT imply an app bundle. A composition can illustrate several apps while explaining which are optional and which relationships make them necessary.

**S1.5 — Keep status and evidence distinct.** Pages MUST distinguish accepted contract facts, behavior established by reading source code, tested effects, behavior verified on a running target and behavior that remains unknown. A proposal MUST be labelled as a proposal and excluded from supported syntax or examples. Documentation MUST follow desired configuration rather than reconstruct an environment's migration or recovery history as an installation prerequisite.

## 2. Structure and page types

**S2.1 — Use a small entry point and linked depth.** The root README SHOULD explain the library, supported platform, owner boundaries and entry routes to learn, select, compose, maintain or contribute. It MUST link a canonical documentation index. It MUST NOT absorb all field reference, installation and troubleshooting material. Plain GitHub-hosted Markdown is a complete delivery format; an HTML platform is not required.

**S2.2 — Give each page one principal job.** Existing useful routes SHOULD be preserved or replaced with pointers during later adoption. The following hierarchy is a responsibility model, not permission to move current files without review.

| Page type | Appropriate reader task | Required shape and limits |
| --- | --- | --- |
| Overview / index | Understand scope or choose a route | State the purpose, supported platform and division of responsibilities. Link readers to their task and make every registered profile and variant discoverable. |
| Concept | Understand a relationship or tradeoff | Explain the library, site, guest and app, including their scope, ownership and effects. Use concrete examples and link the exact reference and task pages. |
| Tutorial | Learn by completing a reproducible result | State the starting environment and observable final result. Supply complete source and ordered steps, include a practical variation, and explain what the result does and does not verify. |
| How-to | Complete one bounded task with known prerequisites | State the outcome, prerequisites, steps, checks and point at which failure stops the procedure. Link concepts rather than reteach the entire model. |
| Component/type reference | Look up framework syntax and behavior | Link the compatible upstream canonical type. Author a local reference only for library-owned declarations; distinguish input from resolved values and generated output. |
| App/profile reference | Choose and configure one registered profile | Use [section 4](#4-profile-template-and-shared-declaration-pages). Include variant choice, binding records, complete usage and precise lifecycle limits. |
| Guest-template reference | Select defaults and override them deliberately | State exact inherited resource, startup and security settings, plus software, runtime and monitoring selections. Explain overrides, limits and effects without supplying site allocations. |
| Composition guide / example | Join independent profiles into a coherent site | Explain each relationship and the component responsible for it, along with placement alternatives. Distinguish values, readiness, access, trust and account effects. Supply complete canonical source and the expected resolved result. |
| Operations guide | Maintain a supported installation managed by HomeLab | Explain prerequisites, required authority, actual continuous deployment (CD) behavior, persistent identities and protected inputs, interruptions, rejected changes and service checks. The site owner remains responsible for its procedure. |
| Troubleshooting / diagnostic reference | Understand and act on a failure | Identify the symptom or exact diagnostic, phase, cause and evidence that distinguishes it from other failures. State the supported correction, its verification, and when to stop or use a separate recovery procedure. |
| Contribution / authoring | Extend or review the library | Explain registration, applicable standards and templates, how to keep source, examples and tests consistent, required evidence and review checks. |

**S2.3 — Avoid competing encyclopedias.** A profile page explains its selected requirements, not every unused framework capability. A composition guide connects canonical definitions rather than repeating their full field tables. A concise glossary can define unfamiliar terms, but MUST link readers onward to behavior and examples.

**S2.4 — Write for someone new to the project.** Narrative MUST name the actor, action and result in ordinary language. Explain necessary technical terms when first used, and put concrete behavior before internal labels. For example, say that HomeLab creates a missing app subdirectory after verifying ownership of its volume. Do not use “create-only initializer on a proved volume” as the explanation. Preserve exact field names, values, constraints, security requirements and evidence limits in reference records and examples. Keep each prose paragraph on one source line.

**S2.5 — Review complete pages for readability.** Read each changed page from start to finish after editing. Check that a newcomer can identify the next action and understand its prerequisites, result and limits without knowing an implementation discussion. Replace dense noun strings, unexplained acronyms and vague phrases with direct sentences. An independent reviewer MUST assess the prose as well as technical accuracy; the author MUST address the findings and reread the complete page before calling it finished.

## 3. The newcomer and maintenance journeys

**S3.1 — Make four distinct stages navigable.** A successful offline tutorial is valuable but does not prove a complete path to a supported installation. The index and tutorial conclusion MUST provide these routes, with availability honestly stated:

| Stage | Observable result | Required explanation |
| --- | --- | --- |
| Offline synthetic tutorial | The compiler resolves source references and generates the selected deployment packet. | Identify compatible source and tools, synthetic values and metadata for private paths. Explain that the reader can inspect output without changing a target. |
| Deployment preparation | The prerequisites for the intended site have been checked. | Explain the supported platform and provider, selected profile capability, trust inputs, ownership of state and backups, credentials, images, packages, existing accounts and data, network access and protected CD. Link the component responsible for each requirement. |
| First installation | HomeLab creates a supported new guest or app. | Explain the actual creation procedure, its exclusions and inputs that must already be prepared. Distinguish what the framework creates from what the operator or vendor must do. |
| Service verification | The intended service and selected integrations work. | Check the actual endpoint, protocol, authentication, persistence and relevant integrations. Record the environment, source revisions and limits of those observations. |

If no public first-install procedure has been verified for the target environment, the page MUST state what is missing and link the supported preparation and operating guidance. It MUST NOT fill the gap with an invented commissioning command, refer vaguely to an unspecified existing site, or describe retained source as an import path.

**S3.2 — Include a later-deployment route.** Explain how the site’s protected continuous-deployment (CD) workflow applies reviewed library and framework changes to an installation that HomeLab already manages. Link profile-specific limits and effective-default changes. A newcomer MUST be able to find this route from the installation section; an existing operator MUST be able to reach it directly from the profile page.

## 4. Profile, template and shared declaration pages

**S4.1 — Use a complete profile page contract.** Every registered profile and public variant MUST have a canonical reference page containing the following information. Headings can group related small records, but the information cannot be replaced with an end-of-page source link.

1. **Purpose and choice:** explain the outcome, selection ID, adapter, supported platform, relevant alternatives and variants, and when to choose each. Name the services, helpers and operating-system units managed by the app and its important external requirements.
2. **Placement and ownership:** explain whether apps can share a guest or need separate guests, and the limits on repeated instances. Identify conflicts involving sockets, operating-system resources, service names, Compose projects, data and credentials. Distinguish checks for conflicting names from tests on a running target.
3. **Syntax:** show the smallest meaningful selection fragment, state its exact placement and shape, and link its complete canonical composition. Include the reusable profile declaration or a precise source link and field navigation.
4. **Bindings and properties:** provide typed [property records](#5-property-and-binding-records) for interface roles, listeners, publications, endpoints, storage, connections, accounts, secrets, authentication, devices, capabilities, app properties, origin, exposures and selected optional features.
5. **Effective defaults and selected policies:** link the selected software, images, runtime settings, health checks, monitoring and resource policies. Explain exactly which values are inherited or overridden, where versions are authoritative, what resource budgets mean and which platform limits apply.
6. **Resolved result:** explain the addresses, ports and identities derived from bindings, generated configuration and runtime files relevant to users, readiness and dependency behavior, and access effects. Generated output is not another authoring API.
7. **Minimal and practical complete usage:** supply canonical source that has passed validation, app and guest IDs, dependency revisions, expected results and evidence. Show a useful nested or conditional feature where supported.
8. **First installation:** explain supported creation behavior and which inputs must be prepared separately. State whether the path performs vendor setup or creates configuration, data and accounts.
9. **Later deployments:** use the exact change classifications from [section 8](#8-installation-updates-and-operational-limits). Explain restrictions on persistent data, protected inputs and identities, and the point where a failure stops work.
10. **Invalid cases and diagnostics:** provide at least two meaningful distinct failures, the actual layer, diagnostic code and path for each, and a supported correction. Link detailed diagnostics and successful examples.
11. **Navigation and provenance:** link the parent catalogue or index, related variants, types, concepts and tasks, complete examples, relevant source and tests, and references for compatibility and changes.

**S4.2 — Apply topics deliberately.** A profile without devices MUST say once that it selects no device role; it does not need a page of serial warnings. An app with no inbound exposure MUST say so without inventing frontend routes. A pure default declaration has no independent service health or installation step: explain its consumer and link that consumer's lifecycle. Required, conditional or security-relevant topics MUST never disappear merely because the current example does not use them.

**S4.3 — Guest-template pages are a different contract.** For each template, document exact complete default blocks and the meaning, bounds and override behavior of every direct field. List references to software, runtime and monitoring definitions and minimum requirements enforced before deployment separately. Explain which site fields remain required and what the template does not allocate. Show an inherited case and a partial override with the resulting effective values. Explain which inheriting guests a template change affects. The [Docker template specimen](#13-worked-specimen-docker-guest-template) demonstrates this page type.

**S4.4 — Shared declarations need their own reference.** Library-owned software roles, runtime profiles, health and monitoring profiles, backup profiles, image policies, assets and reusable policy fragments MUST have canonical definitions. App pages MUST link directly to the selected record. Record the process and security policy, resource-budget units, limits and reservations, probes and timeouts, and named requirements where applicable. Explain which source defines each value and which overrides it accepts. Do not copy volatile package versions or image digests into every app page. A deliberate excerpt MUST be identified as an excerpt and checked against the manifest.

Backup references MUST cover each registered backup profile and every app storage role’s inclusion or exclusion. Explain how bindings supply actual paths, distinguish native full-guest volume protection from selected application recovery, and state the inputs and explicit permissions needed for an operational schedule. Compare declared recovery targets, categories and capture methods with source. Neither client preparation nor successful upload and readback proves that the related application and database can be restored.

**S4.5 — Variants are selectable contracts.** A public-image or database-administration variant MUST state its distinct software, privileges, bindings and lifecycle support. It MAY share unchanged explanation through canonical links, but MUST remain understandable from its own selection page. Documentation for a permissive generic type MUST NOT imply that every adapter or variant accepts it operationally.

## 5. Property and binding records

**S5.1 — Give every accepted path a record and stable destination.** Cover parent objects, nested options, map values, list items, alternatives selected by a type field and fields that are required only under certain conditions. Use a compact index table for scanning, then anchored property records for nontrivial fields. A one-line table is sufficient for a simple scalar only when it contains all applicable information. A long prose paragraph without a discoverable property destination is insufficient.

Use this reusable record form. This is an **authoring form, not YAML syntax or a supported feature**:

| Record item | Required content |
| --- | --- |
| Name and location | Give the exact authored path, the map or list that contains it, and its canonical anchor. Distinguish a reusable declaration from a site binding and a generated result. |
| Purpose and effect | Explain what changes for the user and which resource or operation uses the value. |
| Type and syntax | State whether YAML expects a scalar, sequence or mapping, and give element and key types. Link named nested types and list all accepted alternatives. Quote strings where YAML could change their type. |
| Presence | State whether the value is required, optional or conditional, and give the exact condition. Name the layer that enforces it, including adapter requirements stricter than the profile metadata. |
| Defaults and resolution | Give the literal default or state that none exists. Name the component, profile or resolver that applies it. Explain the order of inheritance, replacement and list appending, and which keys or values each operation affects. |
| Omitted, null and empty | State whether each is accepted and what it does. Distinguish an absent value from an empty mapping, list or string, and from false or zero where meaningful. |
| Value constraints | State units, inclusive bounds, allowed values, case rules, patterns, and path or name formats. Explain whether unknown keys are rejected. Never infer a range from an example alone. |
| Interactions | Explain prerequisites, dependencies, conflicts, related fields required under particular conditions, and supported combinations. Link each relevant rule directly. |
| References and bindings | Name the target type and the namespace or source root used to find it. Explain checks on the target and restrictions on where it may be found. State what happens if it is missing, has the wrong type or creates a cycle, and whether selecting it affects values, order, access, trust or accounts. |
| Outputs | Describe resolved values, generated output or managed files that matter to readers, and say whether each is public or private. Do not present incidental internal structure as stable output. |
| Security and owner | Identify who owns credentials, data and accounts. Distinguish file paths, environment-variable names and other reference metadata from actual protected values. Explain privilege and transport effects, and state permissions only where they are enforced. |
| Lifecycle and limits | Describe effects at first installation and later deployment, including conditions that interrupt, restart, replace or reject work. Identify stable identities and unsupported or unverified operations, and link the lifecycle contract that governs them. |
| Examples and failure | Show a minimal accepted value and, where useful, a combined or conditional case. Give the intended diagnostic for a failure and link its supported correction. |
| Compatibility/provenance | Link the authoritative source at the compatible version and the change that altered behavior. Identify tests and other evidence that establish the specific claim. |

**S5.2 — Avoid meaningless boilerplate.** Every path MUST have type, presence, default or lack of one, and constraints; references MUST have resolution rules. Complex effects MAY be shared at a clearly linked block or type level when they apply uniformly. For a scalar measured in MiB, do not add a meaningless enum field. For a display label, state that it does not rename persistent resources and link identity; do not duplicate the whole deployment procedure. An inapplicable item SHOULD be omitted or explained once for its group. Unknown behavior MUST be recorded as unknown with its affected claim, rather than disguised as “not applicable.”

**S5.3 — Describe actual merging.** Never use “inherits defaults” or “overrides configuration” alone. State which map's direct keys are copied, which instance keys replace them, which lists append, and whether nested values replace or merge. Identify the component that applies each default; a schema annotation is not evidence that a default is inserted. Do not invent a general overlay, patch or recursive merge language.

**S5.4 — Separate acceptance layers.** For each conditional requirement, distinguish type validation, reference and feature checks, the selected adapter’s requirements for generating deployment files, and checks made during deployment. If metadata says optional while the selected adapter requires a binding, state the enforced requirement next to that binding. The [MQTT probe record](#mqtt-probe) is an example. This discrepancy is a documentation and contract-maintenance concern; it is not permission to relax the adapter guard.

**S5.5 — Record outputs separately from inputs.** A generated Compose service, resolved address, workflow dependency or private packet path MUST be marked as output. Explain the source that determines it. Do not suggest editing generated files or treating a runtime receipt as ordinary desired source.

## 6. Contextual links and relationship navigation

**S6.1 — Link where the reader needs the explanation.** A property record MUST link its nested type, important prerequisite, interacting property, complete example and relevant diagnostic at the sentence or table row where the relationship matters. A generic related-links section does not satisfy this rule. Descriptive link text MUST identify the target subject; avoid “here” and unexplained “see docs.”

**S6.2 — Support the whole relationship in both directions.** A profile's interface role should lead to the guest-interface binding contract and a concrete binding example. The binding/concept guide should lead back to representative profiles. A nested type should identify its parent and the declarations that use it. A diagnostic should link to the failing field and valid example; that field should link to its important diagnostic. A complete example should name the profiles and concepts it demonstrates, and those profiles should link to its exact app IDs.

**S6.3 — Explain this relationship chain explicitly.** Library composition guidance MUST cover these distinctions with links at each relevant edge:

| Relationship | What must be explained |
| --- | --- |
| Site network → guest NIC | The site declares the context, CIDR, bridge, VLAN and gateway. The guest selects the slot, MAC, address and control interface. An app reference does not allocate a network interface. |
| Guest NIC → app interface role | A role names an app requirement, and its binding selects a network interface in that app’s guest. A role is not a network ID. Each profile defines whether guest loopback or a private app network is also allowed. |
| Interface role → listener/publication → endpoint | Explain the network namespace, bind address, protocol and port of the actual listener, whether it is published on the host or private, and how the endpoint address is derived. Advertising an endpoint neither isolates the listener nor grants traffic. |
| Consumer connection → producer endpoint/external target | Explain how the typed reference resolves, which source role it uses, and the explicit readiness, hostname, credential or account, and transport choices. Selecting a URL alone supplies none of those other effects. |
| Endpoint → exposure | Distinguish DNS naming from an HTTPS frontend route. Explain ingress, TLS, middleware and authentication choices, ownership and backend transport. An exposure does not retroactively isolate a wildcard listener. |
| Template/profile → instance | Explain exact default and override rules, distinguishing the authoritative reusable selection from the site’s actual identity and allocation. |

**S6.4 — Keep stable destinations.** Use predictable property headings or explicit stable anchors for long dotted paths and ambiguous repeated names. A table containing a field name is not automatically an anchor. Preserve published anchors when moving or refining pages, or add a working compatibility anchor or pointer. Avoid duplicate heading slugs and line-number-only navigation as the primary public API reference. In-page contents SHOULD be present on long pages.

**S6.5 — Keep canonical definitions singular.** Define each shared concept/type once in the documentation maintained by the responsible component. Brief local explanation SHOULD summarize the selected effect and link its source. Do not duplicate field tables across guides. Repeated contextual links are useful across distant sections where readers enter independently; linking the same word repeatedly within one paragraph adds noise. Link important relationships, not every occurrence of an ordinary noun.

**S6.6 — Use compatible public links.** Within a repository, prefer paths that work in the committed tree. Cross-repository behavior and test links MUST identify a compatible published revision or release. Explain how it relates to the authoritative selection; do not create a second pin policy in prose or point at mutable `main` as proof for a pinned consumer. New version and change notes MUST link back to affected profiles/properties and explain inheriting-instance effects. External vendor guidance is supplemental and cannot override HomeLab support.

**S6.7 — Prevent orphans and drift.** Every page MUST be reachable from a canonical index; every registered profile/variant and template MUST be indexed. Review relative links, generated and explicit anchors, public cross-repository targets, moved-page pointers and contextual targets after changes. No broken links or orphan references may remain in the changed surface. Verify external links with bounded checks rather than relying solely on HTTP success: confirm that the target topic, version and anchor still match the claim.

## 7. Examples, failures and reproducible commands

**S7.1 — Label example scope before its fence.** Use one of: complete reusable definition, complete site/composition, typed object/map value, explanatory fragment, non-runnable syntax or deliberately invalid example. A fragment MUST name its placement and link complete surrounding source. Type placeholders belong only in explicitly non-runnable syntax. No unexplained `...`, assumed existing object or unresolved placeholder may appear in a claimed complete executable example.

**S7.2 — Keep complete compositions canonical.** A profile file proves a reusable definition; it does not prove valid usage. Every registered profile and variant MUST map to a complete synthetic composition and an identified instance whose references resolve and whose deployment packets are generated by the real compatible framework. Store example bodies once. Excerpts MUST be extracted or checked against those bodies. One composition MAY cover several profiles, but the catalogue MUST map each selection to its exact app and tested outcome.

**S7.3 — Cover behavior, not only presence.** Each profile MUST have a minimal meaningful selection and a practical case showing a relevant relationship or conditional feature. Across the suite, cover supported shared and separate guest layouts, independently selected apps, repeated profiles, bindings to physical interfaces, guest loopback and private app networks, explicit readiness versus values, exposures, managed versus existing credentials, selected variants and overrides. Do not force irrelevant features into every profile. Cover every nontrivial conditional branch through a suitable direct contract test or focused composition, with explicit traceability.

**S7.4 — Use coherent synthetic values.** Examples MUST use internally consistent names, addresses, subnets, gateways, ports, domains, ownership and source paths that satisfy the owning contract. Use `.invalid` domains and deliberately synthetic endpoints and allocations; explain any contract-required address convention. Secrets MUST be references, synthetic fixtures or clearly non-secret illustrative material. Do not include usable credentials, real site identities or a private history-derived layout. A safe offline example can deliberately refuse real deployment admission; document that boundary.

**S7.5 — Show useful failures.** Include at least two distinct, relevant invalid variations per profile: for example a missing required binding and a conflict involving a condition, path or placement. Keep all unrelated inputs valid so the check reaches the stated boundary. Provide the exact diagnostic code, path and message where stable, the phase that emits it, cause, supported repair and expected recheck result. Never invent a helpful-sounding error. If diagnostic context is broader than the literal source location, state that fact. Reuse existing upstream negative coverage where it proves the claim; do not add redundant tests that only search for prose.

**S7.6 — Make commands reproducible.** Before use, define the checkout and revision, compatible framework selection, working directory, interpreter and dependencies, files, variables and required tools. Commands MUST use actual interfaces. Source-only commands MUST not acquire target authority. Use actual filesystem paths rather than symlinks for disposable source roots where the source reader requires it, use new output directories where overwrite is refused, and keep private and runtime outputs out of source. Link a fully defined setup instead of copying it inconsistently onto every page. State the expected output and result, then explain what to inspect next; an exit code alone is insufficient.

**S7.7 — Bound the proof.** Parsing YAML proves syntax, not references; a real resolver checks source relationships but does not prove that deployment files can be generated; source and deployment-file generation tests do not prove installation on a target. A successful service check does not establish every lifecycle or recovery path. Tests with mocks MUST name the boundary replaced. Do not describe source composition tests as end-to-end service verification.

## 8. Installation, updates and operational limits

**S8.1 — Use plain lifecycle headings.** App pages MUST contain **First installation** and **Later deployments**. “Fresh/update supported” or “guarded plan” alone is insufficient. `lifecycle: fresh` permits supported creation when the backend and prior ownership records are absent and continues through updates to the same HomeLab-managed instance. Readers MUST NOT be told to toggle it after installation. `retained` requires a genuinely existing HomeLab-managed instance, refuses creation and does not authorize importing or adopting another installation. Guest and app lifecycle policies are separate; explain a supported new app on an existing HomeLab-managed guest when relevant.

**S8.2 — Specify first-install prerequisites and ownership.** List the required guests, data, configuration, accounts, trust inputs, images, packages and protected files. Explain which the selected path creates, which the site operator must prepare, and which are unsupported or have not been verified. A ready vendor image, profile listing or compiled packet does not establish successful initial setup. Do not imply that a role binding can generate arbitrary accounts, configuration or access-control rules. Standard source describes desired state; environmental preparation or recovery uses its separately reviewed procedure.

**S8.3 — Classify changes concretely.** For each meaningful change to a profile or template, state the input condition, the component that applies or rejects it, the managed resources affected, the expected effect, possible interruption, and the evidence or verification still needed. Use the following categories only when evidence supports them:

| Classification | Required statement |
| --- | --- |
| Supported ordinary update | Name the exact fields and the ownership records that must stay consistent. Describe the resulting changes to configuration, services and infrastructure. |
| Potentially disruptive | State what may stop, restart, reload or become unreachable, when and why it happens, and whether the effect was observed or inferred. |
| Replacement-triggering | State what triggers replacement and how it affects data and identity. Distinguish a provider-proposed replacement from a HomeLab-supported operation; if HomeLab refuses the proposed replacement, document that trigger and refusal rather than implying it will execute |
| Refused | State the exact prohibited change or condition, diagnostic and phase where known, evidence that remains, and the supported next step. |
| Separately prepared/reviewed | Describe the external work and who performs it. Link an existing procedure if one is supported; do not invent a configuration switch. |
| Not yet qualified / unknown | Identify the behavior or environment that lacks evidence. State what existing source tests establish and what further verification would answer the remaining question. |

A blanket “updates are safe” is prohibited. A blanket “everything replaces” is equally misleading. Distinguish a container reload, owned-service restart, peer restart, guest reboot, resource recreation and data migration. Do not promise zero interruption without target evidence.

**S8.4 — Describe default/software adoption.** Changes to profiles, templates, software, runtime settings or images can affect every instance that inherits them. Identify the authoritative manifest and compare effective output, dependencies and resource budgets before adoption. State whether the image uses a pinned digest or an allowed update policy. Do not promise automatic upgrades, rollback or data migration merely because image selection validates. Do not duplicate volatile versions across pages.

**S8.5 — Preserve operational boundaries.** Explain the stable identities of guests, apps, projects, services, networks, data and credentials and the current records proving HomeLab ownership wherever these constrain changes. Ordinary updates do not implicitly relocate data, rotate credentials, replace or remove other protected inputs, import foreign resources, delete abandoned services, bypass locks or release a HOLD. Deletion, rollback, restore, retry and replacement MUST be described only through existing supported contracts. Where failure can occur after infrastructure or preparation has changed the target, do not claim an atomic no-change refusal. Diagnostics must direct operators to preserve current evidence and use the existing recovery procedure verified for the target environment.

**S8.6 — Explain the CD maintenance flow without site secrets.** Explain the sequence: review desired source and published compatible dependencies, run offline checks and compare the effective plan, pass the site’s protected deployment checks, run infrastructure and configuration phases, then check profile health and actual service behavior. Name the responsible tools: OpenTofu manages infrastructure and state; Ansible manages configuration and services. The library provides reusable definitions and workflows; it does not give the reader another site's operating permission. Site-specific settings, secrets, approval procedure and service observations remain with that site.

## 9. Authoring, inventories and generation

**S9.1 — Build a structural and semantic inventory before claiming completeness.** Read the actual library index, referenced complete declarations and the compatible framework’s types, including their rejection of unknown fields. Inspect the checks in reference resolution, property validation, adapters, deployment-file generation and runtime helpers, along with diagnostics and maintained examples. Schema enumeration alone cannot find every conditional or adapter-specific requirement. Inspect accepted extensions and variants as well as common defaults.

The inventory MUST distinguish at least these entities:

| Entity | Inventory key and required evidence |
| --- | --- |
| Profile / variant / template | Record the registered ID, source, adapter, canonical page, catalogue link and compatible revision. |
| Property / nested type / binding role | Record the full path, variant and any field that selects the variant. State the actual type, presence requirement and default, the layer that merges it, and the page anchor. |
| Semantic rule | Record a stable review identifier, condition, affected paths, source code and phase that enforce it, explanation anchor and relevant validation evidence. |
| Reference edge | Record the source and target types and their scope. Explain lookup and path restrictions, dependency and access effects, navigation in both directions, and an example. |
| Diagnostic | Record the actual code, message, context and emitting phase. Link its rule or field, explain the correction, and include a useful invalid case. |
| Example / scenario | Record canonical source, profile and app IDs, the required dependency revisions, the expected resolution, generated output or rejection, and the evidence level. |
| Lifecycle claim | Record the change condition and whether it is supported, rejected, disruptive or unknown. Name the component responsible, the effect, and evidence from source, tests or a target. |

**S9.2 — Maintain an auditable traceability record.** A contributor or reviewer MUST be able to follow `inventory item → canonical page#anchor → explanation → example or justified non-example → relevant test/evidence`. Record source revision and applicability. Include reverse checks for pages documenting removed or unaccepted fields, stale defaults, obsolete variants and unsupported lifecycle guarantees. A list of all profile names passing compilation is useful but does not establish that all fields, rules and diagnostics are documented.

Example inventory row form, **not a new configuration schema**:

| ID | Owner/source | Page#anchor | Rule/default/condition | Example | Evidence and status |
| --- | --- | --- | --- | --- | --- |
| `mqtt.secret.probe.file` | Selected MQTT adapter requirement | MQTT#probe | A file source is required despite optional profile metadata. | Messaging composition / broker | Accepted and rejected cases use the real resolver and deployment-file generator. Actual secret values on a target were not tested. |

**S9.3 — Generate structure where reliable; author explanation.** A later documentation tool MAY extract IDs, field paths and types, allowed values and numeric bounds, declared defaults, catalogue links and example coverage. The generator MUST use the accepted source and preserve stable destinations. It MUST NOT infer lifecycle guarantees, operational effects, intent, prerequisites or conditional semantics from names. Human and agent authors remain responsible for readable explanations, choices, relationships, useful failures and qualification limits.

Do not duplicate a schema into a manually maintained second authority. A generated table is appropriate only when accurate, concise and linked to authored context; internal implementation fields, repeated empty attributes and unexpanded schema noise SHOULD be excluded from the reader page. The documentation MUST identify the inputs, the component responsible for generated output, and how to reproduce it. This standard does not require or authorize implementing a generator.

**S9.4 — Synchronize the change unit.** A change to a profile, contract or default MUST update its documentation, examples, links between inventory rules and evidence, diagnostics where affected and meaningful existing tests in the same reviewable change. A framework change may require coordinated library documentation, but source compatibility and pin adoption remain separate reviewed decisions. Never refresh frozen expected outputs or hashes merely to hide unexplained drift.

## 10. Verification and review rubric

**S10.1 — Require measurable completion.** For the changed scope, acceptance requires:

- 100% of registered profiles, variants and templates mapped to canonical discoverable pages and complete applicable usage examples.
- 100% of inventoried accepted property paths, nested alternatives and binding roles mapped to accurate records; no unexplained entries or documented phantom fields.
- 100% of inventoried semantic, conditional, reference and lifecycle rules and relevant diagnostics mapped to explanation and suitable evidence, or an explicitly reviewed qualification limit.
- All claimed complete examples pass their owning structural validator; the real compatible library and framework resolve selected complete sites and generate their deployment packets.
- Negative examples reach their documented refusal; examples of defaults, constraints and overrides match actual effective output.
- No broken local links or anchors, unresolved placeholders or orphan pages in the changed surface; compatible external public targets checked for meaning as well as reachability.
- All factual behavior claims cite or trace to source or evidence; actual deployment and service verification is claimed only when performed for that outcome.

The review MUST state the total number of items being checked, drawn from an inspected inventory. A bare “100% covered” or code coverage percentage is insufficient. Until the full inventory exists, report sampled coverage and unknown completeness, not a count of missing fields invented from sampling.

**S10.2 — Choose evidence by boundary.**

| Evidence | What it can establish | What it cannot establish alone |
| --- | --- | --- |
| Source inspection / structural inventory | Establishes the declared structure, conditions and implementation behavior under review. | Does not establish successful execution or support on a target. |
| Direct real component tests | Establish type and range checks, handling of omitted, null and empty values, rejection of unexpected fields, and conditional failures in that contract. | Do not establish whole-site references, app placement or deployment. |
| App/guest units with mocked component contracts | Establish how the library selects definitions and applies defaults, and how an app or guest behaves in isolation. | Do not establish the validation behavior of components replaced by mocks. |
| Real resolver + lowerer integration | Establish compatible profile bindings, checks of dependencies, traffic, identities and resources, and the generated deployment packets. | Does not establish installation on a target or service availability. |
| Controller/helper or isolated protocol tests | Establish specific guarded transitions and checks of protected inputs, ownership and protocols in the named test environment. | Do not establish protected CD or behavior on every target platform. |
| Authorized deployment evidence | Establishes that the selected source and workflow were applied to the recorded environment. | Does not establish every service integration, rollback or recovery path. |
| Actual service acceptance | Establishes the endpoint, authentication, persistence and integration behavior actually checked. | Does not establish unchecked lifecycle changes or universal support. |

Run existing relevant example, contract and navigation checks and repository-required checks. Add evidence only where an unproved claim or changed behavior needs it. Do not create tests that merely restate implementation or demand a new deployment for a prose-only clarification. Reuse valid evidence with its exact scope and revision; re-run when changed inputs invalidate it.

**S10.3 — Apply a severity rubric.**

| Severity | Examples | Review disposition |
| --- | --- | --- |
| Blocker | Disclosure of private data or secrets; an invented supported API; destructive or recovery instructions outside a real contract; a false claim of installation or service verification; or an example directing unsupported adoption of identities or data | Must fix before acceptance |
| Major | A missing accepted path or conditional rule; a wrong default, binding or precedence rule; a claimed complete example that fails or is only a fragment; a misleading lifecycle, restart or replacement claim; a missing critical contextual link; or an untraceable coverage claim | Must fix before the affected page/change is complete |
| Moderate | Discoverability gap, unclear variant choice, insufficient useful failure guidance, stale noncritical target or repeated competing explanation | Fix in the change unless explicitly deferred with a named owner and scope, without falsely claiming completeness |
| Minor | Wording, formatting or a noisy repeated link without behavioral ambiguity | Correct when practical; does not excuse larger defects |

**S10.4 — Critique as a reader and as a contract reviewer.** Starting from the README, attempt to choose one profile and follow its field → type → prerequisite → complete example → diagnostic → later-update path. Inspect Markdown rendering, heading hierarchy, table width and code fences. Then compare every changed property, rule and default to its source and effective result. A peer review is independent only when another reviewer actually performed it; an author's self-review MUST be labelled self-review.

**S10.5 — Definition of done.** The changed inventory agrees with source. Meaningful examples and invalid cases pass their checks at the stated layer, and links and navigation render and resolve. All blocker and major findings are corrected, moderate deferrals are explicit, and source, examples and documentation agree. Existing quality, security and review checks remain intact, and remaining operational unknowns are specific. When first adopting the standard, reviewers must also agree where the canonical policy and templates live; it does not imply the existing suite has already been redesigned to comply.

## 11. Contributor and agent integration

**S11.1 — Use one local policy.** This file governs library profiles, templates, defaults and composition guidance. The [contributor workflow](../contributing.md), [application-profile template](../templates/application-profile.md) and [guest-template template](../templates/guest-template.md) implement it. The selected framework owns grammar and deployment behavior; its compatible documentation remains authoritative for those contracts.

**S11.2 — Synchronize source, examples and records.** The working agreement requires canonical documentation, test-local pointers between source and documentation, complete synthetic examples and relevant checks to change together. Follow [documentation conformance](../testing.md#documentation-conformance). The standard's worked specimens below retain the historical source revisions used for those checks; current reference pages are the consumer-facing records. An inventory of supplied declarations does not establish coverage of all optional framework syntax or procedural lifecycle rules.

**S11.3 — Review outcomes.** Reviewers apply [section 10](#10-verification-and-review-rubric), including meaningful contextual links and unsupported-operation boundaries. Report inspected source, tested integrations, hosted checks and actual service verification separately. Do not relax existing coverage, security, signing or review gates.

## 12. Worked specimen: MQTT profile

This specimen demonstrates a finished profile reference at a checked public snapshot. It is not a new feature or a request to change the library. Its source basis is [`homelab-stack` at `a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d`](https://github.com/theaussiepom/homelab-stack/tree/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d) with its [selected framework `52913d4ba03f85e7d734a85b08c93e73f320455d`](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/.github/workflows/phase.yml). These are the source revisions used for these checks, not a second dependency policy. Recheck facts against the selected combination of revisions when adopting changed source.

[Choice and syntax](#mqtt-choice) · [Binding records](#mqtt-bindings) · [Probe](#mqtt-probe) · [Password file](#mqtt-password-file) · [Examples](#mqtt-example) · [Lifecycle](#mqtt-lifecycle) · [Diagnostics](#mqtt-diagnostics)

<a id="mqtt-choice"></a>
### 12.1 Purpose, choice and reusable syntax

Select `mqtt` to run one Mosquitto broker container with explicitly prepared broker configuration, data and log directories. It owns service role `mqtt` and uses the `mqtt` adapter. MQTT Explorer is a separate optional consumer; selecting this broker does not select Explorer, an identity service or another home-automation app. The supported platform is Debian 13 LXC on Proxmox. Source compilation is separate from service acceptance.

The following is the **complete reusable app-profile definition** from [apps/mqtt.yaml](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/apps/mqtt.yaml). It is a library definition, not a complete site configuration:

```yaml
schema: homelab-components-v1
kind: app-profile
adapter: mqtt
display_name: MQTT
interfaces:
  backend:
    required: true
    accepts: [guest-interface]
  frontend:
    required: true
    accepts: [guest-interface]
listeners:
  mqtt:
    service: mqtt
    namespace: host
    interface: backend
    bind: wildcard
    protocol: tcp
    port: 1883
endpoints:
  backend: {listener: mqtt, protocol: tcp, via: backend}
  frontend: {listener: mqtt, protocol: tcp, via: frontend}
storage:
  config: {target: /mosquitto/config, read_only: false, required: true, kind: directory}
  data: {target: /mosquitto/data, read_only: false, required: true, kind: directory}
  log: {target: /mosquitto/log, read_only: false, required: true, kind: directory}
connections: {}
software: [docker, curl, mqtt-images]
runtime: [container-host, mqtt]
health:
  ready: {profile: adapter-ready}
monitoring: {profile: docker-agent}
secrets:
  probe: {required: false}
```

Direct field destinations include [interface requirements](#field-mqtt-interfaces-backend-required), [listener port](#field-mqtt-listeners-mqtt-port), [frontend endpoint](#field-mqtt-endpoints-frontend), [config mount](#field-mqtt-storage-config-target) and [probe metadata](#field-mqtt-secrets-probe-required). Equivalent-role records share one row while retaining separate field anchors.

The complete declaration is registered as `mqtt` through [stack.json](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/stack.json). The current adapter enforces the [file probe requirement](#mqtt-probe) even though the metadata above marks it optional.

<a id="mqtt-bindings"></a>
### 12.2 Declaration and site binding records

Jump to [interface roles](#field-mqtt-interfaces), [listener](#field-mqtt-listeners-mqtt), [endpoints](#field-mqtt-endpoints), [storage roles](#field-mqtt-storage), [software](#field-mqtt-software), [runtime](#field-mqtt-runtime) or [private role metadata](#field-mqtt-secrets-probe).

The following records describe this selected profile. General syntax is defined by the compatible [framework app contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [library contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/library.md). The complete [broker instance](#mqtt-example) supplies all surrounding site identity and resources.

| Declaration path | Exact selected value/type | Effective meaning and corresponding site input |
| --- | --- | --- |
| <a id="field-mqtt-schema"></a><a id="field-mqtt-kind"></a>`schema`, `kind` | Strings `homelab-components-v1`, `app-profile` | These markers identify a complete reusable definition, not the root type of a site. Neither null nor an empty value is accepted. |
| <a id="field-mqtt-adapter"></a>`adapter` | String `mqtt` | Selects the existing typed MQTT adapter and the service role it manages. It does not allow an arbitrary adapter or Compose override. |
| <a id="field-mqtt-display-name"></a>`display_name` | String `MQTT` | Supplies the default descriptive label. An explicit site `display_name` replaces it without renaming the persistent identity. |
| <a id="field-mqtt-interfaces"></a><a id="field-mqtt-interfaces-backend"></a><a id="field-mqtt-interfaces-backend-required"></a><a id="field-mqtt-interfaces-backend-accepts"></a><a id="field-mqtt-interfaces-frontend"></a><a id="field-mqtt-interfaces-frontend-required"></a><a id="field-mqtt-interfaces-frontend-accepts"></a>`interfaces.backend`, `.frontend` | [Named role mappings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types) | Both roles are required: each `.required` is boolean `true` and `.accepts` is the sequence `[guest-interface]`. Each site role [binds a guest NIC](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md#interface-roles) with `{interface: NIC_ID}` in the selected guest. |
| <a id="field-mqtt-listeners"></a><a id="field-mqtt-listeners-mqtt"></a><a id="field-mqtt-listeners-mqtt-service"></a><a id="field-mqtt-listeners-mqtt-namespace"></a><a id="field-mqtt-listeners-mqtt-interface"></a><a id="field-mqtt-listeners-mqtt-bind"></a><a id="field-mqtt-listeners-mqtt-protocol"></a><a id="field-mqtt-listeners-mqtt-port"></a>`listeners.mqtt` | [Named listener mapping](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types) | The listener declares `.service: mqtt`, `.namespace: host`, `.interface: backend`, `.bind: wildcard`, `.protocol: tcp`, `.port: 1883`. The generated container uses host networking, and its actual socket is host TCP 1883. |
| <a id="field-mqtt-endpoints"></a><a id="field-mqtt-endpoints-backend"></a><a id="field-mqtt-endpoints-backend-listener"></a><a id="field-mqtt-endpoints-backend-protocol"></a><a id="field-mqtt-endpoints-backend-via"></a><a id="field-mqtt-endpoints-frontend"></a><a id="field-mqtt-endpoints-frontend-listener"></a><a id="field-mqtt-endpoints-frontend-protocol"></a><a id="field-mqtt-endpoints-frontend-via"></a>`endpoints.backend`, `.frontend` | [Named endpoint mappings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types) | Each endpoint declares `.listener: mqtt`, `.protocol: tcp`; `.via` is the matching role name. The endpoint address comes from that role’s bound NIC, and the port comes from the shared listener. These are two advertised endpoints for one listener. |
| <a id="field-mqtt-storage"></a><a id="field-mqtt-storage-config"></a><a id="field-mqtt-storage-config-target"></a><a id="field-mqtt-storage-config-required"></a><a id="field-mqtt-storage-config-kind"></a><a id="field-mqtt-storage-config-read-only"></a><a id="field-mqtt-storage-data"></a><a id="field-mqtt-storage-data-target"></a><a id="field-mqtt-storage-data-required"></a><a id="field-mqtt-storage-data-kind"></a><a id="field-mqtt-storage-data-read-only"></a><a id="field-mqtt-storage-log"></a><a id="field-mqtt-storage-log-target"></a><a id="field-mqtt-storage-log-required"></a><a id="field-mqtt-storage-log-kind"></a><a id="field-mqtt-storage-log-read-only"></a>`storage.config`, `.data`, `.log` | [Named storage requirement mappings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#profile-storage-roles) | Each role declares `.required: true`, `.kind: directory`, `.read_only: false`. The `.target` values are `/mosquitto/config`, `/mosquitto/data`, `/mosquitto/log` respectively. The site must [bind all three](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings). The profile declares neither a default source path nor an initializer for a new directory. |
| <a id="field-mqtt-connections"></a>`connections` | Empty mapping `{}` | The broker has no role for connecting to an upstream service. Other apps can target its endpoints through their own supported connection roles; this does not implicitly give the broker an upstream. |
| <a id="field-mqtt-software"></a>`software` | [Software IDs](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#software): `docker`, `curl`, `mqtt-images` | Selects named library definitions. `mqtt-images` maps image role `mqtt` to authoritative catalogue ID `mqtt`. |
| <a id="field-mqtt-runtime"></a>`runtime` | [Runtime-profile IDs](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#runtime-and-allocations): `container-host`, `mqtt` | Selects named runtime requirements. In this snapshot, the MQTT service has a memory reservation and limit of 256 MiB, a CPU limit of 1 and a PID limit of 128. |
| <a id="field-mqtt-health"></a><a id="field-mqtt-health-ready"></a><a id="field-mqtt-health-ready-profile"></a>`health.ready.profile` | [Health-profile reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#health-and-monitoring) `adapter-ready` | Selects the adapter’s health checks, which require the existing probe credentials to succeed and anonymous access to fail. Defining a check does not establish that it ran on a target. |
| <a id="field-mqtt-monitoring"></a><a id="field-mqtt-monitoring-profile"></a>`monitoring.profile` | [Monitoring-profile reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#health-and-monitoring) `docker-agent` | Selects the library’s monitoring policy without allocating a private monitoring server. |
| <a id="field-mqtt-secrets"></a><a id="field-mqtt-secrets-probe"></a><a id="field-mqtt-secrets-probe-required"></a>`secrets.probe.required` | Boolean `false` metadata | The current adapter still requires a file binding. See [probe details](#mqtt-probe) and the [missing-probe diagnostic](#mqtt-diagnostics). |

Both roles can bind the same guest NIC, as in the example. Neither role creates a NIC, and neither endpoint grants traffic or adds a readiness wait. A wildcard host listener may listen beyond the advertised NICs. Binding `backend` and `frontend` to different NICs does not create separate isolated sockets. A second overlapping host TCP 1883 broker on the same guest conflicts; distinct guest placement avoids that specific socket collision but still requires independently owned data, identities and credentials. See [interface composition](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/multiple-interfaces.md) and [placement limits](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/shared-and-separate-guests.md).

Storage bindings select an explicit supported guest volume or root path with a required `subpath` field. Use `subpath: ""` to select the entire bound root; a nonempty subpath must remain confined below it. They resolve under the selected guest, not an arbitrary controller path. The framework verifies existing data; it does not silently change its Unix owner or move it. The adapter mounts these sources at the three declared container targets. This profile does not declare a directory initializer, a generator for broker configuration or access-control lists (ACLs), or a general procedure for creating credentials. Use the compatible [storage reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md) for binding alternatives and path constraints, and [installation limits](#mqtt-lifecycle) before operating.

References to software, runtime settings and health checks resolve to named definitions in the library index. The selected image uses an immutable registry digest in [images.json](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/images.json). Exact package versions and shared security and process defaults belong to [software/runtime declarations](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/reference/software-and-runtime.md). The framework checks resource budgets before deployment; they are not measurements of service capacity. The effective guest reserve and all app requirements must fit within the allocation.

No device role, inbound HTTP route, OAuth client or broker consumer-connection role is declared. These topics are inapplicable to this profile's selected definition; the [Explorer page](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/reference/apps/mqtt_explorer.md) explains its gateway, outpost and workspace requirements.

<a id="mqtt-probe"></a>
### 12.3 `apps.<id>.secrets.probe`

**Type and reference:** a site identifier string selecting `secret_sources.<name>` in the same complete site. For this adapter the selected source MUST be `{type: file, path: ABSOLUTE_PATH}`; file path syntax is defined by the compatible [secret-source contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/identity-and-secrets.md). The source is controller metadata. Resolving it does not read its file or create an account.

**Presence/default:** required by the selected MQTT adapter even though profile metadata marks the role optional. The framework inserts neither a default source nor default credentials. Omission reaches `component.secret-required`; a valid environment source also fails this requirement for a file source. A null or empty identifier does not count as omission and fails the reference and type rules. The [diagnostic example](#mqtt-diagnostics) demonstrates omission from an otherwise valid source.

**Material and output:** the runtime parser accepts one existing JSON probe record with exactly `username` and `password`, both nonempty strings of at most 65,535 UTF-8 bytes without carriage returns (CR), line feeds (LF) or NUL characters. It prepares private `mqtt-probe.json` owned by UID 0 and GID 0 with mode 0600 under the app's selected runtime directory. No actual values belong in public documentation or source. See [probe parser](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/mqtt_runtime.py) and [required probe binding](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_foundations.py).

**Lifecycle:** supply a genuinely existing probe account and prepared broker that accepts it. This record is separate from application credentials, GUI credentials and credentials for an identity service. Ordinary updates must preserve the existing private inputs. Changing a source name or path does not authorize credential rotation. Source compilation neither checks credential contents nor proves broker acceptance. The adapter's health definition checks authenticated acceptance and anonymous refusal after actual deployment; this specimen has not performed that target check.

<a id="mqtt-password-file"></a>
### 12.4 `apps.<id>.properties.password_file`

**Purpose:** names the existing Mosquitto password file for the separately selected managed MQTT-account capability. It does not create `mosquitto.conf`, an ACL or arbitrary broker accounts. A plain broker with an existing explicit credential consumer can omit it, as in the [canonical composition](#mqtt-example).

**Type and constraint:** optional string matching `/mosquitto/config/[A-Za-z0-9_.-]{1,100}`; the basename cannot be `.` or `..`. This is a path inside the declared config mount, not a secret-source ID or controller path. Absolute paths elsewhere, nested subdirectories, null and the empty string fail `component.property`. No units, enum or nested object apply.

**Conditional requirement:** when a supported MQTT Explorer connection selects a managed account on this broker, the resolver requires this property and supplies it to the procedure that creates the account; absence then fails `component.broker-binding`. An Explorer connection using an explicit existing credential is a different mode and does not create that managed account. See the compatible [connection/account rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_foundations.py) and [Explorer's choice](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/reference/apps/mqtt_explorer.md).

**Default/resolution:** no default is declared in this profile; omission leaves it absent. The resolver copies direct profile property keys then replaces them with explicit site property keys. This field is scalar, so no recursive merge applies. The MQTT property object rejects unknown fields: `password_file` is its only accepted key at this snapshot. `port: 1884` is not an available override and fails `component.fields`.

**Conditional syntax fragment**, to be placed in an otherwise valid broker instance whose separately declared managed-account composition requires it:

```yaml
properties:
  password_file: /mosquitto/config/passwords
```

This fragment passes the property's value rule; it does not by itself select or prove the account operation. That operation uses the supported procedure that mounts the password file’s parent directory, updates the file and reloads the broker with HUP, while checking that existing ownership and private inputs remain unchanged. The HUP signal asks the broker to reload its configuration; it is not a promise that every broker update avoids a restart. See [lifecycle](#mqtt-lifecycle) and [invalid property diagnostics](#mqtt-diagnostics).

<a id="mqtt-example"></a>
### 12.5 Minimal usage and complete composition

This is a **complete `apps.broker` map entry**, excerpted from app `broker` in the [complete synthetic messaging composition](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/examples/catalogue/messaging-radio.yaml). Place the shown `broker` entry under the site's `apps` mapping. It is not a complete site and requires that file's guest, network, root path, project, identity and file-source declarations:

```yaml
broker:
  profile: mqtt
  guest: broker
  lifecycle: retained
  interfaces:
    backend: {interface: primary}
    frontend: {interface: primary}
  storage:
    config: {root_path: data, subpath: broker/config}
    data: {root_path: data, subpath: broker/data}
    log: {root_path: data, subpath: broker/log}
  identity:
    phase: broker
    runtime_id: example-broker
    services: {mqtt: broker_mqtt}
    networks: {}
    runtime_directory: /opt/homelab-app/runtime/broker
    project: broker
  secrets:
    probe: broker_probe
```

`primary` resolves to guest `broker`'s NIC at synthetic `198.18.20.90`. Both advertised broker endpoints therefore resolve to that address on TCP 1883; the actual listener remains wildcard in the host namespace. Guest root path `data` is `/srv/example/broker`, so the three subpaths resolve below that base. `project: broker` selects the guest's declared Compose project, rather than inventing a new project during a retained update. At deployment, the explicit identities of retained resources must match the actual HomeLab ownership records for the installation.

The complete composition also illustrates independently selected Explorer, ingress, telemetry and radio profiles. Its existing external broker credential mode does not imply that those consumers are connected to this `broker` app merely because it exists in the same source. The actual `connections` targets determine that relationship. To understand how a managed producer endpoint changes the requirements, follow [connection composition](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/connect-apps.md) and the [password-file conditional record](#mqtt-password-file).

For reproducible source-only validation, use the [fully defined isolated setup](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/first-configuration.md), which defines `STACK`, `FRAMEWORK` and `PYTHON` at the selected compatible revisions. In that shell:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" \
  --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

Expected: the framework resolves every reference in the complete site. The maintained [profile integration](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/tests/test_profile_examples.py) also generates deployment packets for every selected guest using the real framework, while replacing subprocess execution and socket connection calls with test functions that fail if called. A focused check using these exact source and dependency revisions resolved five apps and generated five guest deployment packets. It also exercised the invalid cases below. The checks did not read private file contents or contact infrastructure, containers or services. The composition deliberately uses synthetic values that cannot pass checks for real deployment.

<a id="mqtt-lifecycle"></a>
### 12.6 First installation

This profile supplies no general Mosquitto configuration, ACL, password bootstrap or directory initializer. The site must already have a valid directory tree for configuration, data and logs, plus an existing probe account whose credentials are supplied in a file. The worked composition uses an already HomeLab-managed broker with `retained`; it is an offline usage example, not a procedure for setting up a new broker or importing an existing one. Structural acceptance of `fresh` does not establish a complete new-broker onboarding workflow. Do not infer such a guarantee from the profile or from compilation.

### 12.7 Later deployments

Deployments to the same HomeLab-managed instance reconcile the selected broker container and configuration and use its existing probe credentials. Both lifecycle policies allow supported updates after genuine ownership exists; an instance created through a supported `fresh` path keeps that policy. `retained` cannot create a missing installation or adopt a manually installed broker.

| Change / condition | Supported behavior and limit |
| --- | --- |
| Descriptive display label | Changes the label without renaming the broker, Compose project, service or data identity. |
| Compatible selected software/configuration | HomeLab checks the prerequisites and health requirements, then reconciles the service configuration it manages. The service or container may restart or be interrupted; uninterrupted service is not guaranteed. |
| Explicit managed-account selection | Uses the separate procedure that mounts the password file’s parent directory, updates the file and sends HUP to reload the broker. Its checks still require the expected account and protected-input ownership. Selecting it does not recreate unrelated clients. |
| Host port or listener isolation | This adapter has no `port` property. Changing the advertised endpoint neither isolates the listener nor moves its socket. |
| Service/project/runtime/data identity move | HomeLab does not automatically relocate these resources or adopt a different installation. Preserve the installed identities and paths. If the change is rejected, use the supported handling in the lifecycle contract linked below. |
| Probe material removal/change | Normal deployment checks reject removal or replacement of the existing protected probe credentials. Renaming the source does not authorize or perform credential rotation. |
| App removal / foreign existing service / HOLD | Selecting a profile does not automatically remove an app, adopt a service managed elsewhere or release a HOLD. |

The framework's [lifecycle contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md) and [support boundary](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md) define how existing ownership and inputs are checked and how rejected changes are handled. This specimen’s source checks did not install a broker, measure interruption duration or verify a running service. After authorized protected CD, verify the selected broker endpoint, the existing authentication settings, anonymous refusal and affected integration at the intended site; preserve evidence on failure. The [library troubleshooting guide](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/troubleshooting.md) is the next diagnostic route.

<a id="mqtt-diagnostics"></a>
### 12.8 Invalid cases and actionable diagnostics

Each mutation below starts from the otherwise valid complete messaging composition and changes only the stated input. These are deliberately invalid examples, not additional accepted syntax.

| Mutation | Observed source refusal at the selected revisions | Cause and correction |
| --- | --- | --- |
| Remove `apps.broker.secrets.probe` | `component.secret-required at apps.broker.properties` | The current adapter requires the existing probe credentials in a file. Restore the [probe binding](#mqtt-probe); this adapter emits the broader properties context even though the missing input is under secrets |
| Set `properties.password_file: /tmp/passwords` | `component.property at apps.broker.properties` | The path is outside the supported file location in the mounted configuration directory. Use the exact [password-file pattern](#mqtt-password-file) for the real prepared broker path; do not invent a different existing file |
| Set `properties.password_file: null` or `''` | `component.property at apps.broker.properties` | Null and the empty string do not mean that the value is omitted or defaulted. Omit it only when the managed-account mode does not require it, otherwise provide the accepted path |
| Set `properties.port: 1884` | `component.fields at apps.broker.properties` | The MQTT property object rejects unknown fields and has no port override. Choose valid placement or pursue a separately reviewed adapter capability |

After correction, rerun the real resolver and deployment-file generator with the complete composition. These failures were exercised before any native process or connection could run. They do not prove that protected inputs are correct, broker authentication works, or that a deployment will pass checks preserving the existing installation.

## 13. Worked specimen: Docker guest template

This second specimen demonstrates a reusable-default reference rather than another app page. It uses the same checked library and framework revisions as [MQTT](#12-worked-specimen-mqtt-profile). The canonical definition is [templates/docker.yaml](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/templates/docker.yaml); registration and named policies are in [stack.json](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/stack.json). The structure and permitted ranges are defined by the compatible [guest reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/guests.md) and [structural types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_types.py).

### 13.1 Purpose and complete syntax

Choose `guests.<id>.template: docker` to use these guest defaults and the named Docker and runtime selections. It does not choose any app, VMID, hostname, NIC, address, provider storage, lifecycle, account or credential. A site still supplies its complete guest declaration. The `base` template is an alternative with root size 4 GiB, boot order 20 and no template-level software or runtime selection; this `docker` template uses root size 8 GiB and boot order 50.

The following is the **complete reusable guest-template definition**, not a complete site:

```yaml
schema: homelab-components-v1
kind: guest-template
resources:
  cpu_cores: 1
  memory_mib: 1024
  root_gib: 8
  os_reserve_mib: 256
startup:
  started: true
  start_on_boot: true
  boot_order: 50
security:
  unprivileged: true
  protection: true
  nesting: true
  keyctl: false
software: [docker]
runtime: [container-host]
monitoring: {profile: linux-agent}
```

### 13.2 Fields, defaults and override behavior

Direct field destinations include [CPU](#field-docker-resources-cpu-cores), [memory](#field-docker-resources-memory-mib), [root size](#field-docker-resources-root-gib), [reserve](#field-docker-resources-os-reserve-mib), [boot order](#field-docker-startup-boot-order) and [protection](#field-docker-security-protection); every row below has its own field anchor.

These are declared template values, applied by the real resolver. `resources`, `startup` and `security` are complete mappings in the template. The site's corresponding block is partial; each explicit direct field replaces that template field. There is no arbitrary recursive source overlay. Unknown fields are rejected by the validator for the selected type. Null is not an inheritance marker.

| Path | Type / accepted rule | Template value | Omission or override behavior |
| --- | --- | --- | --- |
| <a id="field-docker-schema"></a><a id="field-docker-kind"></a>`schema`, `kind` | Fixed strings `homelab-components-v1`, `guest-template` | As shown | These markers are required for a complete definition. Neither null nor an empty value is accepted. |
| <a id="field-docker-resources"></a>`resources` | Complete typed mapping in template; partial mapping in guest | Four values below | If the guest omits the block or supplies an empty partial mapping, it inherits every direct default. Null is rejected. |
| <a id="field-docker-resources-cpu-cores"></a>`resources.cpu_cores` | Integer 1..2147483647 | 1 | If the guest omits the field, it inherits 1. An explicit integer for this direct field replaces it. |
| <a id="field-docker-resources-memory-mib"></a>`resources.memory_mib` | Integer 256..2147483647 MiB | 1024 | If the guest omits the field, it inherits 1024. The allocation must fit the effective reserve and the reservations of the selected runtimes and apps. |
| <a id="field-docker-resources-root-gib"></a>`resources.root_gib` | Integer 4..2147483647 GiB | 8 | If the guest omits the field, it inherits 8. During normal updates to an existing guest, the plan guard requires the entire disk block to remain unchanged; it rejects both growth and shrink changes. |
| <a id="field-docker-resources-os-reserve-mib"></a>`resources.os_reserve_mib` | Integer 0..2147483647 MiB; resolved value less than memory | 256 | If the guest omits the field, it inherits 256. The effective runtime reserve is at least 256 MiB, and selected requirements may increase it. |
| <a id="field-docker-startup"></a>`startup` | Complete typed mapping in template; partial mapping in guest | Three values below | An explicit guest field overrides the matching direct key. An empty guest mapping inherits all values; null is rejected. |
| <a id="field-docker-startup-started"></a>`startup.started` | Boolean | `true` | If the guest omits the field, it inherits the template value. False passes structural validation and resolution, but the saved-plan guard requires an active planned guest and rejects false. Null, an empty value and numbers are not booleans. |
| <a id="field-docker-startup-start-on-boot"></a>`startup.start_on_boot` | Boolean | `true` | If the guest omits the field, it inherits the template value. An explicit boolean replaces it. |
| <a id="field-docker-startup-boot-order"></a>`startup.boot_order` | Integer 0..2147483647 | 50 | If the guest omits the field, it inherits 50, not 20 for this template. |
| <a id="field-docker-security"></a>`security` | Complete typed mapping in template; partial mapping in guest | Four values below | Explicit guest fields override matching direct keys, subject to rules requiring true. An empty guest mapping inherits all values; null is rejected. |
| <a id="field-docker-security-unprivileged"></a>`security.unprivileged` | Boolean, required `true` | `true` | The structural security validator rejects false. |
| <a id="field-docker-security-protection"></a>`security.protection` | Boolean, required `true` | `true` | The validator rejects false. Selecting a template does not authorize disabling protection. |
| <a id="field-docker-security-nesting"></a>`security.nesting` | Boolean | `true` | If the guest omits the field, it inherits the template value. The selected `container-host` runtime requires true, so a false override passes structure checks but fails with `component.runtime-requirement`. |
| <a id="field-docker-security-keyctl"></a>`security.keyctl` | Boolean | `false` | If the guest omits the field, it inherits the template value. The runtime’s false requirement does not require keyctl to be enabled and does not itself force the guest value to false. |
| <a id="field-docker-software"></a>`software` | Sequence of named software IDs | `[docker]` | The resolver appends guest software to template software. Names resolve in the library’s software declarations; selected apps also contribute their requirements. |
| <a id="field-docker-runtime"></a>`runtime` | Sequence of named runtime-profile IDs | `[container-host]` | The resolver appends guest runtime selections to template runtime selections. It resolves the selected requirements and checks compatibility rather than inferring behavior from the name. |
| <a id="field-docker-monitoring"></a>`monitoring` | Named monitoring reference mapping | `{profile: linux-agent}` | A guest selection replaces this mapping; omission inherits it. Neither an empty value nor null disables monitoring. |
| <a id="field-docker-monitoring-profile"></a>`monitoring.profile` | Named monitoring-profile reference | `linux-agent` | The guest’s monitoring selection replaces the template’s selection. The named monitoring contract defines the behavior of its nested profile. |

The integer validator requires actual integers, so YAML booleans do not count as CPU, memory or size values. A guest's omitted resources block or empty partial mapping inherits all template fields; a present null block is not accepted. An empty guest software or runtime list contributes no additions; it does not erase the template selections. A null list is not an empty list. Monitoring omission inherits; an empty or null mapping does not mean “disable monitoring.” See [effective resolver rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_plan.py), [monitoring type](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_monitoring.py) and the downstream [saved-plan guard](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/plan_policy.py). Passing structural validation and producing a packet do not bypass the selected runtime requirements or deployment checks.

### 13.3 Partial override and complete context

This is a **guest fragment**, to replace only the template and resource selection in a complete guest:

```yaml
template: docker
resources:
  memory_mib: 3072
```

The [standalone resolver composition](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/site.example.yaml) and its [guest declaration](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/examples/minimal/guests/resolver.yaml) supply the complete context. A focused check loaded that complete source, selected `docker`, replaced its guest resources with `{memory_mib: 3072}`, then resolved it and generated its deployment files with the selected framework. Effective resources were CPU 1, memory 3072 MiB, root 8 GiB, reserve 256 MiB; startup remained `started:true`, `start_on_boot:true`, `boot_order:50`. This checks actual direct-field inheritance, not a copied table. It does not create a Docker host or demonstrate installed resource resizing.

Useful invalid variations are `memory_mib: 255` (below the structural minimum) and `security.protection: false` (violates the true-only rule). An `os_reserve_mib` equal to guest memory passes an individual nonnegative-integer check but fails the resolved reserve-less-than-memory condition. These rules come from the linked validator and resolver; this specimen's execution evidence covers the valid partial override, not a new execution of every negative branch. Existing tests of the actual components provide evidence for the scalar rules.

### 13.4 First installation and later deployments

A template supplies source defaults, so it has no independent installation, credentials or service health procedure. A guest or app that uses it must follow a supported creation path and the actual [lifecycle/support contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md). Selecting `docker` does not prove absence of an existing backend or authorize adoption.

For later deployments, template changes affect guests that inherit the changed field; an explicit guest field remains authoritative for that field. Changes to CPU, memory or startup settings alter the desired infrastructure and may interrupt a running guest or make it unreachable according to the actual supported provider path. The saved-plan guard requires an active planned guest and refuses changes to the existing disk block, including root growth as well as shrink; a syntactically valid value or provider-proposed operation is not deployment permission. Moving persistent identities or paths, removing protection and replacing resources arbitrarily are not supported by describing different defaults. Compare resolved output before adopting a library change and follow the consuming guest's documented operational limits and the behavior already tested on its target.

## 14. Design rationale and source use

These are selected documentation techniques, not a claim that the current suite matches every source or that another system's behavior applies to HomeLab.

| Primary pattern | Adopted rule and HomeLab-specific judgement |
| --- | --- |
| [Compose specification](https://github.com/compose-spec/compose-spec/blob/main/spec.md), [services](https://github.com/compose-spec/compose-spec/blob/main/05-services.md) and [Docker reference](https://docs.docker.com/reference/compose-file/) | Use readable YAML, directly anchored attributes, linked object definitions and coherent compositions. Preserve explicit ownership and the effects of references; do not inherit Compose's broad optional-implementation or ignored-attribute behavior into HomeLab's closed contracts. Source and implementation references can differ; record which is authoritative. |
| Compose [networks](https://github.com/compose-spec/compose-spec/blob/main/06-networks.md), [volumes](https://github.com/compose-spec/compose-spec/blob/main/07-volumes.md), [configs](https://github.com/compose-spec/compose-spec/blob/main/08-configs.md), [secrets](https://github.com/compose-spec/compose-spec/blob/main/09-secrets.md) and [workload dependencies](https://github.com/compose-spec/compose-spec/blob/main/workload_spec.md#depends_on) | Link declaration to consumer and back; distinguish references, access, external lifecycle and explicit dependency conditions. Use short/long-form comparisons only where HomeLab actually accepts alternatives; do not add Compose syntax to a HomeLab example. |
| Terraform AWS [resource reference](https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/r/instance.html.markdown) and [provider reference](https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/index.html.markdown) | Distinguish input arguments from outputs, document interactions and default precedence, and explain when a resource stops, starts or is recreated. Do not present Terraform’s supported operations or import capabilities as HomeLab guarantees. |
| Terraform [author guidance](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/end-user-documentation.md) and [Registry documentation](https://developer.hashicorp.com/terraform/registry/providers/docs) | Require complete coverage of arguments and attributes, linked nested blocks, functional self-contained examples and version-linked documentation; generate reliable structure while authoring behavior. Registry-specific macros, front matter and sentence rules are not requirements for GitHub Markdown. |
| AWS CloudFormation and Azure resource-reference patterns | Use predictable records for syntax, properties and effects, with explicit references for compatibility and changes. Adapt the records to library profiles rather than a cloud resource catalogue. |
| Kubernetes API/concept/task patterns | Link fields to their types, concepts and task guides, with routes back. Keep manifests, prerequisites and results consistent, and distinguish declared intent from observed service state. |
| Stripe operation/flow patterns | Explain concrete configuration effects in readable language and link the next operation or relevant context where readers need it. Accepted or compiled input is distinct from a completed installation or a working service. |
| OpenAPI named-object/reference patterns and GitHub REST concept/guide/reference patterns | Use named nested types and stable contextual references with examples and prerequisites; formal tables alone do not teach newcomers. Plain committed Markdown must work without another site's unresolved macros. |

The practical target is a predictable, complete and navigable library reference combined with useful learning and operating paths. Compliance is established by the [inventory and review evidence](#10-verification-and-review-rubric), not by resemblance to a vendor's page layout.
