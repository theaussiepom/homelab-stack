[Application catalogue](../README.md)

# CloudBeaver with Authentik forward authentication

CloudBeaver Community Edition accepts the username that Traefik receives from Authentik. Traefik sets the CloudBeaver team to `user` and removes client-supplied role headers. Give this backend its own Compose bridge and restrict TCP 8978 on its guest interface to the Traefik guest. The profile runs a single CloudBeaver container and supplies the MariaDB administration driver. [Profile definition](../../../apps/cloudbeaver-forward-auth.yaml)

## Minimal usage

The `administration` app in the complete example binds the database account, one HTTPS exposure, an Authentik provider and the admission group. [Complete site](../../../examples/catalogue/database-forward-auth.yaml)

```yaml
apps:
  administration:
    profile: cloudbeaver-forward-auth
    guest: administration
    lifecycle: retained
```

## First installation

Provide Authentik with its embedded proxy outpost, the site's existing admission group and its authorization and invalidation flows. Bind the Traefik forward-auth middleware to the Identity endpoint. The site selects the user group by name. Identity waits for the native worker to apply the registration and verifies the outpost assignment.

The example selects an existing managed installation. The workspace holds CloudBeaver state and has an application-export capture requirement. The MariaDB administration connection uses the declared managed account. PostgreSQL administration requires its own account selection. [Backup coverage](../backup-coverage.md#cloudbeaver-forward-auth)

## Later deployments

When moving a retained CloudBeaver installation to this profile, keep the server, database account and workspace identities. Supply the existing local recovery password through the profile's required `recovery_password` secret. CD compares it with the previous installation’s sealed configuration before retiring the gateway. CD verifies ownership of the old gateway and its two configuration files before retiring them. Authentik supplies the username for new browser sessions. A previous gateway that prefixed usernames can leave the same person with a different CloudBeaver profile.

The guest checks its server and declared database connections. For a site using deferred checks, the existing web job verifies the public redirect after deployment. Complete a fresh browser sign-in to check the user's return to CloudBeaver.

## Invalid cases and validation

Compilation rejects an alternate route to the same backend, a shared application bridge, a backend grant for another client and a middleware chain that fails to bind the authenticated username and fixed team. An existing proxy registration with an unrelated access binding causes Identity to stop before adoption.

## Declaration records

The table lists the fields supplied by this profile. [Reading declaration records](../declaration-records.md)

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-adapter"></a>`adapter` | `"cloudbeaver"` |
| <a id="declaration-display-name"></a>`display_name` | `"CloudBeaver"` |
| <a id="declaration-interfaces"></a>`interfaces` | `object` |
| <a id="declaration-interfaces-web-interface"></a>`interfaces.web_interface` | `object` |
| <a id="declaration-interfaces-web-interface-required"></a>`interfaces.web_interface.required` | `true` |
| <a id="declaration-interfaces-web-interface-accepts"></a>`interfaces.web_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-private-interface"></a>`interfaces.private_interface` | `object` |
| <a id="declaration-interfaces-private-interface-required"></a>`interfaces.private_interface.required` | `true` |
| <a id="declaration-interfaces-private-interface-accepts"></a>`interfaces.private_interface.accepts` | `["app-network"]` |
| <a id="declaration-interfaces-postgresql-interface"></a>`interfaces.postgresql_interface` | `object` |
| <a id="declaration-interfaces-postgresql-interface-required"></a>`interfaces.postgresql_interface.required` | `false` |
| <a id="declaration-interfaces-postgresql-interface-accepts"></a>`interfaces.postgresql_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-interfaces-mariadb-interface"></a>`interfaces.mariadb_interface` | `object` |
| <a id="declaration-interfaces-mariadb-interface-required"></a>`interfaces.mariadb_interface.required` | `false` |
| <a id="declaration-interfaces-mariadb-interface-accepts"></a>`interfaces.mariadb_interface.accepts` | `["guest-interface"]` |
| <a id="declaration-listeners"></a>`listeners` | `object` |
| <a id="declaration-listeners-web-listener"></a>`listeners.web_listener` | `object` |
| <a id="declaration-listeners-web-listener-service"></a>`listeners.web_listener.service` | `"cloudbeaver"` |
| <a id="declaration-listeners-web-listener-namespace"></a>`listeners.web_listener.namespace` | `"app-network"` |
| <a id="declaration-listeners-web-listener-interface"></a>`listeners.web_listener.interface` | `"private_interface"` |
| <a id="declaration-listeners-web-listener-bind"></a>`listeners.web_listener.bind` | `"wildcard"` |
| <a id="declaration-listeners-web-listener-protocol"></a>`listeners.web_listener.protocol` | `"tcp"` |
| <a id="declaration-listeners-web-listener-port"></a>`listeners.web_listener.port` | `8978` |
| <a id="declaration-listeners-web-listener-publish"></a>`listeners.web_listener.publish` | `object` |
| <a id="declaration-listeners-web-listener-publish-scope"></a>`listeners.web_listener.publish.scope` | `"guest-interface"` |
| <a id="declaration-listeners-web-listener-publish-interface"></a>`listeners.web_listener.publish.interface` | `"web_interface"` |
| <a id="declaration-listeners-web-listener-publish-port"></a>`listeners.web_listener.publish.port` | `8978` |
| <a id="declaration-endpoints"></a>`endpoints` | `object` |
| <a id="declaration-endpoints-web-endpoint"></a>`endpoints.web_endpoint` | `object` |
| <a id="declaration-endpoints-web-endpoint-listener"></a>`endpoints.web_endpoint.listener` | `"web_listener"` |
| <a id="declaration-endpoints-web-endpoint-protocol"></a>`endpoints.web_endpoint.protocol` | `"http"` |
| <a id="declaration-endpoints-web-endpoint-via"></a>`endpoints.web_endpoint.via` | `"web_interface"` |
| <a id="declaration-storage"></a>`storage` | `object` |
| <a id="declaration-storage-workspace"></a>`storage.workspace` | `object` |
| <a id="declaration-storage-workspace-target"></a>`storage.workspace.target` | `"/opt/cloudbeaver/workspace"` |
| <a id="declaration-storage-workspace-read-only"></a>`storage.workspace.read_only` | `false` |
| <a id="declaration-storage-workspace-required"></a>`storage.workspace.required` | `true` |
| <a id="declaration-storage-workspace-kind"></a>`storage.workspace.kind` | `"directory"` |
| <a id="declaration-storage-workspace-initialize"></a>`storage.workspace.initialize` | `object` |
| <a id="declaration-storage-workspace-initialize-type"></a>`storage.workspace.initialize.type` | `"directory"` |
| <a id="declaration-storage-workspace-initialize-uid"></a>`storage.workspace.initialize.uid` | `8978` |
| <a id="declaration-storage-workspace-initialize-gid"></a>`storage.workspace.initialize.gid` | `8978` |
| <a id="declaration-storage-workspace-initialize-mode"></a>`storage.workspace.initialize.mode` | `"0700"` |
| <a id="declaration-connections"></a>`connections` | `object` |
| <a id="declaration-connections-postgresql"></a>`connections.postgresql` | `object` |
| <a id="declaration-connections-postgresql-type"></a>`connections.postgresql.type` | `"postgresql"` |
| <a id="declaration-connections-postgresql-required"></a>`connections.postgresql.required` | `false` |
| <a id="declaration-connections-postgresql-readiness"></a>`connections.postgresql.readiness` | `["start"]` |
| <a id="declaration-connections-mariadb"></a>`connections.mariadb` | `object` |
| <a id="declaration-connections-mariadb-type"></a>`connections.mariadb.type` | `"mariadb"` |
| <a id="declaration-connections-mariadb-required"></a>`connections.mariadb.required` | `false` |
| <a id="declaration-connections-mariadb-readiness"></a>`connections.mariadb.readiness` | `["start"]` |
| <a id="declaration-connections-postgresql-admin"></a>`connections.postgresql-admin` | `object` |
| <a id="declaration-connections-postgresql-admin-type"></a>`connections.postgresql-admin.type` | `"postgresql"` |
| <a id="declaration-connections-postgresql-admin-required"></a>`connections.postgresql-admin.required` | `false` |
| <a id="declaration-connections-postgresql-admin-accounts"></a>`connections.postgresql-admin.accounts` | `["postgresql-admin"]` |
| <a id="declaration-connections-mariadb-admin"></a>`connections.mariadb-admin` | `object` |
| <a id="declaration-connections-mariadb-admin-type"></a>`connections.mariadb-admin.type` | `"mariadb"` |
| <a id="declaration-connections-mariadb-admin-required"></a>`connections.mariadb-admin.required` | `true` |
| <a id="declaration-connections-mariadb-admin-accounts"></a>`connections.mariadb-admin.accounts` | `["mariadb-admin"]` |
| <a id="declaration-software"></a>`software` | `["docker", "curl", "cloudbeaver-server-image"]` |
| <a id="declaration-runtime"></a>`runtime` | `["container-host", "cloudbeaver-server"]` |
| <a id="declaration-health"></a>`health` | `object` |
| <a id="declaration-health-ready"></a>`health.ready` | `object` |
| <a id="declaration-health-ready-profile"></a>`health.ready.profile` | `"adapter-ready"` |
| <a id="declaration-authentication"></a>`authentication` | `"cloudbeaver-forward-auth"` |
| <a id="declaration-secrets"></a>`secrets` | `object` |
| <a id="declaration-secrets-recovery-password"></a>`secrets.recovery_password` | `object` |
| <a id="declaration-secrets-recovery-password-required"></a>`secrets.recovery_password.required` | `true` |
| <a id="declaration-monitoring"></a>`monitoring` | `object` |
| <a id="declaration-monitoring-profile"></a>`monitoring.profile` | `"docker-agent"` |
| <a id="declaration-properties"></a>`properties` | `object` |
| <a id="declaration-properties-mariadb-jdbc"></a>`properties.mariadb_jdbc` | `object` |
| <a id="declaration-properties-mariadb-jdbc-version"></a>`properties.mariadb_jdbc.version` | `"3.5.11"` |
| <a id="declaration-properties-mariadb-jdbc-sha256"></a>`properties.mariadb_jdbc.sha256` | `"42604178b9e57ec08ee0035079961516f086e455d0141f0b22c6eff29fb2fff4"` |
| <a id="declaration-properties-mariadb-jdbc-image-filename"></a>`properties.mariadb_jdbc.image_filename` | `"mariadb-java-client-3.5.10.jar"` |
| <a id="declaration-backup"></a>`backup` | `object` |
| <a id="declaration-backup-include"></a>`backup.include` | `object` |
| <a id="declaration-backup-include-workspace"></a>`backup.include.workspace` | `object` |
| <a id="declaration-backup-include-workspace-category"></a>`backup.include.workspace.category` | `"state"` |
| <a id="declaration-backup-include-workspace-capture"></a>`backup.include.workspace.capture` | `"application-export"` |
| <a id="declaration-backup-exclude"></a>`backup.exclude` | `{}` |
