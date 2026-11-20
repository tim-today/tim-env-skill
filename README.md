# tim-env

**Give your AI coding assistant a reliable place to find and maintain project environment knowledge.**

A skill for managing SDKs, tool paths, service connections, runtime configuration, lifecycle commands, builds, and deployments in English Markdown. Records live outside your source tree in `~/.tim-env`, isolated by canonical project path, so you can reuse environment knowledge without repeatedly supplying it or mixing settings between projects.

The skill combines instructions for an AI assistant with a local Python helper. The helper handles location, initialization, verified migration, and checks. The assistant collects relevant information, understands configuration, and updates documentation as part of the current task.

## When to use it

- **Project onboarding:** document SDK requirements, configuration sources, startup commands, and dependencies.
- **Development:** update versions, paths, ports, and commands as they are discovered.
- **Troubleshooting:** read the relevant environment first and distinguish declarations from verified runtime state.
- **Builds and packaging:** find the correct toolchain, working directory, configuration injection, and artifact outputs.
- **Deployment and maintenance:** consolidate hosts, SSH, directories, service connections, lifecycle operations, releases, and rollback.
- **Legacy upgrades:** migrate in-project `.tim-env` records into the user store and detect tracked leftovers.

Ordinary business-code edits do not trigger a full environment scan. This is not a background monitor, password manager, automatic deployment system, or environment autodiscovery service.

## Installation

### Requirements

- An AI assistant that supports skills defined by `SKILL.md`. Codex interface metadata is included.
- Python 3; the helper uses only the standard library. No `pip install` is required.
- macOS or Linux with `fcntl` file locking and POSIX permissions. Native Windows cannot run the helper directly; use WSL, with paths and records managed inside that environment.
- Git for cloning/updating and checking tracked legacy records. Non-Git projects are also supported.

### Install the skill

Clone the full repository into a `tim-env` folder within a skill search path supported by your assistant. For example, if your client uses `~/.codex/skills` for personal skills:

```sh
mkdir -p "$HOME/.codex/skills"
git clone https://github.com/tim-today/tim-env-skill.git "$HOME/.codex/skills/tim-env"
```

If the destination exists, check its origin and local changes rather than overwriting it. Refresh skill discovery as required by your client. Other Agent Skills clients can use the same files, but installation paths, automatic discovery, and interface-metadata support vary by client.

The installation directory contains public instructions and code. `~/.tim-env` contains local project records. **Do not put project environment records in this repository.**

## Quick start

In an assistant session opened for your target project:

```text
Use $tim-env to organize this project's local development environment:
SDKs, startup commands, dependency services, configuration sources, and build
artifacts. Store records in the user directory and mark unknowns To confirm.
```

For later tasks:

```text
Use $tim-env to read the existing records first, then help diagnose the Redis
connection issue in the test environment.
```

```text
Use $tim-env to document the production environment: SSH, service connections
and credential references, directories, URLs, lifecycle commands, deployment,
and rollback. Only organize records for this task.
```

The usual workflow is:

1. Confirm the actual project root and run `init` to locate records and handle legacy migration.
2. Read `index.md` and relevant environment sections from the returned `records_dir`.
3. Incrementally update records using task-relevant configuration, user information, and actual verification results.
4. Add a short discovery rule to the project's `AGENTS.md`, preserving unrelated text.
5. Report updates, verified scope, and unknowns that still affect the task.

The `init` command does not collect SDK information, generate complete runbooks, or edit `AGENTS.md`; the assistant does that by following the skill. Implicit invocation is enabled in the included metadata, but actual loading depends on the client. Discovery rules cannot guarantee execution in every client.

## Record layout

```text
~/.tim-env/
└── projects/
    └── <project-id>/
        ├── project.json          # Script-managed project identity
        ├── index.md              # Navigation, environments, critical gaps
        ├── sdk.md                # Requirements, installed versions, tool paths
        ├── paths.md              # Local/remote paths, mounts, caches
        ├── modules.md            # Modules, endpoints, ports, dependencies
        ├── services.md           # Shared service definitions
        ├── build.md              # Build commands, configuration, outputs
        ├── environments/
        │   ├── local.md
        │   ├── test.md
        │   └── production.md
        ├── deploy/               # Actual deployment-target procedures
        ├── scripts/              # Local-only helpers
        └── secrets/              # Only for explicitly requested plaintext storage
```

This is a possible layout, not a mandatory set of empty files. Initialization creates only identity and index files; further documents follow real content. Larger projects can split build/service records by module.

Each real environment has a complete runbook consolidating effective values: hosts and access requirements, SDKs, module endpoints, database/Redis/MQ connections, accounts and credential references, directories, lifecycle/diagnostic commands, builds, deployment, and rollback. Shared definitions may be linked, but operators should not have to reconstruct effective settings across multiple files.

Records retain sources, status, and verification dates. Statuses are `Verified`, `Declared in configuration`, `User-provided`, `To confirm`, and `Obsolete`. Reading configuration is not runtime verification, and unknown values are not filled with guesses.

## Project identity

- The helper generates the full SHA-256 of the canonical absolute root path. Use its output to locate records.
- Switching branches at the same path keeps the same identity; document branch-specific settings explicitly.
- Different clones, worktrees, and same-name directories are isolated. Names and Git remotes do not trigger automatic merges.
- Symlink entry points resolve to the same real project root.
- Monorepos normally share one root-level record set with module IDs; independent nested repositories are separate.
- Moving or renaming a root produces a new identity. Reusing old records requires explicit ownership checks and rebinding; the helper has no automatic rebind command.
- Store and project directories must not contain each other. The home directory itself cannot be the project root.

## Command reference

