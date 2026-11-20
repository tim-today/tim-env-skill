# Record structure and formatting

Read when creating or changing record formats. For ordinary build/deployment work, follow the project index directly to relevant records.

## Directory layout

All files below belong in the external `records_dir` returned by `scripts/tim_env.py init --root <project-root>`, never inside the project. See [Storage and migration](storage.md).

```text
~/.tim-env/projects/<project-id>/
  project.json                  # Script-managed identity; do not edit the hash
  index.md                      # Navigation, IDs, sources, critical gaps
  sdk.md                        # Project requirements and local toolchain
  paths.md                      # Directories, caches, mounts, mappings
  modules.md                    # Modules, dependencies, startup order, URLs
  services.md                   # Shared database/Redis/MQ definitions
  build.md                      # Build targets and artifacts, including APK/IPA/desktop
  environments/
    local.md                    # Complete local runbook
    test.md
    production.md
    <environment-id>.md
  deploy/
    <deployment-target-id>.md   # Actual Docker/K8s/SSH/FTP/etc. deployment
  scripts/                      # Local-only scripts referenced from Markdown
  secrets/
    <environment-id>.md        # Only for explicitly requested plaintext retention
```

Create only files with real content and environments that actually exist. Small projects may start with SDK/build/local records. Large projects can split `build/<module-id>.md` or `services/<service-id>.md`; update the index. Do not create a parallel duplicate structure.

## Shared formatting

- Use English headings, Markdown tables, and language-tagged command blocks. Omit tutorials, pleasantries, speculation, and repeated explanations.
- Start documents with `Updated` and `Applicable modules/environments`. Preserve `Source`, `Status`, and `Verified on`; shared metadata may appear below a table.
- Commands need working directory, shell/OS, prerequisites, environment injection, output location, and success criteria. Identify the module rather than recording only `npm run build`. Reference sensitive values through variables using the actual script's input method.
- Distinguish project-relative, local absolute, and remote paths. Quote spaces. Keep passwords and credential-bearing query parameters out of URLs/DSNs.
- Replace changed fields, preserve useful manual notes, and mark obsolete entries outside effective operating instructions. Do not accumulate chat logs.

## index.md

```markdown
# Project environment index

Updated: <actual-date>
Project root: <actual-path>
Project name: <actual-name>

| Topic | File | Applicable modules / environments |
| --- | --- | --- |
| SDK | [SDK](sdk.md) | <module-id> |

## Environments

| Environment ID | Name / purpose | Complete runbook | Modules | Verification status |
| --- | --- | --- | --- | --- |
| <environment-id> | <purpose> | [Runbook](environments/<environment-id>.md) | <module-id> | <status> |

## To confirm

| Item | Impact | Information needed |
| --- | --- | --- |

## Release exclusions

| Scope | Rule / file | Last checked | Status |
| --- | --- | --- | --- |
```

Keep navigation, related IDs, critical gaps, and exclusion results in the index, not every connection detail or plaintext secret.

## sdk.md

| Tool / runtime | Module | Project requirement | Local installation | Executable path | Version manager / configuration source | Status | Verified on |
| --- | --- | --- | --- | --- | --- | --- | --- |

Cover actual tools: JDK/JAVA_HOME, Node/package managers/Corepack, Python, Go, Rust, .NET, Maven/Gradle wrappers, Android SDK/NDK/build-tools/adb, Xcode/Flutter, Docker/Compose/kubectl/Helm, and database clients. Record architecture, OS, image version/digest when available, switching method, and necessary variable names. Keep service versions in service records, distinct from local client versions. Prefer wrappers/lockfiles; do not infer requirements from system defaults.

## paths.md

| Path ID | Purpose | Host / environment | Path | Access / mount relationship | Source | Status |
| --- | --- | --- | --- | --- | --- | --- |

Cover relevant project/tool/cache/data/log/temp directories, certificates, artifact directories, host/container mappings, and remote working directories. Do not scan unrelated directories.

## modules.md

| Module ID | Directory | Stack | Required modules / services | Startup order | Startup-command reference | Environment ID |
| --- | --- | --- | --- | --- | --- | --- |

Use separate URL rows per environment: module/environment IDs, protocol, listen address/port, internal/external URLs, domain, proxy/TLS termination, health endpoint, source, and status. Distinguish container, host, and public ports.

## services.md

Use one stable ID per service and record:

- Type, purpose, required/verified server version, related modules and environment references.
- Host, port, protocol, database/schema, Redis DB, MQ vhost/topic/queue/group, encoding/timezone, and necessary connection options as applicable.
- Username, credential reference/injection, TLS/certificate references, and known relevant pool settings.
- Docker/Compose service/network aliases, K8s service/namespace, dependencies, health checks, and data-volume references.
- Safe connection-command templates, sources, and verification dates. Only record verification actually performed with authorization.

Do not make production the default or write to databases, migrate data, or restart services just to complete records.

## build.md or build/<module-id>.md

Use this structure per target; unknown required values are `To confirm`:

````markdown
## <build-target-id>

| Field | Value |
| --- | --- |
| Module / target environment | <IDs> |
| Working directory / OS / shell | <value> |
| SDK / prerequisites | <SDK reference> |
| Configuration / variables | <paths, variable names, credential references> |
| Script / entry point | <path> |
| Artifacts | <filename/pattern and absolute/relative directory> |
| Success criteria | <exit code and expected outputs> |
| Source / status / verified on | <value> |

### Commands

```sh
<exact-command-without-plaintext-credentials>
```
````

Do not copy the outer example fence into real records. Include actual clean/install/compile/test/package commands as needed; APK/AAB flavor/buildType/ABI, signing alias/credential references, mapping/symbol outputs; frontend base/public path; image registry/repository/tag/digest/platform; build arguments, version sources, and checksums. Do not invent commands or run unknown release scripts to discover outputs.

## environments/<environment-id>.md

Follow the [Environment runbook](environment.md). Consolidate actual effective SSH, database/Redis/MQ connections and credential references, lifecycle commands, directories, endpoints, builds, and deployments. Link shared sources and refresh effective values when sources change; do not write only “see services.md.” Existing single-file multi-environment sections may remain if the index links directly to them.

## deploy/<deployment-target-id>.md

Record only methods actually used:

| Field | Value |
| --- | --- |
| Environment / module / build target | <IDs / references> |
| Method | <SSH / SFTP / FTP / Docker / Compose / K8s / platform> |
| Host / port / user | <values; credentials referenced separately> |
| SSH alias / jump host / authentication | <configuration source and key/agent references, never private-key contents> |
| Remote / release directory / runtime user | <values> |
| Docker context / build context / Dockerfile / ignore | <actual paths and selection rules> |
| Compose files / project / profile | <values> |
| K8s context / namespace / workload / Helm release | <explicit values, not implicit current cluster> |
| Registry / image / tag | <references> |
| Configuration / secret injection | <source references without sensitive values> |
| Persistent volumes / network / proxy / TLS | <references> |
| Deployment script / working directory | <paths> |
| Prerequisites / migrations / backups | <existing procedures; state if not executed> |
| Health checks / logs / success criteria | <exact methods> |
| Rollback entry point / verified version | <existing procedure or To confirm> |
| .tim-env exclusion / artifact checks | <actual rules, scope, date, results> |
| Source / status / verified on | <values> |

Document actual preflight, build, staging, upload, switch, health-check, and rollback steps, identifying remote mutations. Organizing records does not execute these steps. Keep SSH host-key checks enabled; record actual FTP settings without silently downgrading transport.
