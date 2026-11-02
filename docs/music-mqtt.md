# Music Assistant and the dedicated broker

The stack now gives Music Assistant and MQTT their own guest jobs. These source
profiles do not establish native readiness. The private site supplies actual
addresses, network identities, trusted keys and genuine prerequisite acceptance.
The public examples propose guest207 for Music and guest217 for MQTT. VLAN41 is a
candidate dedicated MQTT client network; it must be collision-checked and routed
through the existing network owner before private adoption.

## Music Assistant

Music Assistant uses the upstream `ghcr.io/music-assistant/server:latest` image,
following the selected floating-image policy. Record its resolved image/version
at deployment. Its private application tree is staged separately at
`/srv/homelab/data/music-assistant/data`, preserving existing providers, identity,
library, SQLite state and credentials. Ordinary CD never restores this state or
bootstraps accounts.

The application uses host networking in its unprivileged Docker-capable guest.
Its selected Home interface supplies the bind/publish address; management and
backend identities remain separate. No SYS_ADMIN, DAC_READ_SEARCH, unconfined
AppArmor or filesystem-provider mount privilege is inherited from the old Docker
host. No NAS library provider or share is invented. The existing finite reply
routing helper preserves the selected Home source on routed replies.

The pre-start helper verifies the prepared settings and retained database inputs;
it does not rewrite them. Normal health first checks `/info` on8095 and the
stream8097 listener, then checks the published HTTPS `/info` route through the
selected ingress address. The route check requires a valid browser certificate
and the `server_version` response field. It binds the already allowed Home
interface as its client source, preserving the existing allowlist. Actual enabled provider/library access, discovery,
player callbacks and playback remain native acceptance after authorised rollout.
Public rules declare the existing Home discovery and scoped ingress/HA paths;
they do not prove physical multicast or deployed firewall enforcement.

The browser route additionally selects the native `music-clients` IP allowlist.
Public defaults allow the example Home LAN and VPN only. The private site replaces
its complete `ipAllowList.sourceRange` with the approved finite LAN/VPN ranges and
individual tablet `/32` entries. This does not admit an entire IoT subnet or
arbitrary routed/Internet clients. It uses the existing middleware contract,
without a plugin, second bypass router or new rule/priority grammar. The filter
does not add an Authentik login; application identity and authentication remain
with the retained Music Assistant data.

## MQTT

The single broker publication moves from `automation.mqtt` to `mqtt.mqtt`, keeping
`broker.mqtt` as its canonical hostname. Backend clients use the broker's declared
backend address; external clients use its dedicated client VLAN address. DNS,
container aliases and required connection metadata derive from this owner.
Home Automation retains HA and Node-RED only. Radios has a real broker dependency
and no artificial Home Automation startup barrier.

The broker image is the same selected Mosquitto digest. Its original config,
password file, persisted messages, durable sessions and log/data paths are staged
separately, preserving ownership and existing credentials. A source-bound private
probe JSON carries one existing account for authenticated CONNECT and anonymous
refusal; no account is created or rotated. The broker receives no HTTP frontend.

Cutover must stop and retire only the old managed broker writer, copy a coherent
retained broker generation, update every actual client/DNS binding and admit the
new role before CD. The framework refuses a retained old MQTT container under a
broker-free Automation profile; it never deletes the container or its data
implicitly. Two active brokers with independent retained/session state are not a
migration strategy. Automation's existing NIC order and addresses are preserved
in this stream; stale hardcoded clients must be explicitly found and corrected,
not hidden behind a new proxy, NAT rule or duplicate broker.

The declared client allowances preserve existing Home/IoT MQTT clients and exact
Pi peers while the backend admits only the selected Automation and Radios peers.
Source firewall checks model required flows. This stack does not change cluster
firewall enablement or establish live filtering. Router/VLAN changes and actual
connectivity belong to the reviewed private adoption, not the public example.
