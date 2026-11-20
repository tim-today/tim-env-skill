---
name: tim-env
description: Maintain project environment knowledge in ~/.tim-env, matched by canonical project path, and migrate legacy in-project .tim-env records. Read and update SDKs, tool paths, service connections, runtime configuration, build and deployment instructions when initializing projects, discovering environment changes, troubleshooting, running, building, packaging, or deploying. Do not perform a full environment scan for ordinary business-code edits.
---

# tim-env

Store project environment knowledge in `~/.tim-env/projects/<project-id>/` (the **records directory**) using concise, organized English Markdown. Maintain it incrementally so users do not have to repeat information. Both the external store and legacy in-project `.tim-env` are local records: never commit them to Git or include them in artifacts, images, uploads, or server deployments.

## Entering a project and triggering the skill

- Identify the actual project root first. A monorepo normally has one root-level record set with module IDs; independent nested repositories are separate projects. Do not initialize an arbitrary working directory or infer an environment from its name.
- Before SDK, dependency installation, startup, service connection, build, packaging, deployment, or environment troubleshooting work, run `python3 <skill-dir>/scripts/tim_env.py init --root <project-root>`. Read `index.md` from the returned `records_dir`, then the relevant sections of `environments/<environment-id>.md`, following module/build/deployment references only as needed. Use targeted searches; do not load all records or secrets.
- For initialization or record organization, read [Record structure](references/records.md). The script resolves identity, creates the external index, and verifies/migrates legacy records. It does not collect environment details, create an in-project records directory, or modify the Git index. Run `init` even for existing records to detect directories recreated by older versions. Resolve failures rather than falling back to in-project storage. Create other documents only when actual content exists. Each real environment needs a complete document following the [Environment runbook](references/environment.md), not just scattered links.
- Update the corresponding records when development reveals new versions, paths, ports, commands, or corrections. Ordinary business-code edits do not require unrelated scans.
- After initialization/migration, add the following short discovery rule to the root `AGENTS.md`, creating it if absent. Replace only the managed `tim-env:start/end` block, including older versions of that block; preserve all other text. Do not add credentials, absolute home paths, hashes, or full records. Keep only a non-sensitive discovery rule in the project; do not create a symlink to the store. This helps later sessions discover records but cannot guarantee skill execution in every client.

```markdown
<!-- tim-env:start -->
For project SDKs, environments, service connections, running, building, packaging, or deployment, use the tim-env skill. Run its scripts/tim_env.py init --root <project-root> with the actual project root, then read index.md and relevant environment files from the returned records_dir and update incrementally. Store records only in ~/.tim-env; never create an in-project .tim-env or link to it. Migrate legacy .tim-env using the skill. Never commit, package, upload, or deploy the store or legacy records. If the skill is unavailable, locate the installed skill first; do not guess project IDs or create an in-project substitute.
<!-- tim-env:end -->
```

## Collecting and updating information

1. Prefer user-provided information, project version declarations, lockfiles, build scripts, Compose/K8s/CI configuration, and existing records. Verify executable paths and versions only as needed, distinguishing project requirements from the actual local installation. Do not install/upgrade SDKs, change PATH, start containers, connect remotely, or query production just to fill tables.
2. Inspect only files relevant to the task. Do not scan entire disks, enumerate home-directory credentials, read complete process environments, or dump `.env` files. Extract only required sensitive fields and redact them; keep values out of command arguments, logs, and replies.
3. Record source paths/configuration keys (with line numbers when useful), verification dates, and status. Use only `Verified / Declared in configuration / User-provided / To confirm / Obsolete`. Use actual dates and evidence. Mark unknowns `To confirm` and confirmed non-applicable fields `Not applicable`; never guess passwords, ports, or paths.
4. Preserve a short conflict note with both sources. Ask about critical differences needed for the current operation, while continuing independent documentation. Do not silently treat a declaration as runtime verification.
5. Use stable IDs for modules, environments, services, build targets, and deployment targets. Record shared definitions once, but consolidate effective connections, URLs, ports, directories, lifecycle commands, and credential references for each environment. Execution must not depend on reconstructing values across files. Trace fields to shared definitions or overrides; refresh affected environments when shared values change and retain verification status. Merge records, preserve manual notes, and avoid duplicate entries.
6. Execute recorded commands only when the current task requires them. Documentation is not authorization. Specify production/test targets explicitly; never fill local gaps with production settings or modify remote resources as a side effect of documentation work.

## Environment completeness

