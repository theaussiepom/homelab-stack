# MQTT Explorer

`mqtt_explorer` and `mqtt` are independently selected app profiles. A site can
place them together or bind Explorer to a supported external broker. They are not
a fixed guest bundle. Selected same-guest dependencies order app steps inside one
guest job; no identity/ingress readiness is inferred from login or hostname data.

Explorer uses the official image in `images.json`, UID/GID 1001 and a private
app network with no direct host port. Its file-only Traefik gateway publishes the
selected web endpoint. Every app and Socket.IO request passes through the named
existing Authentik outpost; callbacks go to the outpost separately. The sidecar
has no ACME, API/dashboard, Docker socket or infrastructure provider. It does not
create an identity provider or change its policy.

The GUI's canonical HTTPS exposure and native broker DNS exposure are separate.
A broker connection can retain its saved hostname while targeting the selected
backend. The compiler derives one closed Explorer-only runtime alias from that
endpoint; it does not change managed DNS, broker listeners or the gateway's alias
map. Connection declarations do not grant network access.

## Saved account and profile

An explicit same-guest managed account selects dedicated `read-write-all` access:
it can read and publish every broker topic. Independent placement uses a supported
explicit existing credential; it never silently creates an account on another
guest. The broker probe, existing clients and identity-provider credentials remain
separate inputs. The broker's selected password-file capability is explicit;
no ACL or new authentication mechanism is inferred.

Ordinary input preparation creates or reuses the protected managed credential
record. Account collision or drift refuses instead of rotating or adopting it.
The existing guarded broker account lifecycle validates the parent-mounted
password file before atomic addition and HUP. App changes target their own
services; updating the GUI does not implicitly recreate a peer broker.

The native version1 saved profile contains the password in plaintext at rest.
It stays in the explicitly bound private workspace under umask 077; existing
profiles and unrelated settings remain. No password enters Git or application
environment variables. The generated startup boundary suppresses secret-bearing
upstream console output while retaining fixed error signals. No fixed client ID,
autoconnect, public demo broker or AI key is selected.

Local readiness checks the app, loaded gateway and exact backend alias without
requiring IdP availability. Actual sign-in, saved-account read/publish behavior
and existing-client continuity are acceptance checks after authorized deployment.
Resource declarations are placement policy, not a load-capacity guarantee.
