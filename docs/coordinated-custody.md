# Completed commissioning groups and ordinary deployment

A private site may select exact completed-group custody as provenance for ordinary
per-guest maintenance. Initial scope is the MariaDB singleton and the PostgreSQL,
Identity and db-tools group. Public profiles select no historical group. Actual
record paths, group and receipt hashes, trust bindings and backend anchors belong
in the reviewed private overlay; public examples and tests use invented evidence.
Completion alone is insufficient. With no exact selection, coordinated membership
retains its existing refusal.

The optional guest configuration field `coordinated_custody` must bind the exact
closed contract of the selected published framework. It identifies the complete
immutable group proof and each member's qualified starting generation. Every
configured member carries the identical complete selection, including members
excluded from this run. The compiler rejects missing or conflicting copies,
wrong roles or VMIDs, overlap and unrelated groups before packet admission.
This selection is provenance, not a readiness or exclusive-writer acceptance.

## Private proof inputs

The selected [framework contract](https://github.com/theaussiepom/homelab/blob/84cfff2e5a5c2bc664c1277f5508d42d3a2df1ba/docs/coordinated-custody.md)
defines the closed `homelab-coordinated-custody-v1` selection. Supply it under
`guests.<member>.config.coordinated_custody`, and set that member's
`config.paths.coordinated_custody_inputs` to `${inputs}`. The compiler binds this
to the exact guest packet directory; all members still carry the same selection.

The four public profiles provide these immutable text-file slots:

| Packet file | Private central value |
| --- | --- |
| `custody-catalogue.json` | `custody.catalogue`, shared by all four members |
| `custody-acceptance.json` in PostgreSQL, Identity and db-tools | `custody.postgresql_acceptance` |
| `custody-acceptance.json` in MariaDB | `custody.mariadb_acceptance` |

Set the group's `catalogue.file` and `acceptance.file` to those exact filenames.
Their `sha256` fields must hash the complete raw UTF-8 bytes of the corresponding
central value, including whitespace and final newlines. The selected proof bytes
are never interpolated: even literal `${inputs}` and central-value tokens stay
unchanged. Ordinary runtime configuration retains its existing substitution.
Do not reconstruct or normalize retained JSON to make a digest match.

Public values default to inert `{}` text and public profiles select no group.
Those defaults neither represent retained evidence nor grant admission. The private
site must override them with the exact retained catalogue and each group's
acceptance proof, supply every member/record/anchor binding required by the closed
schema, and retain all prerequisite gates. The public overlay example remains
empty. Tests construct invented selections solely to check source compilation;
they do not qualify a NAS mount, retained state or real commissioning record.

## Configured provenance and enabled guests

All eleven guests remain configured and `disabled: []` enables all of them. The
existing guest dependency graph decides which exclusions are valid. Custody does
not enable an excluded guest or turn the historical group into an atomic job.

| Disabled guests | Existing selection result |
| --- | --- |
| None | All eleven enabled |
| db-tools | Valid leaf exclusion; PostgreSQL and Identity remain enabled |
| Identity alone, or Identity with db-tools | Invalid: Automation still needs Identity |
| Identity with Automation, leaving db-tools or Zigbee2MQTT active | Invalid: an active consumer lacks its prerequisite |
| Identity, db-tools, Automation and Zigbee2MQTT | Valid; the other seven guests retain their normal execution |
| PegaProx or Bitwarden alone | Valid unrelated leaf exclusion |
| DNS with consumers active | Invalid prerequisite exclusion |

An excluded group member still contributes its configured immutable provenance.
Removing its copy or required proof is not permitted. Its disabled packet does not
enter runtime admission or contact its target. Enabled members verify the full
immutable group proof, while each member's mutable backend generation is checked
under that member's existing locks when it runs. The independent DAG does not
promise simultaneous peer-state equality or execution of every group member.

## State progression and refusal

Admission retains the original requests, claims, completions, overlays and
installation/source/input/trust records. Local and NAS proof must agree under the
existing recovery identity and path rules. Ordinary deployment does not create
missing proof, copy or rename a historical receipt, replay commissioning, or clear
a hold to obtain admission.

The first run requires the exact qualified starting backend generation and the
selected absent-or-exact starting ordinary receipt. A selected older four-field
receipt is recognized only by its exact raw digest and matching immutable
operation copy; it is initial provenance, never a current-framework success.
Identity and db-tools can start from their separately qualified later ordinary-CD
generation instead of being forced back to an older overlay state.

After successful infrastructure, the same run uses its exact owned hold and
immutable infrastructure receipt. Later runs use a successful current-framework
ordinary receipt whose canonical bytes match its immutable operation copy and
whose state hash matches the current backend. Lineage and closed resource identity
remain required. Existing workflow sequence, source ancestry, binding, phase
ordering and no-replay checks continue to apply. Successful receipts may advance
the complete state hash and serial without repinning an old overlay.

A present failure, pending or foreign marker, malformed receipt, unfinished
operation, changed proof or unexplained backend generation refuses admission.
It never falls back to an older anchor. Admission neither clears markers nor
repairs custody; normal successful phase receipts remain the only ordinary state
progression. Immutable proof participates in normal drift checks; mutable backend
state, holds and latest-receipt pointers are not immutable inputs.

## Private adoption remains separate

Before native adoption, retire or drain the old cooperating writer and service
verifier entrypoints through the existing global queue, and separately review the
owner/window for manual or noncooperating writers. The existing database shared
lock and per-member exclusive locks do not exclude an old shared-lock service
verifier for a whole phase. An idle sample is not an ownership reservation.

This source contract introduces no migration executor, handoff write, global
serialization or readiness/writer flag. A source pin, synthetic tests and passing
CI do not authorize a main merge, deployment, native mutation, hold release or
application acceptance. Keep all existing prerequisite and failure custody checks.
