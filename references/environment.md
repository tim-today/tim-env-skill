# Environment runbook specification

Use for initial organization or completing environment records. These are field checklists/templates, not claims about a real environment. Give each actual environment one complete document. Remove irrelevant optional sections; use `To confirm` for required unknowns and `Not applicable` when confirmed. Do not create/connect to remote services to fill tables.

Generated runbooks should contain headings, tables, and necessary commands. Record source, status, and verification date per object, or shared metadata below a group. Never invent commands or copy template explanations into project records.

## 1. Overview

Title: `# <Environment name> (<environment-id>)`.

| Field | Content |
| --- | --- |
| Updated / verified on | Actual dates; To confirm if unverified |
| Purpose / modules | Local, development, test, staging, production, or actual name; module IDs |
| Hosts / cluster / region | Host IDs, cloud region, K8s context/namespace |
| OS / architecture / timezone | Distinguish local and remote |
| Access prerequisites | Actual VPN, private network, jump host, IP allowlist |
| Configuration entry points / precedence | Profiles, files, variables, configuration-service overrides |
| Release version / build / deployment targets | Known versions and IDs |
| Known operating scope | Current authorization/defined permissions; do not expand |
| Source / status | Configuration paths, user information, verification evidence |

Assign separate host IDs. Commands and paths must identify the host rather than referring vaguely to “the server.”

## 2. Hosts, SSH, and file transfer

One section per actual host:

| Field | Content |
| --- | --- |
| Host ID / purpose | Application, database, proxy, build machine, etc. |
| Private / public address / SSH port | Separate values; Not applicable if no public address |
| SSH alias / user / authentication | SSH config Host, username, agent/key/password |
| Password / private key / passphrase | Exact references, not private-key or passphrase contents |
| SSH config / known_hosts | Existing paths; known fingerprints and sources if available |
| Jump host / ProxyJump / VPN | Targets and dependency references |
| Login shell / working directory | Shell, required profiles, toolchain initialization |
| sudo / runtime user / scope | Known information or To confirm; do not probe elevation |
| SFTP / FTP / FTPS | Actual protocol, host, port, user, credentials, TLS, remote root |
| Local staging / remote destination | Actual directories and filtering |

Document existing login, transfer, and forwarding commands with execution host, target, cwd, and success criteria. Forwarding needs local bind address/port, destination host/port, occupancy check, and shutdown method; do not assume a tunnel exists. Never disable SSH host-key verification.

## 3. SDKs and runtime tools

| Module / host | Tool | Required version | Actual version | Executable path / HOME | Switching / initialization | Source / status / verified on |
| --- | --- | --- | --- | --- | --- | --- |

Consolidate effective JDK, Node, package manager, Maven/Gradle, Python, mobile toolchain, Docker/Compose, and kubectl/Helm values as applicable, linking shared SDK definitions. Separate container runtimes from host tools, and local PATH from server PATH.

## 4. Modules, endpoints, and ports

| Module / instance | Host / container / workload | Internal listen address:port | Host-mapped port | Internal URL | External URL / domain | Context / base path | Health check |
| --- | --- | --- | --- | --- | --- | --- | --- |

Include actual frontend, admin, API, gateway, docs/Swagger, monitoring, MQ console, and object-storage consoles as applicable. Record protocol, proxy/TLS termination, certificates, authentication, account/credential references. Separate management and business endpoints; do not infer public reachability. Include actual DNS/hosts overrides, upstreams, callbacks, and WebSocket endpoints when used.

## 5. Database and middleware connections

One section per service instance. Identify shared modules/environments and separate application/admin accounts.

### Databases

| Instance / type / version | Host / port / network scope | Database / schema | Account / purpose / permissions | Password / credential reference | TLS / certificates | Encoding / timezone / connection options |
| --- | --- | --- | --- | --- | --- | --- |

Add redacted JDBC/DSN templates, configuration keys/injection, client tools/paths, safe connection commands, migration entry points, data/log directories, and existing backup/restore references. Record actual MySQL/PostgreSQL/etc. usage; identify read/write splits, read-only instances, and cluster endpoints separately. Do not embed passwords in URLs, arguments, or examples.

### Redis

| Instance / version / mode | Host / port | DB index / key prefix | ACL user / authentication | Password / credential reference | TLS / certificates | Configuration / data directory |
| --- | --- | --- | --- | --- | --- | --- |

Include actual standalone/Sentinel/Cluster details, Sentinel endpoints/master name, nodes, separate authentication references, clients, safe connections, cache purpose, and shared scope. No-password claims require a source. Do not run full `KEYS` scans or clear caches to verify records.

### Message queues

| Instance / type / version | Broker / protocol / port | Vhost / namespace | Application user / authentication | Password / credential reference | TLS / SASL | Console URL / admin-account reference |
| --- | --- | --- | --- | --- | --- | --- |

