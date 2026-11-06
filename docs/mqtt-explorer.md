# MQTT Explorer

The canonical [MQTT Explorer profile reference](reference/apps/mqtt_explorer.md) covers gateway/authentication, broker targeting, roles, storage, inputs, runtime and lifecycle limits. [MQTT](reference/apps/mqtt.md) remains independently selectable.

## Saved account and profile

Read [Explorer requirements](reference/apps/mqtt_explorer.md#application-requirements) and [Connect apps](guides/connect-apps.md#mqtt-and-a-saved-hostname). Managed all-topic access and explicit existing credentials are separate choices; neither reuses the broker probe. The saved profile contains a plaintext password in protected app data. Updating the GUI does not implicitly recreate the broker or rotate credentials.
