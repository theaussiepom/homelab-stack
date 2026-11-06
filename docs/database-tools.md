# CloudBeaver profiles

The canonical reference is [CloudBeaver](reference/apps/cloudbeaver.md), with the explicit [MariaDB-admin variant](reference/apps/cloudbeaver-mariadb-admin.md). Both pages cover roles, gateway/authentication, workspace, inputs, software, budgets and lifecycle limits.

## Connections and dedicated administration

See [CloudBeaver requirements](reference/apps/cloudbeaver.md#application-requirements), [the variant](reference/apps/cloudbeaver-mariadb-admin.md#application-requirements) and [Connect apps](guides/connect-apps.md#database-connections). Managed PostgreSQL/MariaDB administration is a deliberate powerful account capability, not metadata-only connection setup or database initialization.

## Saved credentials and retained state

See [Cloud workspace/inputs](reference/apps/cloudbeaver.md#connections-accounts-and-private-inputs) and [Secrets, data and configuration](secrets.md). Saved managed credentials are plaintext at rest in the protected workspace; no encrypted-at-rest guarantee is claimed.
