# External storage and migration (v2)

## Location and identity

Default location: `~/.tim-env/projects/<project-id>/`. The ID is the full hexadecimal SHA-256 of the canonical absolute project-root path. Let the script resolve it. The name in `project.json` is for display only, so identically named directories cannot accidentally share database or production settings.

- Establish the actual root from project context, Git root, or monorepo definitions. Do not treat arbitrary subdirectories as projects. Standalone non-Git projects are supported.
- `resolve` reports locations without creation or migration. Run `init` before each use; `migrate` is a compatibility alias for the same flow.
- Resolving paths maps symlink entry points to the same real project. Different clones/worktrees remain isolated to avoid mixing local paths/configuration. Branch changes preserve identity; note branch-specific versions/profiles in records.
- `project.json` contains `schema_version`, `canonical_root`, `display_name`, `project_id`, and `created_at`. Reject mismatches or nonempty directories missing identity rather than automatically claiming them.
- Do not use the home directory, a directory inside the store, or a directory containing the store as the root. Do not symlink the store into a project or shared synchronization directory.
- `--store <external-directory>` is for isolated tests or an explicitly requested storage location. Use the same option on every command; omit it for normal use. Its parent must already exist, and store/project directories must not contain each other.

```sh
python3 <skill-dir>/scripts/tim_env.py resolve --root <project-root>
python3 <skill-dir>/scripts/tim_env.py init --root <project-root>
python3 <skill-dir>/scripts/tim_env.py check --root <project-root>
```

Use the returned `records_dir/index.md`; relative document links are based on that directory. Code paths remain relative to the project root. Moving documentation must not change build-command working directories.

## Migration transaction and conflicts

The script checks only `.tim-env` directly under the specified project root, not other projects or credential stores.

1. Create the private store and identity; serialize helper writes with a store-level file lock.
2. Check source/destination types and ownership. Reject symbolic/hard links, special files, reserved identity-file conflicts, and permissive existing target records. Correct only relevant real paths, without recursively following links.
3. Compare relative paths, types, and file SHA-256. Identical files need no overwrite. On different contents or conflicting file/directory types, report paths and preserve both sides; do not choose a winner. A retained legacy directory means migration is incomplete and affected releases must stop.
4. Copy into a `700` temporary directory in the external store, using `600` files. Verify complete paths and hashes before merging; never print credentials.
5. Verify the destination and confirm the source has not changed before deleting the legacy directory. Failures preserve the source; identical external copies already written permit an idempotent retry. Do not edit legacy records concurrently with migration.
6. Leave no records, links, copies, or migration backups inside the project. Remove temporary copies afterward. Output only status, paths, and counts.
7. Check/handle tracked legacy paths, update the `AGENTS.md` managed block, and review script references, absolute links, and project-relative paths. The script does not rewrite document contents or execute migrated scripts.

Moving `.tim-env` does not remove Git history. Report affected paths and required follow-up without reading/printing historical passwords or rewriting history without authorization.

## Moving or renaming projects

A new path produces a new ID; matching names/remotes do not imply sharing. Before reusing records, verify the old `canonical_root` corresponds to the new project and is no longer used by another checkout. Rebind only on an explicit user request: retain old records until the new directory is verified file by file, merge existing destination records under the same conflict rules, and update `project.json` with the new root/ID/name while preserving creation time and noting the old path. The helper does not automate this procedure. Update local absolute paths and recheck SDKs/connections; old verification is not proof of the new environment.

There is no automatic cross-machine synchronization. Verify accounts, certificates, and endpoints against each machine's actual configuration.