- Give each real environment a complete runbook, normally `environments/<environment-id>.md`, titled `# <Environment name> (<environment-id>)`, linked directly from the index. An existing single document with `## <Environment name>` sections can remain; do not maintain duplicate runbooks.
- Consolidate overview/access restrictions, hosts/SSH, SDKs, modules/endpoints, all actual dependency connections/authentication, directories/volumes, configuration/certificates, lifecycle/diagnostic commands, artifacts, deployment/rollback, verification, and gaps. Cover only actual dependencies; completeness does not authorize remote probing.
- Identify commands by object, environment, and execution location. List start, stop, restart, status, logs, and health checks separately for applications, databases, Redis, MQ, proxies, and other managed objects. Distinguish application restarts from shared infrastructure restarts. Record dependency order, graceful shutdown, cross-module impact, and known data effects. Mark unknown commands `To confirm`; deleting volumes, clearing databases, and `down -v` are not routine shutdowns.
- Connection tables must include username and password/credential fields. Use precise secure-store references, variable names, or local secrets anchors rather than omitting authentication. Explicitly unauthenticated services use `No authentication (source/status)`; blanks do not imply no password. Separate multiple accounts, read-only/admin users, Redis ACL users, and MQ business/console accounts.
- Fill gaps without changing the task goal or starting/restarting services. Ask only about unknowns affecting the current operation; list other gaps as `To confirm`.

## Credentials and local protection

- Normally record usernames, credential references (password-manager/Keychain entries, environment-variable names, existing key/certificate paths), injection methods, and purpose. Do not copy passwords, tokens, SSH private keys, signing keys, or kubeconfig contents into ordinary Markdown, `AGENTS.md`, ignore files, or replies. Replace password-bearing URLs with separate host/user fields and credential references.
- Using a user-provided password for an authorized task does not authorize plaintext persistence. Only on an explicit request for local plaintext storage, write `<records-dir>/secrets/<environment-id>.md` with directories `700` and files `600`; the index should say only that restricted local credentials exist. This is not encryption; prefer existing secure storage and do not duplicate values elsewhere.
- Use `700` for store/project directories and `600` for record files. Reject writes through symlinks. Keep existing private keys in their original protected locations. Never use `chmod -R` or follow links to change external permissions.
- Do not move sensitive records to the cloud or create external backups, telemetry, or synchronized copies.

## Project matching and legacy migration

Read [Storage and migration](references/storage.md) for initialization, resolution, migration failures, moved projects, or same-name project questions.

- The default store is `Path.home() / ".tim-env"`, independent of the skill installation. Project IDs are full SHA-256 hashes of resolved canonical root paths. Use the script output as the sole location authority; do not calculate or guess IDs. Never merge by name, Git remote, or branch. Distinct clones/worktrees are isolated.
- `resolve` only locates records. `init`/`migrate` create identity/index and copy, verify, then remove legacy `.tim-env`. On conflict, preserve both sides and stop affected releases until merged and retried. Reject links, special files, and identity mismatches.
- Keep records, migration backups, mapping JSON, and store links out of the project. External `project.json` records root/name, not possibly credential-bearing Git remotes. Relative document links remain valid; check old script paths and command working directories, and remove references to in-project `.tim-env`.
- A moved project has a new identity. Explicitly rebind only after checking the old path, destination, and user intent; matching names/remotes are insufficient. Path matching does not synchronize machines or clones.

## Git and release constraints

After initialization/migration and before release, run:

```sh
python3 <skill-dir>/scripts/tim_env.py check --root <project-root>
```

- Check external identity/permissions, legacy remnants, and the owning repository's index. Moving files does not clean the index or history. When authorized by the current request, remove only legacy `.tim-env` from the index with `git rm --cached`, preserve external records, and inspect staged changes. If rejected, inspect staging rather than blindly forcing. Do not automatically commit, rewrite history, or force-push. Report historical/remote exposure honestly and address required credential rotation.
- Preserve legacy `.gitignore`/`.dockerignore` exclusions as compatibility defenses. External storage does not require new projects to change these files. Migrate directories recreated by old versions rather than treating remnants as safe. Check nested projects against their actual owning repositories.
- The external store must be outside build/upload contexts; never build/upload the entire home directory. Inspect actual Docker contexts, additional contexts, Dockerfiles/specific ignore files, scripts, CI, COPY/ADD, mounts, rsync, FTP/SFTP, scp, tar/zip, and kubectl cp for explicit store copies. External placement alone cannot prevent deliberate copying.
- Put build artifacts and remotely executed scripts in existing project script locations. Inject credentials securely at runtime. Store scripts are local-only; never use the store as a Secret/ConfigMap, CI artifact, or release configuration input. Recheck cwd/relative paths after migration; do not create compatibility links inside the project.
- Run `python3 <skill-dir>/scripts/tim_env.py artifact --path <staging-directory-or-zip/tar>` on actual staging/archives. This checks `.tim-env` path components and links, not renamed copies, nested archives, or image layers. Review real copy sources too. Fix affected release steps if checks fail or copying cannot be ruled out; do not block unrelated local development.

## Completion report

Briefly state which records changed, the exclusion scope actually verified, and remaining critical gaps. Never repeat passwords or paste entire environment documents into chat. Do not claim persistent monitoring, guaranteed automatic loading, or that `.gitignore` alone guarantees release exclusion.