Include actual RabbitMQ exchanges/queues/routing keys, Kafka bootstrap servers/topics/groups/security protocols, RocketMQ NameServer/topics/groups, etc. Separate business and console ports. Do not create queues/topics or produce/consume messages to fill records.

### Other actual dependencies

For configuration/discovery services, search, object storage, SMTP, third-party APIs, monitoring, and scheduling, record actual endpoints, protocol/ports, tenant/bucket/index, accounts/credentials, TLS, configuration entry points, management URLs, and sharing. Omit dependencies not used by the project.

## 6. Start, stop, restart, and diagnostics

Use the following table for each application and dependency actually managed by the project. For hosted services without local lifecycle control, use `Platform-managed; not applicable` or an existing management entry point; do not invent commands.

| Object ID | Operation | Execution host / cwd / shell | Exact command / script | Prerequisites / injection | Success criteria | Impact |
| --- | --- | --- | --- | --- | --- | --- |
| <object> | Start | To confirm | To confirm | To confirm | To confirm | To confirm |
| <object> | Stop | To confirm | To confirm | To confirm | To confirm | To confirm |
| <object> | Restart | To confirm | To confirm | To confirm | To confirm | To confirm |
| <object> | Status | To confirm | To confirm | To confirm | To confirm | To confirm |
| <object> | Logs | To confirm | To confirm | To confirm | To confirm | To confirm |
| <object> | Health check | To confirm | To confirm | To confirm | To confirm | To confirm |

Use inline code for short commands and linked operation IDs for multi-step shell blocks. Include:

- Dependency/readiness and shutdown order, graceful stop/timeouts, background/process management, PID source. Do not terminate unrelated services with vague process matching.
- Actual systemd units, launchd labels, PM2 apps, Compose project/profile/service, container names, or K8s context/namespace/workload. Do not depend on an implicit current cluster/directory.
- Separate application restart from whole-environment restart. Shared databases/Redis/MQ do not restart with applications. Document a combined lifecycle entry point only if one exists; do not create destructive scripts for completeness.
- Log paths, time/line limits or rotation, and the distinction between process liveness, readiness, and business availability. Only mark success criteria verified when evidence exists.
- Brief troubleshooting notes: symptom, diagnostic commands, known cause, existing recovery. Data clearing, volume deletion, and `kill -9` are not routine remedies.

## 7. Directories, configuration, volumes, and certificates

| Host / object | Purpose | Actual path | Host/container mapping | Owner / permissions | Persistence / cleanup constraints | Source / status |
| --- | --- | --- | --- | --- | --- | --- |

Cover actual source/SDK paths, deployment roots, releases/current links, upload staging, configuration/.env, logs, PIDs, temp/cache, attachments, database/Redis/MQ data, backups, static assets, certificates/truststores/signing files. Distinguish local/remote/container paths and real mounts; never copy key contents.

## 8. Build, release, and rollback

| Build / deployment target | Module / profile | Execution host / cwd | Command / script | Artifacts / output directory | Deployment directory / image | Verification / readiness |
| --- | --- | --- | --- | --- | --- | --- |

Consolidate effective commands/artifacts; link build/deploy files for complex parameters, signing, and pipelines. Record preparation, build, artifact checks, upload, migrations if applicable, switch, start/restart, health checks, and rollback in order. Identify stateful steps and external impact. Include available rollback versions/backups and application/data compatibility; mark unknowns `To confirm`, not “rollback supported.”

## 9. Credential discovery

| Credential ID | Object / account | Password / token / key reference | Retrieval / injection | Scope / expiration | Source / status |
| --- | --- | --- | --- | --- | --- |

References must locate credentials during authorized work: exact password-manager item/field, Keychain service/account, variable plus source file, or `<records-dir>/secrets/<environment-id>.md#<credential-id>`. “Configured” or “see environment variables” is insufficient. Do not enumerate an entire vault to locate a field.

Prefer secure-store references. Only when local plaintext retention is explicitly requested, keep values in restricted secrets documents, with credential ID, account, value, purpose, source, and updated date. Ordinary runbooks reference them. Keep private keys in existing files, never copy their contents.

## 10. Verification, exclusions, and gaps

| Check | Actual scope / command | Date | Result / uncovered scope |
| --- | --- | --- | --- |

Record actual exclusions for external/legacy records across Git, Docker contexts/specific ignore files, build/upload scripts, staging, and archives. Never mark unperformed checks passed.

| Gap / conflict | Object | Existing sources | Impact on current task | Information needed |
| --- | --- | --- | --- | --- |

Completed documentation does not imply lifecycle operations, connections, release, or rollback were executed. Verification status must reflect actual evidence.
