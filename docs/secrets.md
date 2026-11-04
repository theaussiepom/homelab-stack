# Secrets, data and configuration

Keep secret values outside every Git repository, including private Git. Reusable
profiles declare closed named roles and conditional capability requirements.
Sites bind those roles to supported file/environment sources or explicitly
selected generated account custody. The framework owns validation and protected
materialization; the library does not read secrets or implement another input
engine.

Reusable workflow edges declare named scalar secret slots explicitly. Each app
phase receives only its selected slots, while common provider/SSH credentials use
their existing separate stage. No whole-secret JSON wrapper, inherited secret bag
or caller-name presence replaces value/ownership validation. Environment bindings
and workflow-secret aliases are source metadata, not secret values or evidence
that a value exists on a runner.

Existing controller-private inputs remain owned by their original parser: retained
Bitwarden environment, PegaProx database key, MQTT probe JSON, WiNet options and
selected authentication material. An optional role does not waive a capability's
required input. Zabbix's root feature retains its existing generated credential
record; it is not a new required environment password. Do not invent another
secret merely to bypass a custody check.

Managed MQTT/DB accounts have separate explicit owners and credential identities.
Their protected create-once record is reused unchanged; collision, drift and
foreign ownership refuse. Explorer's saved profile and CloudBeaver's managed
native datasource contain plaintext passwords at rest and remain private. No
encryption-at-rest guarantee is claimed. See [Explorer](mqtt-explorer.md) and
[database administration](database-tools.md#connections-and-dedicated-administration).

Application data, private archives, HA/Node-RED credentials, Zigbee network keys,
radio backups and commissioning records remain consumer-owned. The source does
not retrieve or restore them. Retained paths, modes, ownership, holds and required
prerequisites must be preserved before an update. Music's floating image policy
also requires its protected pre-upgrade data copy and resolved-image record;
ordinary deployment does not reset providers or accounts.
