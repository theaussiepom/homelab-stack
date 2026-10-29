# Adopt after current Automation work

This is a local source implementation, not a native rollout. Finish the existing
HA/Automation owner's deployment first. These worktrees do not supersede that work
or qualify stopped Proxmox guests.

Before publishing, review the public-source policy and scan the complete public
history. Then separately authorize publication, run hosted CI and qualify the
selected framework/stack on the admitted runner. Test graph display, nested
workflow access and secret inheritance there; local YAML checks cannot prove them.

Before private adoption, compare the finished live desired state with these profiles.
Carry current actual settings privately; do not revive old shared PostgreSQL
backend assignments. Compare VMIDs, NIC MACs, addresses, disks, storage/template
identities, UID/GID/modes, CA/SSH trust, backend state and all holds. DNS needs an
explicit existing-state adoption because its complete commissioned infrastructure
input was not in the private source seed. Its public profile is a proposal.

Keep the state root and backend identities. Do not import, recreate or rename an
installed guest through ordinary CD. Every admitted runner must see the same durable
state and private inputs; jobs may move between admitted slots. The parent retains
the existing global deployment concurrency group and does not cancel running work.

Update the private site's sole literal stack workflow SHA through a reviewed change.
Accept exact prerequisites only after separate data/configuration preparation and
writer fencing. All declared guests participate by default. An optional `disabled`
list can exclude named guests while preserving dependencies of active consumers. A failed
or interrupted run preserves its hold and evidence and requires exact continuation
review; rerunning jobs is not a recovery procedure. No automatic rollback exists.

Local tests prove source behavior and synthetic custody only. Native PVE plans,
Debian packages, NAS mount/backup behavior, Docker health, real logins, physical
devices, DNS connectivity, firewall enforcement and no-op behavior in the target
environment require future qualification. No deployment is authorized by this guide.