Examples assume installation at `~/.codex/skills/tim-env`. Replace sample project and artifact paths with real absolute paths.

```sh
# Locate records without creating or migrating anything
python3 "$HOME/.codex/skills/tim-env/scripts/tim_env.py" resolve --root "/absolute/path/to/project"

# Initialize identity/index and attempt legacy migration when needed
python3 "$HOME/.codex/skills/tim-env/scripts/tim_env.py" init --root "/absolute/path/to/project"

# Check external identity/permissions, legacy remnants, and Git index
python3 "$HOME/.codex/skills/tim-env/scripts/tim_env.py" check --root "/absolute/path/to/project"

# Inspect the actual upload staging directory or archive
python3 "$HOME/.codex/skills/tim-env/scripts/tim_env.py" artifact --path "/absolute/path/to/release.zip"
```

| Command | Purpose | Writes records? |
| --- | --- | --- |
| `resolve --root` | Return canonical root, record/index paths, and existence | No |
| `init --root` | Create identity/index, check/migrate legacy records, run checks | Yes |
| `migrate --root` | Compatibility entry point for the same flow as `init` | Yes |
| `check --root` | Check identity/permissions, legacy directory, Git index | No |
| `artifact --path` | Check `.tim-env` path components and links in supported artifacts | No |

Commands return JSON. Success uses `ok: true` and exit code `0`; failed checks or caught operation errors use `ok: false` and exit code `1`. Invalid arguments are handled by the argument parser. Inspect `issues`, `error`, or `migration` for details. A returned `records_dir` alone does not mean success.

`resolve`, `init`, `migrate`, and `check` accept `--store "/absolute/path/to/store"` for isolated tests or explicitly requested external storage. Its parent must exist, and subsequent commands must use the same option. Normal use needs no override.

## Migrating legacy `.tim-env`

`init` and `migrate` inspect `.tim-env` directly under the specified project root:

1. Verify external identity and file types; reject links, special files, and unsuitable target records.
2. Compare paths, types, and file SHA-256 values. Preserve both sides and report conflicts when contents differ.
3. Copy through a private staging directory, verify the destination and unchanged source, then remove the legacy directory.
4. Check whether Git still tracks legacy paths.

Resolve conflicts before retrying; do not bypass remnants for affected releases. The helper does not edit the Git index, rewrite document paths/history, or execute migrated scripts. The assistant must also review old command working directories/references and update the project discovery rule.

Moving tracked records out of the working tree does not remove them from the index or history. Limit index cleanup to legacy `.tim-env` paths and review staged changes. Previously exposed credentials require separate remediation and rotation.

## Credentials and release boundaries

Ordinary records contain accounts, precise credential-storage references, and injection methods: password-manager items, Keychain service/account, variables and their source, or existing key paths. Authentication fields remain explicit without putting passwords, tokens, or private-key contents in normal documents or replies.

Create separate `secrets` documents only when the user explicitly requests local plaintext retention. Store directories use `700` and record files `600`. These are local access restrictions, **not encryption**. Fix permission issues on specific paths without recursively following links.

Neither the external store nor legacy `.tim-env` belongs in Git, images, upload packages, or server deployments. External storage reduces accidental inclusion but does not prevent scripts from copying it. Review actual Docker contexts, COPY/ADD, CI, archives, and upload scripts.

`artifact` supports staging directories, ZIP-based formats (including APK/AAB/JAR), and tar archives. It reports `.tim-env` paths and links requiring review. It does not inspect renamed record copies, nested archives, or image layers, and is not a general secret scanner. `check` does not inspect Git history, remote deployments, or every build script.

The helper makes no network requests. Documentation work does not automatically install/upgrade SDKs, connect to production, restart services, deploy, or sync records to the cloud. A recorded command is not execution authorization.

## FAQ

**Why are environment files missing after initialization?** The helper creates the index, not full runbooks. Ask the assistant to organize actual environments using the skill. Required unknowns stay `To confirm`; services and empty tables are not invented.

**Why does another worktree have no records?** Identity follows the actual root path. Isolation is intentional. Verify ownership and local paths before reuse; do not copy an old identity file into a new record directory.

**Why does a check fail after migration?** Inspect the failure fields. Common causes include tracked Git paths, content conflicts, permissive permissions, links, and identity mismatches. Fix the specific issue, then rerun `init` and `check`.

**Why was the skill not called automatically?** Invoke `$tim-env` explicitly and confirm your client discovered the complete skill directory. `AGENTS.md` is a discovery hint, not a substitute for installation/client support.

**Can records sync across machines?** There is no synchronization feature. Records contain local paths and connection details and should not be committed here. Verify the actual environment again on each machine.

## Repository files

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Assistant triggers, workflow, and constraints |
| [agents/openai.yaml](agents/openai.yaml) | Codex display metadata, default prompt, invocation policy |
| [scripts/tim_env.py](scripts/tim_env.py) | Local location, initialization, migration, and checks |
| [references/records.md](references/records.md) | Record layout and formats |
| [references/environment.md](references/environment.md) | Complete environment runbook fields/template |
| [references/storage.md](references/storage.md) | Identity, storage, migration, and path changes |

## Updates and feedback

For a Git installation with no unresolved local changes, run `git pull --ff-only` in the skill directory. Updating skill files does not itself change `~/.tim-env`; a later `init` checks/migrates the specified project's records. If your checkout predates a repository history reset, install a fresh clone instead of merging unrelated histories; preserve any local edits first.

Report problems or suggestions through [GitHub Issues](https://github.com/tim-today/tim-env-skill/issues). Use fictional projects/service values and minimal redacted errors. Do not attach environment stores, real credentials, or complete production configuration.

## License

[MIT License](LICENSE).
