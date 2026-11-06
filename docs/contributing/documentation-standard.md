# HomeLab Stack documentation standard

This standard defines how to design, write and review documentation for the reusable `homelab-stack` application library. Documentation is part of the library's public contract. A reader must be able to choose a profile, supply its bindings, understand its effects and limits, and find the precise upstream contract without knowing an implementation discussion or another consumer's environment.

**MUST** identifies an acceptance requirement. **SHOULD** identifies the normal approach; a documented, reviewed reason may justify another approach. **MAY** identifies an option. These words govern documentation quality; they do not create capabilities in HomeLab. Examples and operational claims MUST follow the accepted implementation at the documented compatible revisions.

This is the canonical documentation policy for this library. The [contributor workflow](../contributing.md) and [application-profile template](../templates/application-profile.md) apply it to changes; [section 11](#11-contributor-and-agent-integration) defines their ownership. Existing source checks have the bounded scope described in [documentation conformance](../testing.md#documentation-conformance); adoption does not certify every semantic or native claim.

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

**S1.1 — Serve decisions at the library boundary.** The suite MUST serve new users choosing an application, site authors composing instances, operators assessing supported changes, and contributors extending reusable definitions. It MUST explain both the reusable definition and its application in a consuming site. A catalogue of product names alone is insufficient.

**S1.2 — Keep the three owners explicit.**

| Owner | Canonical responsibility | Documentation responsibility |
| --- | --- | --- |
| `homelab` | Typed grammar, reference resolution, validation, compilation, packet lowering and deployment capabilities | Exact general field/type rules, diagnostic and lifecycle contracts, execution and support boundaries |
| `homelab-stack` | Registered app profiles, guest templates, software/image selection, runtime/health/monitoring defaults and reusable policy fragments | Which framework capabilities each profile selects; its effective requirements, defaults, compatible placement, variants, dependencies and limits |
| Consuming deployment repository | Concrete provider/site allocation, trust, credentials, access policy, operating authority and qualified environment | Actual preparation, installation, service acceptance and site operating procedures |

Library pages MUST NOT make consumers adopt a fixed environment or publish private repository identities, real allocations, credentials, local operator paths, operational history or recovery artefacts. Standard runtime target paths that are part of a public adapter contract are legitimate reference information; an author's local checkout path is not.

**S1.3 — Compose, do not duplicate authority.** Reuse an existing component and link its owning contract. Do not create another validator in prose, reimplement an execution engine in a guide, or offer arbitrary environment/command/mount/Compose override bags as documented configuration. A missing typed capability requires a separately scoped contract change before it can appear as supported usage.

**S1.4 — Preserve independence.** A profile MUST state actual companion requirements without imposing unrelated applications. Supporting containers belong to their owning app. A guest template MUST NOT imply an app bundle. A composition can illustrate several apps while explaining which are optional and which relationships make them necessary.

**S1.5 — Keep status and evidence distinct.** Pages MUST distinguish accepted contract facts, source-inspected effects, tested effects, native qualification and unknown behavior. A proposal MUST be labelled as a proposal and excluded from supported syntax/examples. Documentation MUST follow desired configuration rather than reconstruct an environment's migration or recovery history as an installation prerequisite.

## 2. Structure and page types

**S2.1 — Use a small entry point and linked depth.** The root README SHOULD explain the library, supported platform, owner boundaries and four entry routes: learn, select, compose, maintain/contribute. It MUST link a canonical documentation index. It MUST NOT absorb all field reference, installation and troubleshooting material. Plain GitHub-hosted Markdown is a complete delivery format; an HTML platform is not required.

**S2.2 — Give each page one principal job.** Existing useful routes SHOULD be preserved or replaced with pointers during later adoption. The following hierarchy is a responsibility model, not permission to move current files without review.

| Page type | Appropriate reader task | Required shape and limits |
| --- | --- | --- |
| Overview / index | Understand scope or choose a route | Brief purpose, supported platform, owner boundaries, task-oriented links; every registered profile and variant is discoverable |
| Concept | Understand a relationship or tradeoff | Explain library/site/guest/app, scope, ownership and effects; use concrete examples; link exact reference and task pages |
| Tutorial | Learn by completing a reproducible result | State initial environment and final observable result; supply complete source and ordered steps; include a practical variation and explain evidence limits |
| How-to | Complete one bounded task with known prerequisites | State outcome, prerequisites, steps, verification and failure boundary; link concepts rather than reteach the entire model |
| Component/type reference | Look up framework syntax and behavior | Link the compatible upstream canonical type. Author a local reference only for library-owned declarations; distinguish input from resolved/generated output |
| App/profile reference | Choose and configure one registered profile | Use [section 4](#4-profile-template-and-shared-declaration-pages); include variant choice, binding records, complete usage and precise lifecycle limits |
| Guest-template reference | Select defaults and override them deliberately | Exact inherited resources/startup/security/software/runtime/monitoring, override rules, bounds and effects; no site allocations |
| Composition guide / example | Join independent profiles into a coherent site | Explain each relationship and its owner, placement alternatives, values/readiness/access/trust/account distinctions, complete canonical source and expected resolved result |
| Operations guide | Maintain a supported owned installation | Preconditions, authority boundary, actual CD behavior, persistent identities/material, interruption/refusal behavior and service checks; site procedure remains with its owner |
| Troubleshooting / diagnostic reference | Understand and act on a failure | Symptom or exact diagnostic, phase, cause, distinguishing evidence, supported correction, verification and stop/recovery boundary |
| Contribution / authoring | Extend or review the library | Registration, standards/templates, source/example/test synchronization, evidence requirements and review gates |

**S2.3 — Avoid competing encyclopedias.** A profile page explains its selected requirements, not every unused framework capability. A composition guide connects canonical definitions rather than repeating their full field tables. A concise glossary can define unfamiliar terms, but MUST link readers onward to behavior and examples.

## 3. The newcomer and maintenance journeys

**S3.1 — Make four distinct stages navigable.** A successful offline tutorial is valuable but does not prove a complete path to a supported installation. The index and tutorial conclusion MUST provide these routes, with availability honestly stated:

| Stage | Observable result | Required explanation |
| --- | --- | --- |
| Offline synthetic tutorial | Source resolves and a selected packet lowers | Exact compatible source/tooling; synthetic values and private-path metadata; no native effects; inspectable output |
| Deployment preparation | A real consuming site has qualified prerequisites | Supported platform/provider, selected profile capability, trust, state/backup ownership, credentials, images/packages, accounts/data prerequisites, network/access and protected CD; link each owner |
| First installation | A supported new owned guest/app is created | Actual creation path and exclusions; required prepared inputs; what the framework does and what the operator/vendor must do |
| Service verification | Intended service and selected integrations work | Actual endpoint/protocol/authentication, persistence and relevant integration checks; record environment/revisions and limits |

If a public, qualified first-install procedure is unavailable, the page MUST say what is missing and link the supported preparation/operations boundary. It MUST NOT fill the gap with an invented commissioning command, refer vaguely to an unspecified existing site, or describe retained source as an import path.

**S3.2 — Include a later-deployment route.** Explain how an installed, genuinely owned instance consumes reviewed library/framework changes through protected CD. Link profile-specific limits and effective-default changes. A newcomer MUST be able to find this route from the installation section; an existing operator MUST be able to reach it directly from the profile page.

## 4. Profile, template and shared declaration pages

**S4.1 — Use a complete profile page contract.** Every registered profile and public variant MUST have a canonical reference page containing the following information. Headings can group related small records, but the information cannot be replaced with an end-of-page source link.

1. **Purpose and choice:** outcome, selection ID, adapter, supported platform, relevant alternatives/variants and when to choose each; owned services/helpers/native units and important external requirements.
2. **Placement and ownership:** supported same/separate guest layouts, repeated-instance limits, socket/native/service/project/data/credential conflicts; distinguish namespace checks from native qualification.
3. **Syntax:** smallest meaningful selection fragment, exact placement and shape, plus a link to its complete canonical composition. Include the reusable profile declaration or a precise source link and field navigation.
4. **Bindings and properties:** typed [property records](#5-property-and-binding-records) for interface roles, listeners/publications/endpoints, storage, connections, accounts, secrets/authentication, devices/capabilities, app properties, origin/exposures and selected optional features.
5. **Effective defaults and selected policies:** software/image/runtime/health/monitoring/resource policy references; exact inherited versus overridden behavior; authoritative version source; budget meaning and platform limits.
6. **Resolved result:** addresses/ports and identities derived from bindings, generated configuration/runtime artefacts relevant to consumers, readiness/dependency behavior and access effects. Generated output is not another authoring API.
7. **Minimal and practical complete usage:** known valid canonical source, app/guest IDs, dependency tuple, expected results and evidence. Show a useful nested or conditional feature where supported.
8. **First installation:** supported creation behavior and prepared-input limits, including whether vendor setup/configuration/data/account creation exists.
9. **Later deployments:** exact change classifications from [section 8](#8-installation-updates-and-operational-limits), persistence/material/identity restrictions and failure boundaries.
10. **Invalid cases and diagnostics:** at least two meaningful distinct failures, actual layer/code/path and a supported repair; link detailed diagnostics and successful examples.
11. **Navigation and provenance:** parent catalogue/index, related variants/types/concepts/tasks, complete examples, relevant source/tests and compatibility/change references.

**S4.2 — Apply topics deliberately.** A profile without devices MUST say once that it selects no device role; it does not need a page of serial warnings. An app with no inbound exposure MUST say so without inventing frontend routes. A pure default declaration has no independent service health or installation step: explain its consumer and link that consumer's lifecycle. Required, conditional or security-relevant topics MUST never disappear merely because the current example does not use them.

**S4.3 — Guest-template pages are a different contract.** For each template, document exact complete default blocks and the meaning, bounds and override behavior of every direct field. List software/runtime/monitoring references and effective admission floors separately. Explain which site fields remain required and what the template does not allocate. Show an inherited case and a partial override with the resulting effective values. Explain the blast radius of a template change on inheriting guests. The [Docker template specimen](#13-worked-specimen-docker-guest-template) demonstrates this page type.

**S4.4 — Shared declarations need their own reference.** Library-owned software roles, runtime profiles, health/monitoring profiles, image policies, assets and reusable policy fragments MUST have canonical definitions. App pages MUST link directly to the selected record. Record process/security policy, budget units, limits/reservations, probes/timeouts, named requirements and source/override authority where applicable. Do not copy volatile package versions or image digests into every app page. A deliberate excerpt MUST be identified as an excerpt and checked against the manifest.

**S4.5 — Variants are selectable contracts.** A public-image or database-administration variant MUST state its distinct software, privileges, bindings and lifecycle support. It MAY share unchanged explanation through canonical links, but MUST remain understandable from its own selection page. Documentation for a permissive generic type MUST NOT imply that every adapter or variant accepts it operationally.

## 5. Property and binding records

**S5.1 — Give every accepted path a record and stable destination.** Cover parent objects, nested options, map values, list items, discriminated alternatives and conditional leaves. Use a compact index table for scanning, then anchored property records for nontrivial fields. A one-line table is sufficient for a simple scalar only when it contains all applicable information. A long prose paragraph without a discoverable property destination is insufficient.

Use this reusable record form. This is an **authoring form, not YAML syntax or a supported feature**:

| Record item | Required content |
| --- | --- |
| Name and location | Exact authored path, map/list scope, canonical anchor; distinguish reusable declaration from site binding and generated result |
| Purpose and effect | What changes for the user; owned resource or consuming behavior |
| Type and syntax | YAML scalar/sequence/mapping, element/key types, named nested type link and all accepted alternatives; quote strings where YAML could change their type |
| Presence | Required/optional/conditional and exact condition; layer that enforces it, including an adapter floor stricter than profile metadata |
| Defaults and resolution | Literal default or explicit absence; actual component/profile/resolver applying it; inheritance/override/append order and granularity |
| Omitted, null and empty | Whether each is accepted and its actual effect; distinguish absent from empty mapping/list/string and false/zero where meaningful |
| Value constraints | Units, inclusive bounds, enum values, case rules, pattern and path/name format; unknown-key policy; no range merely inferred from an example |
| Interactions | Prerequisites, dependencies, conflicts, conditional siblings and supported combinations, with direct links |
| References and bindings | Target kind, lookup namespace/root, qualification/confinement, missing/wrong-type/cycle behavior; whether selection yields values, ordering, access, trust or account effects |
| Outputs | Resolved/generated value or owned artefact relevant to readers, and whether it is public/private; do not advertise internal incidental structure as stable output |
| Security and owner | Credential/data/account ownership, file/environment/reference metadata versus actual material, privilege and transport effects; permissions only where enforced |
| Lifecycle and limits | Concrete first/later effects, interruption/restart/replacement/refusal conditions, stable identities and unsupported/unqualified operations; link the owning lifecycle |
| Examples and failure | Minimal accepted value, useful combined/conditional case where relevant, intended diagnostic and repair link |
| Compatibility/provenance | Source of truth at the compatible version and change reference for changed semantics; tests/evidence at the appropriate boundary |

**S5.2 — Avoid meaningless boilerplate.** Every path MUST have type, presence, default/absence and constraints; references MUST have resolution rules. Complex effects MAY be shared at a clearly linked block/type level when they apply uniformly. For a scalar measured in MiB, do not add a meaningless enum field. For a display label, state that it does not rename persistent resources and link identity; do not duplicate the whole deployment procedure. An inapplicable item SHOULD be omitted or explained once for its group. Unknown behavior MUST be recorded as unknown with its affected claim, rather than disguised as “not applicable.”

**S5.3 — Describe actual merging.** Never use “inherits defaults” or “overrides configuration” alone. State which map's direct keys are copied, which instance keys replace them, which lists append, and whether nested values replace or merge. Identify the default-applying layer; a schema annotation is not evidence that a default is inserted. Do not invent a general overlay, patch or recursive merge language.

**S5.4 — Separate acceptance layers.** For each conditional requirement, distinguish structural type acceptance, resolved reference/feature requirements, selected adapter lowering requirements and runtime/native guards. If metadata says optional while the selected adapter requires a binding, expose the effective requirement near that binding. The [MQTT probe record](#mqtt-probe) is an example. This discrepancy is a documentation and contract-maintenance concern; it is not permission to relax the adapter guard.

**S5.5 — Record outputs separately from inputs.** A generated Compose service, resolved address, workflow dependency or private packet path MUST be marked as output. Explain the source that determines it. Do not suggest editing generated files or treating a runtime receipt as ordinary desired source.

## 6. Contextual links and relationship navigation

**S6.1 — Link where the reader needs the explanation.** A property record MUST link its nested type, important prerequisite, interacting property, complete example and relevant diagnostic at the sentence or table row where the relationship matters. A generic related-links section does not satisfy this rule. Descriptive link text MUST identify the target subject; avoid “here” and unexplained “see docs.”

**S6.2 — Support the whole relationship in both directions.** A profile's interface role should lead to the guest-interface binding contract and a concrete binding example. The binding/concept guide should lead back to representative profiles. A nested type should identify its parent/consumers. A diagnostic should link to the failing field and valid example; that field should link to its important diagnostic. A complete example should name the profiles and concepts it demonstrates, and those profiles should link to its exact app IDs.

**S6.3 — Explain this relationship chain explicitly.** Library composition guidance MUST cover these distinctions with links at each relevant edge:

| Relationship | What must be explained |
| --- | --- |
| Site network → guest NIC | Site owns context/CIDR/bridge/VLAN/gateway; guest chooses slot/MAC/address/control interface; reference is not NIC allocation by an app |
| Guest NIC → app interface role | Role names an app requirement; binding selects a NIC in that app's guest; role is not a network ID; allowed loopback/app-network alternatives are profile-specific |
| Interface role → listener/publication → endpoint | Actual socket namespace/bind/protocol/port, host publication versus private listener, endpoint address derivation; advertisement does not establish isolation or grant traffic |
| Consumer connection → producer endpoint/external target | Typed value resolution, source role, explicit readiness, hostname, credential/account and transport; selecting a URL alone creates none of these other effects |
| Endpoint → exposure | DNS naming versus an HTTPS frontend route, ingress/TLS/middleware/authentication choices, ownership and backend transport; exposure does not retroactively isolate a wildcard listener |
| Template/profile → instance | Exact default and override rules; authoritative reusable selection versus concrete site identity/allocation |

**S6.4 — Keep stable destinations.** Use predictable property headings or explicit stable anchors for long dotted paths and ambiguous repeated names. A table containing a field name is not automatically an anchor. Preserve published anchors when moving/refining pages or add a working compatibility anchor/pointer. Avoid duplicate heading slugs and line-number-only navigation as the primary public API reference. In-page contents SHOULD be present on long pages.

**S6.5 — Keep canonical definitions singular.** Define each shared concept/type once under its owner. Brief local explanation SHOULD summarize the selected effect and link its source. Do not duplicate field tables across guides. Repeated contextual links are useful across distant sections where readers enter independently; linking the same word repeatedly within one paragraph adds noise. Link important relationships, not every occurrence of an ordinary noun.

**S6.6 — Use compatible public links.** Within a repository, prefer paths that work in the committed tree. Cross-repository behavior and test links MUST identify a compatible published revision or release. Explain how it relates to the authoritative selection; do not create a second pin policy in prose or point at mutable `main` as proof for a pinned consumer. New version/change notes MUST link back to affected profiles/properties and explain inheriting-instance effects. External vendor guidance is supplemental and cannot override HomeLab support.

**S6.7 — Prevent orphans and drift.** Every page MUST be reachable from a canonical index; every registered profile/variant and template MUST be indexed. Review relative links, generated/explicit anchors, public cross-repository targets, moved-page pointers and contextual targets after changes. No broken links or orphan references may remain in the changed surface. Verify external links with bounded checks rather than relying solely on HTTP success: confirm the target topic/version/anchor still matches the claim.

## 7. Examples, failures and reproducible commands

**S7.1 — Label example scope before its fence.** Use one of: complete reusable definition, complete site/composition, typed object/map value, explanatory fragment, non-runnable syntax or deliberately invalid example. A fragment MUST name its placement and link complete surrounding source. Type placeholders belong only in explicitly non-runnable syntax. No unexplained `...`, assumed existing object or unresolved placeholder may appear in a claimed complete executable example.

**S7.2 — Keep complete compositions canonical.** A profile file proves a reusable definition; it does not prove valid usage. Every registered profile and variant MUST map to a complete synthetic composition and an identified instance that passes the real compatible resolver and packet lowerer. Store example bodies once. Excerpts MUST be extracted or checked against those bodies. One composition MAY cover several profiles, but the catalogue MUST map each selection to its exact app and tested outcome.

**S7.3 — Cover behavior, not only presence.** Each profile MUST have a minimal meaningful selection and a practical case showing a relevant relationship/conditional feature. Across the suite, cover supported same/separate guest layouts, independently selected apps, repeated profiles, physical/loopback/private bindings, explicit readiness versus values, exposures, managed versus existing credentials, selected variants and overrides. Do not force irrelevant features into every profile. Cover every nontrivial conditional branch through a suitable direct contract test or focused composition, with explicit traceability.

**S7.4 — Use coherent synthetic values.** Examples MUST use internally consistent names, addresses/subnets/gateways, ports, domains, ownership and source paths that satisfy the owning contract. Use `.invalid` domains and deliberately synthetic endpoint/allocation values; explain any contract-required address convention. Secrets MUST be references, synthetic fixtures or clearly non-secret illustrative material. Do not include usable credentials, real site identities or a private history-derived layout. A safe offline example can deliberately refuse real deployment admission; document that boundary.

**S7.5 — Show useful failures.** Include at least two distinct, relevant invalid variations per profile: for example a missing required binding and a conditional/path/placement conflict. Keep all unrelated inputs valid so the check reaches the stated boundary. Provide the exact diagnostic code and path/message where stable, the phase that emits it, cause, supported repair and expected recheck result. Never invent a helpful-sounding error. If diagnostic context is broader than the literal source location, state that fact. Reuse existing upstream negative coverage where it proves the claim; do not add redundant tests that only search for prose.

**S7.6 — Make commands reproducible.** Define checkout/revision, compatible framework selection, working directory, interpreter/dependencies, files, variables and required tools before use. Commands MUST use actual interfaces. Source-only commands MUST not acquire target authority. Resolve disposable source roots physically where source confinement requires it, use new output children where overwrite is refused, and keep private/runtime outputs out of source. Link a fully defined setup instead of copying it inconsistently onto every page. State expected output/result and the next inspection, not merely an exit code.

**S7.7 — Bound the proof.** Parsing YAML proves syntax, not references; a real resolver proves source relationships, not packet lowering; source/lowering tests do not prove target installation. A successful service check does not establish every lifecycle or recovery path. Tests with mocks MUST name the boundary replaced. Do not describe source composition tests as end-to-end service verification.

## 8. Installation, updates and operational limits

**S8.1 — Use plain lifecycle headings.** App pages MUST contain **First installation** and **Later deployments**. “Fresh/update supported” or “guarded plan” alone is insufficient. `lifecycle: fresh` permits supported creation when the owner/backend is absent and continues through ordinary owned updates. Readers MUST NOT be told to toggle it after installation. `retained` requires a genuinely existing HomeLab-managed instance, refuses creation and is not import/adoption authority. Guest and app lifecycle policies are separate; explain a supported new app on an already owned guest when relevant.

**S8.2 — Specify first-install prerequisites and ownership.** Name which guest/data/config/account/trust/image/package/private-material requirements are created by the selected path, which must be prepared by the consuming site and which are unsupported/unqualified. A ready vendor image, profile listing or compiled packet is not commissioning evidence. Do not imply arbitrary account/configuration/ACL generation from a role binding. Standard source describes desired state; environmental preparation or recovery uses its separately reviewed procedure.

**S8.3 — Classify changes concretely.** For each meaningful profile/template change, document input condition, applying/enforcing layer, owned resources affected, expected effect, interruption and proof/qualification limit. Use the following categories only when evidence supports them:

| Classification | Required statement |
| --- | --- |
| Supported ordinary update | Exact fields and same-owner requirements; resulting configuration/service/infrastructure effects |
| Potentially disruptive | What may stop, restart, reload or lose reachability; when and why; whether measured or inferred |
| Replacement-triggering | Actual replacement trigger and data/identity effect. Distinguish a provider-proposed replacement from a HomeLab-supported operation; if HomeLab refuses the proposed replacement, document that trigger and refusal rather than implying it will execute |
| Refused | Exact prohibited change/condition, diagnostic/phase where known, preserved evidence and supported next step |
| Separately prepared/reviewed | External work and its owner; link an existing procedure if one is supported; no fictional switch |
| Not yet qualified / unknown | Specific behavior/environment without evidence; what existing source tests do prove and what future evidence would resolve it |

A blanket “updates are safe” is prohibited. A blanket “everything replaces” is equally misleading. Distinguish a container reload, owned-service restart, peer restart, guest reboot, resource recreation and data migration. Do not promise zero interruption without target evidence.

**S8.4 — Describe default/software adoption.** Profile/template/software/runtime/image changes can affect every inheriting instance. Identify the authoritative manifest, compare effective output/dependencies/budgets before adoption, and state pinned digest versus allowed update policy. Do not promise automatic upgrades, rollback or data migration merely because image selection validates. Do not duplicate volatile versions across pages.

**S8.5 — Preserve operational boundaries.** Explain stable guest/app/project/service/network/data/credential identities and current ownership proofs where they constrain changes. Ordinary updates do not implicitly relocate data, rotate/remove private material, import foreign resources, delete abandoned services, bypass locks or release a HOLD. Deletion, rollback, restore, retry and replacement MUST be described only through existing supported contracts. Where failure can occur after infrastructure/preparation effects, do not claim an atomic no-change refusal. Diagnostics must direct operators to preserve current evidence and use the existing qualified recovery boundary.

**S8.6 — Explain the CD maintenance flow without site secrets.** Describe reviewed desired source and published compatible dependencies → offline checks and effective-plan comparison → consuming site's protected admission/CD → infrastructure/configuration phases → profile health and service acceptance. Name actual layer ownership: OpenTofu infrastructure/state and Ansible configuration/services. The library provides reusable definitions/workflows; it does not give the reader another site's operating permission. Site-specific settings, secrets, approval procedure and service observations remain with that site.

## 9. Authoring, inventories and generation

**S9.1 — Build a structural and semantic inventory before claiming completeness.** Read the actual library index, referenced complete declarations, compatible framework closed types, resolver/property/adapter/lowerer/runtime guards, diagnostics and maintained examples. Schema enumeration alone cannot find every conditional or adapter-specific requirement. Inspect accepted extension/variant paths, not just common defaults.

The inventory MUST distinguish at least these entities:

| Entity | Inventory key and required evidence |
| --- | --- |
| Profile / variant / template | Registered ID, source, adapter, canonical page, catalogue link and compatible revision |
| Property / nested type / binding role | Fully qualified path with variant/discriminator; actual type/presence/default/merge layer and page anchor |
| Semantic rule | Stable review identifier, condition, affected paths, owning source/phase, explanation anchor and relevant validation evidence |
| Reference edge | Source/target type and scope, resolution/confinement/dependency/access semantics, forward/reverse navigation and example |
| Diagnostic | Actual code/message/context and emitting phase, rule/field link, corrective guidance, useful negative case |
| Example / scenario | Canonical source, profile/app IDs, required dependency tuple, expected resolution/lowering/refusal and evidence level |
| Lifecycle claim | Change condition, supported/refused/disruptive/unknown classification, owner/effect and source/test/target evidence |

**S9.2 — Maintain an auditable traceability record.** A contributor/reviewer MUST be able to follow `inventory item → canonical page#anchor → explanation → example or justified non-example → relevant test/evidence`. Record source revision and applicability. Include reverse checks for pages documenting removed/unaccepted fields, stale defaults, obsolete variants and unsupported lifecycle guarantees. A list of all profile names passing compilation is useful but does not establish field/rule/diagnostic completeness.

Example inventory row form, **not a new configuration schema**:

| ID | Owner/source | Page#anchor | Rule/default/condition | Example | Evidence and status |
| --- | --- | --- | --- | --- | --- |
| `mqtt.secret.probe.file` | Selected MQTT adapter requirement | MQTT#probe | File source required despite optional profile metadata | Messaging composition / broker | Real resolver+lowerer negative and positive; native secret material not exercised |

**S9.3 — Generate structure where reliable; author explanation.** A later documentation tool MAY extract IDs, field paths/types, enum/bound literals, declared defaults, catalogue links and example coverage. The generator MUST use the accepted source and preserve stable destinations. It MUST NOT infer lifecycle guarantees, operational effects, intent, prerequisites or conditional semantics from names. Human/agent authors remain responsible for readable explanations, choices, relationships, useful failures and qualification limits.

Do not duplicate a schema into a manually maintained second authority. A generated table is appropriate only when accurate, concise and linked to authored context; internal implementation fields, repeated empty attributes and unexpanded schema noise SHOULD be excluded from the reader page. Generation inputs/output ownership and reproducibility MUST be clear. This standard does not require or authorize implementing a generator.

**S9.4 — Synchronize the change unit.** A profile/contract/default change MUST update its documentation, examples, inventory/rule traceability, diagnostics where affected and meaningful existing tests in the same reviewable change. A framework change may require coordinated library documentation, but source compatibility and pin adoption remain separate reviewed decisions. Never refresh frozen output/hash expectations merely to hide unexplained drift.

## 10. Verification and review rubric

**S10.1 — Require measurable completion.** For the changed scope, acceptance requires:

- 100% of registered profiles/variants/templates mapped to canonical discoverable pages and complete applicable usage examples.
- 100% of inventoried accepted property paths, nested alternatives and binding roles mapped to accurate records; no unexplained entries or documented phantom fields.
- 100% of inventoried semantic/conditional/reference/lifecycle rules and relevant diagnostics mapped to explanation and suitable evidence, or an explicitly reviewed qualification limit.
- All claimed complete examples pass their owning structural validator; selected complete sites resolve and lower with the real compatible library/framework.
- Negative examples reach their documented refusal; defaults/constraint/override examples match actual effective output.
- No broken local links/anchors, unresolved placeholders or orphan pages in the changed surface; compatible external public targets checked for meaning as well as reachability.
- All factual behavior claims cite/trace to source or evidence; actual deployment/service verification is claimed only when performed for that outcome.

The denominator MUST come from an inspected inventory and be stated. A bare “100% covered” or code coverage percentage is insufficient. Until the full inventory exists, report sampled coverage and unknown completeness, not a count of missing fields invented from sampling.

**S10.2 — Choose evidence by boundary.**

| Evidence | What it can establish | What it cannot establish alone |
| --- | --- | --- |
| Source inspection / structural inventory | Declared shape, conditions and implementation behavior under review | Successful execution or target support |
| Direct real component tests | Type and range checks, omission/null/empty inputs, unexpected fields and conditional refusals at that contract | Whole-site references, app placement or deployment |
| App/guest units with mocked component contracts | Library selection/default wiring and isolated app/guest behavior | The mocked component's validation semantics |
| Real resolver + lowerer integration | Compatible profile bindings, dependency/traffic/identity/resource checks, generated packets | Native installation or service availability |
| Controller/helper or isolated protocol tests | Specific guarded transitions, material/ownership/protocol behavior under the named fixture | Protected CD or all target platforms |
| Authorized deployment evidence | Actual selected source/workflow applied to the recorded environment | Every service integration or rollback/recovery path |
| Actual service acceptance | Checked endpoint/authentication/persistence/integration behavior | Unchecked lifecycle changes or universal support |

Run existing relevant example/contract/navigation gates and repository-required checks. Add evidence only where an unproved claim or changed behavior needs it. Do not create tests that merely restate implementation or demand a new deployment for a prose-only clarification. Reuse valid evidence with its exact scope and revision; re-run when changed inputs invalidate it.

**S10.3 — Apply a severity rubric.**

| Severity | Examples | Review disposition |
| --- | --- | --- |
| Blocker | Private/secret leakage; invented supported API; destructive/recovery instructions outside a real contract; false installation/service verification claim; an example directs unsupported identity/data adoption | Must fix before acceptance |
| Major | Missing accepted path/conditional rule; wrong default/binding/precedence; complete example fails or is a fragment; misleading lifecycle/restart/replacement claim; missing critical contextual link; untraceable coverage claim | Must fix before the affected page/change is complete |
| Moderate | Discoverability gap, unclear variant choice, insufficient useful failure guidance, stale noncritical target or repeated competing explanation | Fix in the change unless explicitly deferred with owner/scope and no false completeness claim |
| Minor | Wording, formatting or a noisy repeated link without behavioral ambiguity | Correct when practical; does not excuse larger defects |

**S10.4 — Critique as a reader and as a contract reviewer.** Starting from the README, attempt to choose one profile and follow its field → type → prerequisite → complete example → diagnostic → later-update path. Inspect Markdown rendering, heading hierarchy, table width and code fences. Then compare every changed property/rule/default to its source and effective result. A peer review is independent only when another reviewer actually performed it; an author's self-review MUST be labelled self-review.

**S10.5 — Definition of done.** The changed inventory is reconciled, meaningful examples/negative cases pass at their stated boundary, links/navigation render and resolve, all blocker/major findings are corrected, moderate deferrals are explicit, source/example/docs agree, existing quality/security/review gates remain intact, and remaining operational unknowns are specific. For initial standards adoption, acceptance also requires agreeing the canonical policy/template routes; it does not imply the existing suite has already been redesigned to comply.

## 11. Contributor and agent integration

**S11.1 — Use one local policy.** This file governs library profiles, templates, defaults and composition guidance. The [contributor workflow](../contributing.md), [application-profile template](../templates/application-profile.md) and [guest-template template](../templates/guest-template.md) implement it. The selected framework owns grammar and deployment behavior; its compatible documentation remains authoritative for those contracts.

**S11.2 — Synchronize source, examples and records.** The working agreement requires canonical documentation, test-local source/document pointers, complete synthetic examples and relevant checks to change together. Follow [documentation conformance](../testing.md#documentation-conformance). The standard's worked specimens below retain their historical evidence coordinates; current reference pages are the consumer-facing records. An inventory of supplied declarations does not establish coverage of all optional framework syntax or procedural lifecycle rules.

**S11.3 — Review outcomes.** Reviewers apply [section 10](#10-verification-and-review-rubric), including meaningful contextual links and unsupported-operation boundaries. Report inspected source, tested integrations, hosted checks and actual service verification separately. Do not relax existing coverage, security, signing or review gates.

## 12. Worked specimen: MQTT profile

This specimen demonstrates a finished profile reference at a checked public snapshot. It is not a new feature or a request to change the library. Its source basis is [`homelab-stack` at `a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d`](https://github.com/theaussiepom/homelab-stack/tree/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d) with its [selected framework `52913d4ba03f85e7d734a85b08c93e73f320455d`](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/.github/workflows/phase.yml). These are evidence coordinates, not a second dependency policy. Recheck facts against the selected tuple when adopting changed source.

[Choice and syntax](#mqtt-choice) · [Binding records](#mqtt-bindings) · [Probe](#mqtt-probe) · [Password file](#mqtt-password-file) · [Examples](#mqtt-example) · [Lifecycle](#mqtt-lifecycle) · [Diagnostics](#mqtt-diagnostics)

<a id="mqtt-choice"></a>
### 12.1 Purpose, choice and reusable syntax

Select `mqtt` to run one Mosquitto broker container with explicitly prepared broker configuration, data and log directories. It owns service role `mqtt` and uses the `mqtt` adapter. MQTT Explorer is a separate optional consumer; selecting this broker does not select Explorer, an identity service or another home-automation app. The supported platform is Debian 13 LXC on Proxmox. Source compilation is separate from service acceptance.

The following is the **complete reusable app-profile definition** from [apps/mqtt.yaml](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/apps/mqtt.yaml). It is a library definition, not a complete consuming site:

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

The complete declaration is registered as `mqtt` through [stack.json](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/stack.json). The current adapter adds the effective [file probe requirement](#mqtt-probe) despite optional metadata above.

<a id="mqtt-bindings"></a>
### 12.2 Declaration and site binding records

Jump to [interface roles](#field-mqtt-interfaces), [listener](#field-mqtt-listeners-mqtt), [endpoints](#field-mqtt-endpoints), [storage roles](#field-mqtt-storage), [software](#field-mqtt-software), [runtime](#field-mqtt-runtime) or [private role metadata](#field-mqtt-secrets-probe).

The following records describe this selected profile. General syntax is owned by the compatible [framework app contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md) and [library contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/library.md). The complete [broker instance](#mqtt-example) supplies all surrounding site identity and resources.

| Declaration path | Exact selected value/type | Effective meaning and corresponding site input |
| --- | --- | --- |
| <a id="field-mqtt-schema"></a><a id="field-mqtt-kind"></a>`schema`, `kind` | Strings `homelab-components-v1`, `app-profile` | Complete reusable definition markers, not a site's root kind; no null/empty alternative |
| <a id="field-mqtt-adapter"></a>`adapter` | String `mqtt` | Selects the existing typed MQTT adapter and owned service role; no arbitrary adapter or Compose override |
| <a id="field-mqtt-display-name"></a>`display_name` | String `MQTT` | Default descriptive label; explicit site `display_name` replaces it without renaming persistent identity |
| <a id="field-mqtt-interfaces"></a><a id="field-mqtt-interfaces-backend"></a><a id="field-mqtt-interfaces-backend-required"></a><a id="field-mqtt-interfaces-backend-accepts"></a><a id="field-mqtt-interfaces-frontend"></a><a id="field-mqtt-interfaces-frontend-required"></a><a id="field-mqtt-interfaces-frontend-accepts"></a>`interfaces.backend`, `.frontend` | [Named role mappings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types) | Both required; each `.required` is boolean `true`, `.accepts` is the sequence `[guest-interface]`; each site role [binds a guest NIC](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/apps.md#interface-roles) with `{interface: NIC_ID}` in the selected guest |
| <a id="field-mqtt-listeners"></a><a id="field-mqtt-listeners-mqtt"></a><a id="field-mqtt-listeners-mqtt-service"></a><a id="field-mqtt-listeners-mqtt-namespace"></a><a id="field-mqtt-listeners-mqtt-interface"></a><a id="field-mqtt-listeners-mqtt-bind"></a><a id="field-mqtt-listeners-mqtt-protocol"></a><a id="field-mqtt-listeners-mqtt-port"></a>`listeners.mqtt` | [Named listener mapping](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types) | `.service: mqtt`, `.namespace: host`, `.interface: backend`, `.bind: wildcard`, `.protocol: tcp`, `.port: 1883`; generated container uses host networking and the actual socket is host TCP 1883 |
| <a id="field-mqtt-endpoints"></a><a id="field-mqtt-endpoints-backend"></a><a id="field-mqtt-endpoints-backend-listener"></a><a id="field-mqtt-endpoints-backend-protocol"></a><a id="field-mqtt-endpoints-backend-via"></a><a id="field-mqtt-endpoints-frontend"></a><a id="field-mqtt-endpoints-frontend-listener"></a><a id="field-mqtt-endpoints-frontend-protocol"></a><a id="field-mqtt-endpoints-frontend-via"></a>`endpoints.backend`, `.frontend` | [Named endpoint mappings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#profile-interface-listener-and-endpoint-types) | Each `.listener: mqtt`, `.protocol: tcp`; `.via` is the matching role name. Endpoint address comes from that role's bound NIC, port from the one listener; these are two advertisements of one listener |
| <a id="field-mqtt-storage"></a><a id="field-mqtt-storage-config"></a><a id="field-mqtt-storage-config-target"></a><a id="field-mqtt-storage-config-required"></a><a id="field-mqtt-storage-config-kind"></a><a id="field-mqtt-storage-config-read-only"></a><a id="field-mqtt-storage-data"></a><a id="field-mqtt-storage-data-target"></a><a id="field-mqtt-storage-data-required"></a><a id="field-mqtt-storage-data-kind"></a><a id="field-mqtt-storage-data-read-only"></a><a id="field-mqtt-storage-log"></a><a id="field-mqtt-storage-log-target"></a><a id="field-mqtt-storage-log-required"></a><a id="field-mqtt-storage-log-kind"></a><a id="field-mqtt-storage-log-read-only"></a>`storage.config`, `.data`, `.log` | [Named storage requirement mappings](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#profile-storage-roles) | `.required: true`, `.kind: directory`, `.read_only: false`; `.target` is `/mosquitto/config`, `/mosquitto/data`, `/mosquitto/log` respectively. Site must [bind all three](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md#app-storage-bindings); no default source path or fresh initializer is declared |
| <a id="field-mqtt-connections"></a>`connections` | Empty mapping `{}` | No consumer connection role. Other apps can target its endpoints through their own supported connection roles; the broker does not gain an upstream by implication |
| <a id="field-mqtt-software"></a>`software` | [Software IDs](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#software): `docker`, `curl`, `mqtt-images` | Named library selections; `mqtt-images` maps image role `mqtt` to authoritative catalogue ID `mqtt` |
| <a id="field-mqtt-runtime"></a>`runtime` | [Runtime-profile IDs](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#runtime-and-allocations): `container-host`, `mqtt` | Named runtime requirements; selected MQTT service reserves/limits 256 MiB memory, CPU limit 1 and PID limit 128 in this snapshot |
| <a id="field-mqtt-health"></a><a id="field-mqtt-health-ready"></a><a id="field-mqtt-health-ready-profile"></a>`health.ready.profile` | [Health-profile reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#health-and-monitoring) `adapter-ready` | Selects adapter health checks, including authenticated retained probe acceptance and anonymous refusal; defining the check is not evidence it ran on a target |
| <a id="field-mqtt-monitoring"></a><a id="field-mqtt-monitoring-profile"></a>`monitoring.profile` | [Monitoring-profile reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/supporting-types.md#health-and-monitoring) `docker-agent` | Selected library monitoring policy; not a private server allocation |
| <a id="field-mqtt-secrets"></a><a id="field-mqtt-secrets-probe"></a><a id="field-mqtt-secrets-probe-required"></a>`secrets.probe.required` | Boolean `false` metadata | Current adapter still requires a file binding; see [probe details](#mqtt-probe) and [missing-probe diagnostic](#mqtt-diagnostics) |

Both roles can bind the same guest NIC, as in the example. Neither role creates a NIC, and neither endpoint grants traffic or adds a readiness wait. A wildcard host listener may listen beyond the advertised NICs. Binding `backend` and `frontend` to different NICs does not create separate isolated sockets. A second overlapping host TCP 1883 broker on the same guest conflicts; distinct guest placement avoids that specific socket collision but still requires independent data/identity/credential ownership. See [interface composition](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/multiple-interfaces.md) and [placement limits](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/shared-and-separate-guests.md).

Storage bindings select an explicit supported guest volume or root path with an optional confined subpath. They resolve under the selected guest, not an arbitrary controller path. Retained data is verified rather than silently chowned or relocated. The adapter mounts these sources at the three declared container targets. This profile declares no directory initializer, broker configuration/ACL generator or general credential bootstrap. Use the compatible [storage reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/storage.md) for binding alternatives and path constraints, and [installation limits](#mqtt-lifecycle) before operating.

Named software/runtime/health references resolve in the library index. The selected image uses an immutable registry digest in [images.json](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/images.json). Exact package versions and shared security/process defaults belong to [software/runtime declarations](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/reference/software-and-runtime.md). Budgets are admission policy rather than measured service capacity; effective guest reserve and all app requirements must fit.

No device role, inbound HTTP route, OAuth client or broker consumer-connection role is declared. These topics are inapplicable to this profile's selected definition; the [Explorer page](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/reference/apps/mqtt_explorer.md) owns its gateway/outpost/workspace requirements.

<a id="mqtt-probe"></a>
### 12.3 `apps.<id>.secrets.probe`

**Type and reference:** a site identifier string selecting `secret_sources.<name>` in the same complete site. For this adapter the selected source MUST be `{type: file, path: ABSOLUTE_PATH}`; file path syntax is defined by the compatible [secret-source contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/identity-and-secrets.md). The source is controller metadata. Resolving it does not read its file or create an account.

**Presence/default:** required by the selected MQTT adapter even though profile metadata marks the role optional. No source/default credential is inserted. Omission reaches `component.secret-required`; a valid environment source also fails this file-only floor. A null/empty identifier is not an omission alternative and does not satisfy reference/type rules. The [diagnostic example](#mqtt-diagnostics) demonstrates omission from an otherwise valid source.

**Material and output:** the runtime parser accepts one existing JSON probe record with exactly `username` and `password`, both nonempty strings of at most 65,535 UTF-8 bytes without CR/LF/NUL. It prepares private `mqtt-probe.json` owned by UID/GID 0 with mode 0600 under the app's selected runtime directory. No actual values belong in public documentation or source. See [probe parser](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/mqtt_runtime.py) and [binding floor](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_foundations.py).

**Lifecycle:** supply a genuinely existing probe account and prepared broker that accepts it. This record is distinct from application/GUI/identity credentials. Ordinary private-material continuity rules apply; changing a source name or path does not authorize rotation. Source compilation neither checks credential contents nor proves broker acceptance. The adapter's health definition checks authenticated acceptance and anonymous refusal after actual deployment; this specimen has not performed that target check.

<a id="mqtt-password-file"></a>
### 12.4 `apps.<id>.properties.password_file`

**Purpose:** names the existing Mosquitto password file for the separately selected managed MQTT-account capability. It does not create `mosquitto.conf`, an ACL or arbitrary broker accounts. A plain broker with an existing explicit credential consumer can omit it, as in the [canonical composition](#mqtt-example).

**Type and constraint:** optional string matching `/mosquitto/config/[A-Za-z0-9_.-]{1,100}`; the basename cannot be `.` or `..`. This is a path inside the declared config mount, not a secret-source ID or controller path. Absolute paths elsewhere, nested subdirectories, null and the empty string fail `component.property`. No units, enum or nested object apply.

**Conditional requirement:** when a supported MQTT Explorer connection selects a managed account on this broker, the resolver requires this property and supplies it to that account path; absence then fails `component.broker-binding`. An Explorer connection using an explicit existing credential is a different mode and does not create that managed account. See the compatible [connection/account rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_foundations.py) and [Explorer's choice](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/reference/apps/mqtt_explorer.md).

**Default/resolution:** no default is declared in this profile; omission leaves it absent. The resolver copies direct profile property keys then replaces them with explicit site property keys. This field is scalar, so no recursive merge applies. The MQTT property object is closed: `password_file` is its only accepted key at this snapshot. `port: 1884` is not an available override and fails `component.fields`.

**Conditional syntax fragment**, to be placed in an otherwise valid broker instance whose separately declared managed-account composition requires it:

```yaml
properties:
  password_file: /mosquitto/config/passwords
```

This fragment passes the property's value rule; it does not by itself select or prove the account operation. That operation uses the supported parent-mounted password-file/HUP path and its continuity checks. HUP is a broker reload interaction; it is not a promise that every broker update avoids a restart. See [lifecycle](#mqtt-lifecycle) and [invalid property diagnostics](#mqtt-diagnostics).

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

`primary` resolves to guest `broker`'s NIC at synthetic `198.18.20.90`. Both advertised broker endpoints therefore resolve to that address on TCP 1883; the actual listener remains wildcard in the host namespace. Guest root path `data` is `/srv/example/broker`, so the three subpaths resolve below that base. `project: broker` selects the guest's declared Compose project, rather than inventing a new project during a retained update. Explicit retained identities must match genuine installed ownership at deployment.

The complete composition also illustrates independently selected Explorer, ingress, telemetry and radio profiles. Its existing external broker credential mode does not imply that those consumers are connected to this `broker` app merely because it exists in the same source. The actual `connections` targets determine that relationship. To understand how a managed producer endpoint changes the requirements, follow [connection composition](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/connect-apps.md) and the [password-file conditional record](#mqtt-password-file).

For reproducible source-only validation, use the [fully defined isolated setup](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/guides/first-configuration.md), which defines `STACK`, `FRAMEWORK` and `PYTHON` at the selected compatible revisions. In that shell:

```sh
"$PYTHON" "$FRAMEWORK/blueprints/compile.py" \
  --stack "$STACK" --site "$STACK/examples/catalogue/messaging-radio.yaml" --check
```

Expected: the complete site resolves. The maintained [profile integration](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/tests/test_profile_examples.py) additionally calls the real packet lowerer for every selected guest, with subprocess execution and socket connection patched to fail. A focused check of this exact source/dependency tuple resolved five apps and lowered five guest packets; its invalid cases below were also exercised. No private file contents, infrastructure, container or service was contacted. The synthetic composition deliberately is not ready for deployment admission.

<a id="mqtt-lifecycle"></a>
### 12.6 First installation

This profile supplies no general Mosquitto configuration, ACL, password bootstrap or directory initializer. A valid prepared configuration/data/log tree and an existing file-backed probe account are prerequisites. The worked composition uses an already HomeLab-managed broker with `retained`; it is an offline usage example, not a fresh broker commissioning or import procedure. Structural acceptance of `fresh` does not establish a complete new-broker onboarding workflow. Do not infer such a guarantee from the profile or from compilation.

### 12.7 Later deployments

Ordinary owned deployments reconcile the selected broker container/configuration and bind its existing probe material. Both lifecycle policies allow supported updates after genuine ownership exists; an instance created through a supported `fresh` path keeps that policy. `retained` cannot create an absent owner or adopt a manually installed broker.

| Change / condition | Supported behavior and limit |
| --- | --- |
| Descriptive display label | Changes the label; does not rename broker/project/service/data identity |
| Compatible selected software/configuration | Reconciles owned service configuration subject to admission and health guards; service/container restart or interruption may occur; no universal zero-downtime claim |
| Explicit managed-account selection | Uses the separate guarded password-file/HUP path; parent config mount and account/material ownership apply; does not recreate unrelated clients by implication |
| Host port or listener isolation | No `port` property exists for this adapter; changing endpoint advertisement is not isolation and does not relocate the socket |
| Service/project/runtime/data identity move | No automatic relocation/adoption guarantee; preserve installed identities and use the existing qualified boundary for a refusal |
| Probe material removal/change | Ordinary continuity checks refuse implicit private-material removal/rotation; renaming the source is not a rotation procedure |
| App removal / foreign existing service / HOLD | No automatic cleanup, foreign adoption or HOLD release is supplied by profile selection |

The framework's [lifecycle contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md) and [support boundary](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/support.md) own continuity and refusal details. Actual commissioning, interruption duration and service behavior have not been qualified by this specimen's source checks. After authorized protected CD, verify the selected broker endpoint, retained authentication, anonymous refusal and affected integration at the consuming site; preserve evidence on failure. The [library troubleshooting guide](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/docs/troubleshooting.md) is the next diagnostic route.

<a id="mqtt-diagnostics"></a>
### 12.8 Invalid cases and actionable diagnostics

Each mutation below starts from the otherwise valid complete messaging composition and changes only the stated input. These are deliberately invalid examples, not additional accepted syntax.

| Mutation | Observed source refusal at the selected tuple | Cause and correction |
| --- | --- | --- |
| Remove `apps.broker.secrets.probe` | `component.secret-required at apps.broker.properties` | Current adapter requires the file-backed existing probe. Restore the [probe binding](#mqtt-probe); this adapter emits the broader properties context even though the missing input is under secrets |
| Set `properties.password_file: /tmp/passwords` | `component.property at apps.broker.properties` | Path is outside the accepted mounted config leaf. Use the exact [password-file pattern](#mqtt-password-file) for the real prepared broker path; do not invent a different existing file |
| Set `properties.password_file: null` or `''` | `component.property at apps.broker.properties` | Null/empty is not an absent/default value. Omit it only when the managed-account mode does not require it, otherwise provide the accepted path |
| Set `properties.port: 1884` | `component.fields at apps.broker.properties` | Closed MQTT property object has no port override. Choose valid placement or pursue a separately reviewed adapter capability |

After correction, rerun the real source resolver/lowerer with the complete composition. These failures were exercised before any native process or connection could run. They do not prove private material is correct, broker authentication works, or deployment continuity will pass.

## 13. Worked specimen: Docker guest template

This second specimen demonstrates a reusable-default reference rather than another app page. It uses the same checked library/framework tuple as [MQTT](#12-worked-specimen-mqtt-profile). The canonical definition is [templates/docker.yaml](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/templates/docker.yaml); registration and named policies are in [stack.json](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/stack.json). General shape/bounds are owned by the compatible [guest reference](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/guests.md) and [structural types](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_types.py).

### 13.1 Purpose and complete syntax

Choose `guests.<id>.template: docker` for these guest defaults and named Docker/runtime selections. It does not choose any app, VMID, hostname, NIC, address, provider storage, lifecycle, account or credential. A site still supplies its complete guest declaration. The `base` template is an alternative with root size 4 GiB, boot order 20 and no template-level software/runtime selection; this `docker` template uses root size 8 GiB and boot order 50.

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

These are declared template values, applied by the real resolver. `resources`, `startup` and `security` are complete mappings in the template. The site's corresponding block is partial; each explicit direct field replaces that template field. There is no arbitrary recursive source overlay. Unknown fields are rejected by the closed owning type. Null is not an inheritance marker.

| Path | Type / accepted rule | Template value | Omission or override behavior |
| --- | --- | --- | --- |
| <a id="field-docker-schema"></a><a id="field-docker-kind"></a>`schema`, `kind` | Fixed strings `homelab-components-v1`, `guest-template` | As shown | Required complete-definition markers; no null/empty alternative |
| <a id="field-docker-resources"></a>`resources` | Complete typed mapping in template; partial mapping in guest | Four values below | Guest omission or empty partial mapping inherits all direct defaults; null refuses |
| <a id="field-docker-resources-cpu-cores"></a>`resources.cpu_cores` | Integer 1..2147483647 | 1 | Guest omission inherits 1; explicit direct integer replaces it |
| <a id="field-docker-resources-memory-mib"></a>`resources.memory_mib` | Integer 256..2147483647 MiB | 1024 | Guest omission inherits 1024; must leave room for effective reserve and selected runtime/app reservations |
| <a id="field-docker-resources-root-gib"></a>`resources.root_gib` | Integer 4..2147483647 GiB | 8 | Guest omission inherits 8; the existing-guest ordinary plan guard treats the entire disk block as immutable, so both growth and shrink changes are refused |
| <a id="field-docker-resources-os-reserve-mib"></a>`resources.os_reserve_mib` | Integer 0..2147483647 MiB; resolved value less than memory | 256 | Guest omission inherits 256; effective runtime reserve has at least a 256 MiB floor and may be raised by selected requirements |
| <a id="field-docker-startup"></a>`startup` | Complete typed mapping in template; partial mapping in guest | Three values below | Direct-key override; empty guest mapping inherits; null refuses |
| <a id="field-docker-startup-started"></a>`startup.started` | Boolean | `true` | Guest omission inherits; false is structurally accepted and resolves, but the saved-plan guard requires the planned guest active and refuses false; null/empty/number is not a boolean |
| <a id="field-docker-startup-start-on-boot"></a>`startup.start_on_boot` | Boolean | `true` | Guest omission inherits; explicit boolean replaces |
| <a id="field-docker-startup-boot-order"></a>`startup.boot_order` | Integer 0..2147483647 | 50 | Guest omission inherits 50; not 20 for this template |
| <a id="field-docker-security"></a>`security` | Complete typed mapping in template; partial mapping in guest | Four values below | Direct-key override subject to true-only constraints; empty guest mapping inherits; null refuses |
| <a id="field-docker-security-unprivileged"></a>`security.unprivileged` | Boolean, required `true` | `true` | False is rejected by the owning structural security rule |
| <a id="field-docker-security-protection"></a>`security.protection` | Boolean, required `true` | `true` | False is rejected; a template is not permission to disable protection |
| <a id="field-docker-security-nesting"></a>`security.nesting` | Boolean | `true` | Guest omission inherits; the selected `container-host` runtime requires true, so a structurally valid false override refuses `component.runtime-requirement` |
| <a id="field-docker-security-keyctl"></a>`security.keyctl` | Boolean | `false` | Guest omission inherits; the runtime's false requirement is non-demanding and does not itself force the guest value to false |
| <a id="field-docker-software"></a>`software` | Sequence of named software IDs | `[docker]` | Resolver appends guest software to template software; names resolve in library software declarations; app selections also contribute their requirements |
| <a id="field-docker-runtime"></a>`runtime` | Sequence of named runtime-profile IDs | `[container-host]` | Resolver appends guest runtime to template runtime; selected requirements and compatibility are resolved, not inferred from the name |
| <a id="field-docker-monitoring"></a>`monitoring` | Named monitoring reference mapping | `{profile: linux-agent}` | Guest selection replaces this mapping; omission inherits; empty/null is not a disable operation |
| <a id="field-docker-monitoring-profile"></a>`monitoring.profile` | Named monitoring-profile reference | `linux-agent` | Guest monitoring selection replaces the template monitoring selection; nested profile semantics belong to the named monitoring contract |

The integer validator requires actual integers, so YAML booleans do not count as CPU/memory/size values. A guest's omitted resources block or empty partial mapping inherits all template fields; a present null block is not accepted. An empty guest software/runtime list contributes no additions; it does not erase the template selections. A null list is not an empty list. Monitoring omission inherits; an empty/null mapping does not mean “disable monitoring.” See [effective resolver rules](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_plan.py), [monitoring type](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/blueprints/component_monitoring.py) and the downstream [saved-plan guard](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/proxmox/applications/plan_policy.py). Structural acceptance and a resolved packet do not bypass these selected-runtime and execution floors.

### 13.3 Partial override and complete context

This is a **guest fragment**, to replace only the template/resource selection in a complete guest:

```yaml
template: docker
resources:
  memory_mib: 3072
```

The [standalone resolver composition](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/site.example.yaml) and its [guest declaration](https://github.com/theaussiepom/homelab-stack/blob/a1ed87bbb7b1d41434a0f60bf3ff4c06a9fd2c8d/examples/minimal/guests/resolver.yaml) supply the complete context. A focused check loaded that complete source, selected `docker`, replaced its guest resources with `{memory_mib: 3072}`, then resolved and lowered it with the selected real framework. Effective resources were CPU 1, memory 3072 MiB, root 8 GiB, reserve 256 MiB; startup remained `started:true`, `start_on_boot:true`, `boot_order:50`. This checks actual direct-field inheritance, not a copied table. It does not create a Docker host or demonstrate installed resource resizing.

Useful invalid variations are `memory_mib: 255` (below the structural minimum) and `security.protection: false` (violates the true-only rule). An `os_reserve_mib` equal to guest memory passes an individual nonnegative-integer check but fails the resolved reserve-less-than-memory condition. These rules come from the linked actual validator/resolver; this specimen's execution evidence covers the valid partial override, not a new execution of every negative branch. Existing direct component tests are the proper evidence boundary for the scalar rules.

### 13.4 First installation and later deployments

A template is a source-default value, so it has no independent installation, credential material or service health procedure. Its consuming guest/app must use a supported creation path and the actual [lifecycle/support contract](https://github.com/theaussiepom/homelab/blob/52913d4ba03f85e7d734a85b08c93e73f320455d/docs/reference/lifecycle.md). Selecting `docker` does not prove absence of an existing backend or authorize adoption.

For later deployments, template changes affect guests that inherit the changed field; an explicit guest field remains authoritative for that field. CPU/memory/startup changes alter desired infrastructure and may affect running state or reachability according to the actual supported provider path. The saved-plan guard requires an active planned guest and refuses changes to the existing disk block, including root growth as well as shrink; a syntactically valid value or provider-proposed operation is not deployment permission. Persistent identity/path moves, protection removal and arbitrary replacement are not supported by describing different defaults. Compare resolved output before adopting a library change and follow the consuming guest's actual operation/qualification limits.

## 14. Design rationale and source use

These are selected documentation techniques, not a claim that the current suite matches every source or that another system's behavior applies to HomeLab.

| Primary pattern | Adopted rule and HomeLab-specific judgement |
| --- | --- |
| [Compose specification](https://github.com/compose-spec/compose-spec/blob/main/spec.md), [services](https://github.com/compose-spec/compose-spec/blob/main/05-services.md) and [Docker reference](https://docs.docker.com/reference/compose-file/) | Use readable YAML, directly anchored attributes, linked object definitions and coherent compositions. Preserve explicit ownership/reference effects; do not inherit Compose's broad optional-implementation or ignored-attribute behavior into HomeLab's closed contracts. Source and implementation references can differ; record which is authoritative. |
| Compose [networks](https://github.com/compose-spec/compose-spec/blob/main/06-networks.md), [volumes](https://github.com/compose-spec/compose-spec/blob/main/07-volumes.md), [configs](https://github.com/compose-spec/compose-spec/blob/main/08-configs.md), [secrets](https://github.com/compose-spec/compose-spec/blob/main/09-secrets.md) and [workload dependencies](https://github.com/compose-spec/compose-spec/blob/main/workload_spec.md#depends_on) | Link declaration to consumer and back; distinguish references, access, external lifecycle and explicit dependency conditions. Use short/long-form comparisons only where HomeLab actually accepts alternatives; do not add Compose syntax to a HomeLab example. |
| Terraform AWS [resource reference](https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/r/instance.html.markdown) and [provider reference](https://github.com/hashicorp/terraform-provider-aws/blob/main/website/docs/index.html.markdown) | Distinguish input arguments from outputs, document interactions/default precedence and concrete stop/start/recreation behavior. Do not import Terraform's operation/import capabilities as HomeLab guarantees. |
| Terraform [author guidance](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/end-user-documentation.md) and [Registry documentation](https://developer.hashicorp.com/terraform/registry/providers/docs) | Require complete argument/attribute coverage, linked nested blocks, functional self-contained examples and version-linked documentation; generate reliable structure while authoring behavior. Registry-specific macros/front matter and sentence rules are not requirements for GitHub Markdown. |
| AWS CloudFormation and Azure resource-reference patterns | Predictable syntax/property/effect records and explicit compatibility/change references, adapted to library profiles rather than a cloud resource catalogue. |
| Kubernetes API/concept/task patterns | Field-to-type-to-concept/task navigation and return paths, with manifest/prerequisite/result coherence; separate declarative intent from observed service state. |
| Stripe operation/flow patterns | Explain concrete configuration effects in readable language and link the next operation/context at the point of use; accepted/compiled input is distinct from completed installation/service outcome. |
| OpenAPI named-object/reference patterns and GitHub REST concept/guide/reference patterns | Named nested types and stable contextual references with examples and prerequisites; formal tables alone do not teach newcomers. Plain committed Markdown must work without another site's unresolved macros. |

The practical target is a predictable, complete and navigable library reference combined with useful learning and operating paths. Compliance is established by the [inventory and review evidence](#10-verification-and-review-rubric), not by resemblance to a vendor's page layout.
