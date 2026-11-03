# MQTT Explorer

The MQTT guest runs the existing Mosquitto broker, then **MQTT Explorer**, in one
guest job. Broker clients, its internal DNS publication, retained data and probe
account are unchanged. The guest still depends only on DNS. The GUI phase adds no
identity or ingress startup dependency, and existing fail-stop behavior remains.

The browser application uses the official upstream image selected in
`images.json`. It runs as UID/GID1001 on a private Compose network with no host
port. The existing pinned Traefik image supplies a separate file-only gateway on
the selected backend address, port80. The outer ingress route supplies browser
HTTPS. Every application and Socket.IO request passes through the existing
Authentik outpost; callbacks go to the outpost separately. The sidecar has no
ACME resolver, API/dashboard, Docker socket or infrastructure provider.

`domains.mqtt_explorer` is the GUI hostname. It is separate from
`hostnames.mqtt_broker`, which remains the native MQTT publication. The consumer
must select an already qualified Authentik provider and its access policy for the
GUI hostname. This composition neither creates nor changes identity providers.

The source declares only the two additional backend connections: ingress to the
GUI gateway on TCP80, and the GUI gateway to the existing outpost on TCP9000.
Compilation checks declared relationships; it does not establish target firewall
enforcement or introduce a broader access policy.

## Dedicated broker account and saved profile

The selected `stack.mqtt_explorer.broker_connection` names a new dedicated MQTT
account with `access: read-write-all`. It can read and publish all broker topics.
Its username and credential ID are consumer bindings. The read-only probe,
existing client credentials and identity-provider secret are separate inputs.

Ordinary input preparation creates or reuses one private managed-credential
record and binds its unchanged value to
`${inputs}/managed-${credentials.mqtt_explorer}.json`. A mismatch or foreign
account collision refuses instead of rotating, replacing or adopting it. The
consumer supplies the exact existing `paths.mqtt_password_file`; no ACL file or
new broker authentication mechanism is inferred. The framework qualifies the
parent-mounted password file before an atomic account addition and HUP, without
recreating the retained broker or disconnecting its established clients.

Explorer stores a native version1 connection profile in its own
`/srv/homelab/data/mqtt-explorer` workspace. Existing profiles and unrelated
settings are retained. Its JSON contains the broker password, shared among the
authorized GUI users, so the parent is private0700 and the generated process uses
umask077. No password is placed in Git or application environment variables. No
fixed MQTT client ID, automatic connection, public demo broker or AI API key is
selected by the profile. Normal broker and GUI deployment phases target their
own services; GUI-only changes do not recreate the broker.

The GUI and gateway limits are256MiB and128MiB, alongside the unchanged256MiB
broker limit in the existing1024MiB guest. These are initial source resource
limits, not a load-capacity guarantee. Local health checks verify the application
and loaded gateway without requiring the identity provider to be available.
Actual browser sign-in, dedicated-account operation and existing-client
continuity are acceptance checks after authorized deployment.
