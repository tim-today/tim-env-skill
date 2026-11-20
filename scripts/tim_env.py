#!/usr/bin/env python3
"""User-scoped project records with verified legacy migration. No network access."""
import argparse
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile


def plain(path, directory=False):
    if path.is_symlink():
        raise ValueError(f'Refusing symbolic link: {path}')
    if path.exists() and not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f'Unexpected path type: {path}')
    if path.exists() and not directory and path.stat().st_nlink > 1:
        raise ValueError(f'Refusing hard link: {path}')


def root_path(root):
    root = Path(os.path.normcase(str(Path(root).resolve(strict=True))))
    if not root.is_dir():
        raise ValueError('root must be a directory')
    return root


def location(root, store=None):
    root = root_path(root)
    base = Path(store).expanduser().absolute() if store else Path.home() / '.tim-env'
    # Never follow a link in the store path or place private records in this project.
    for part in [*reversed(base.parents), base]:
        if part.is_symlink():
            raise ValueError(f'Store path contains a symbolic link: {part}')
    base = base.resolve()
    if base == root or root in base.parents or base in root.parents:
        raise ValueError('Store and project directories must not contain each other; the home directory cannot be the project root')
    project_id = hashlib.sha256(os.fsencode(str(root))).hexdigest()
    return root, base, base / 'projects' / project_id


def secure_dir(path):
    plain(path, directory=True)
    path.mkdir(mode=0o700, parents=False, exist_ok=True)
    if path.stat().st_uid != os.getuid():
        raise ValueError(f'Records directory is not owned by the current user: {path}')
    path.chmod(0o700)


def write_new(path, data):
    plain(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def manifest(path, strict_permissions=False):
    plain(path, directory=True)
    result = {}
    if not path.is_dir():
        raise ValueError(f'Directory does not exist: {path}')
    def visit(item):
        rel = item.relative_to(path).as_posix()
        info = item.lstat()
        if info.st_uid != os.getuid():
            raise ValueError(f'Record is not owned by the current user: {rel}')
        if strict_permissions and info.st_mode & 0o077:
            raise ValueError(f'Permissions must restrict access to the current user: {rel}')
        if stat.S_ISDIR(info.st_mode):
            result[rel] = ('dir', '')
            for child in sorted(item.iterdir()):
                visit(child)
        elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
            digest = hashlib.sha256()
            with item.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            result[rel] = ('file', digest.hexdigest())
        else:
            raise ValueError(f'Refusing link or special file: {rel}')
    visit(path)
    return result


def identity(root, target):
    metadata = target / 'project.json'
    plain(metadata)
    if metadata.exists():
        value = json.loads(metadata.read_text(encoding='utf-8'))
        if (value.get('schema_version') != 2 or value.get('canonical_root') != str(root)
                or value.get('project_id') != target.name):
            raise ValueError('project.json identity mismatch; never merge automatically by project name or remote')
    elif any(target.iterdir()):
        raise ValueError('Nonempty records directory lacks identity; verify ownership rather than claiming it automatically')


def tracked(root):
    try:
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'], capture_output=True)
    except FileNotFoundError:
        return [], 'Git is unavailable'
    if result.returncode:
        return [], 'Not a Git project'
    top = Path(os.fsdecode(result.stdout).strip()).resolve()
    relative = (root / '.tim-env').relative_to(top).as_posix()
    result = subprocess.run(['git', '-C', str(top), 'ls-files', '-z', '--', relative], capture_output=True)
    if result.returncode:
        raise ValueError('Cannot inspect the Git index')
    return [os.fsdecode(p) for p in result.stdout.split(b'\0') if p], 'Checked the actual owning Git repository'


def migrate(root, target):
    source = root / '.tim-env'
    if not source.exists() and not source.is_symlink():
        return {'status': 'absent'}
    before = manifest(source)
    # Source is copied as opaque bytes; never print or rewrite credentials or scripts.
    if 'project.json' in before:
        raise ValueError('Legacy directory contains reserved project.json; source preserved, manual merge required')
    current = manifest(target, strict_permissions=True)
    conflicts = [name for name, value in before.items()
                 if name != '.' and name in current and current[name] != value]
    if conflicts:
        return {'status': 'conflict', 'paths': conflicts,
                'action': 'Both sides preserved; resolve the merge before retrying migration; do not continue the release'}
    stage = Path(tempfile.mkdtemp(prefix='.migration-', dir=target.parent))
    try:
        # Fully copy and verify into a private sibling before touching destination.
        for name, (kind, _) in before.items():
            if name == '.':
                continue
            dest = stage / name
            if kind == 'dir':
                secure_dir(dest)
            else:
                write_new(dest, (source / name).read_bytes())
        if manifest(stage, strict_permissions=True) != before:
            raise ValueError('Migration staging verification failed; original directory preserved')
        for name, (kind, _) in before.items():
            if name == '.':
                continue
            dest = target / name
            if kind == 'dir':
                secure_dir(dest)
            elif not dest.exists():
                # Atomic move of a verified file; lock serializes all helper writes.
                plain(dest)
                os.rename(stage / name, dest)
        after = manifest(target, strict_permissions=True)
        if any(after.get(name) != value for name, value in before.items()):
            raise ValueError('Destination verification failed; original directory preserved')
        if manifest(source) != before:
            raise ValueError('Legacy records changed during migration; source preserved, merge and retry')
        shutil.rmtree(source)
        return {'status': 'migrated', 'files': sum(v[0] == 'file' for v in before.values()),
                'verified': 'File SHA-256 and complete relative paths verified; legacy directory removed'}
    finally:
        shutil.rmtree(stage)


@contextlib.contextmanager
def store_lock(base):
    # Parent is normally the existing user home; custom store is for isolated tests.
    if not base.parent.is_dir():
        raise ValueError('Store parent directory must already exist')
    secure_dir(base)
    lock = base / '.lock'
    plain(lock)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def init(root, store=None):
    root, base, target = location(root, store)
    with store_lock(base):
        secure_dir(base / 'projects')
        secure_dir(target)
        identity(root, target)
        metadata = target / 'project.json'
        if not metadata.exists():
            value = {'schema_version': 2, 'canonical_root': str(root), 'display_name': root.name,
                     'project_id': target.name, 'created_at': datetime.datetime.now().astimezone().isoformat()}
            write_new(metadata, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())
        manifest(target, strict_permissions=True)
        migration = migrate(root, target)
        if migration['status'] == 'conflict':
            return {'ok': False, 'records_dir': str(target), 'migration': migration}
        index = target / 'index.md'
        if not index.exists():
            content = ('# Project environment index\n\n'
                       f'Updated: {datetime.date.today().isoformat()}\nProject root: {root}\n\n'
                       '| Topic | File | Applicable modules / environments |\n| --- | --- | --- |\n\n'
                       '## Environments\n\n| Environment ID | Complete runbook | Modules | Status |\n| --- | --- | --- | --- |\n\n'
                       '## To confirm\n\n| Item | Impact | Information needed |\n| --- | --- | --- |\n')
            write_new(index, content.encode())
        result = check(root, store)
        result['migration'] = migration
        return result


def check(root, store=None):
    root, base, target = location(root, store)
    issues = []
    for parent in (base, base / 'projects'):
        plain(parent, directory=True)
        if parent.exists():
            info = parent.stat()
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                issues.append(f'Invalid store parent ownership or permissions: {parent}')
    if target.exists():
        manifest(target, strict_permissions=True)
        if not (target / 'project.json').is_file():
            issues.append('Missing project.json')
        else:
            identity(root, target)
        if not (target / 'index.md').is_file():
            issues.append('Missing index.md')
    else:
        issues.append('Missing external records directory; run init first')
    if (root / '.tim-env').exists() or (root / '.tim-env').is_symlink():
        issues.append('Legacy .tim-env remains inside the project; run init and resolve migration conflicts first')
    found, note = tracked(root)
    issues.extend(f'Git index still tracks legacy records: {name}' for name in found)
    return {'ok': not issues, 'root': str(root), 'records_dir': str(target),
            'index': str(target / 'index.md'), 'git': note, 'issues': issues,
            'scope': 'External identity/permissions, legacy remnants, Git index; separately review historical exposure and scripts/artifacts copying external records'}


def forbidden(name):
    # Check both separators for archives built on different operating systems.
    return '.tim-env' in PurePosixPath(name.replace('\\', '/')).parts


def artifact(path):
    plain(path, directory=path.is_dir())
    if not path.exists():
        raise ValueError('Artifact path does not exist')
    issues = []
    if path.is_dir():
        if forbidden(path.name):
            issues.append('Artifact directory itself is .tim-env')
        for parent, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                item = Path(parent) / name
                rel = item.relative_to(path).as_posix()
                if forbidden(rel):
                    issues.append(f'Contains a local records path: {rel}')
                if item.is_symlink():
                    issues.append(f'Artifact contains a link; review upload expansion behavior: {rel}')
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for item in archive.infolist():
                if forbidden(item.filename):
                    issues.append(f'Archive contains a local records path: {item.filename}')
                if stat.S_ISLNK(item.external_attr >> 16):
                    issues.append(f'Archive contains a link; review actual contents: {item.filename}')
    elif tarfile.is_tarfile(path):
        with tarfile.open(path) as archive:
            for item in archive:
                if forbidden(item.name) or (item.linkname and forbidden(item.linkname)):
                    issues.append(f'Archive contains a local records path: {item.name}')
                if item.issym() or item.islnk():
                    issues.append(f'Archive contains a link; review actual contents: {item.name}')
    else:
        raise ValueError('Only staging directories, ZIP formats such as zip/APK/AAB/JAR, and tar archives are supported; unknown formats do not pass')
    return {'ok': not issues, 'path': str(path), 'issues': issues,
            'scope': 'Member paths and links only; does not inspect renamed record copies, nested archive contents, or image layers'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('resolve', 'init', 'migrate', 'check'):
        entry = sub.add_parser(name)
        entry.add_argument('--root', type=Path, required=True)
        entry.add_argument('--store', type=Path, help='Explicit external store (default ~/.tim-env); for tests or a user-specified location')
    sub.add_parser('artifact').add_argument('--path', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'artifact':
            result = artifact(args.path.absolute())
        elif args.command == 'resolve':
            root, base, target = location(args.root, args.store)
            result = {'ok': True, 'root': str(root), 'records_dir': str(target),
                      'index': str(target / 'index.md'), 'exists': target.exists()}
        else:
            result = check(args.root, args.store) if args.command == 'check' else init(args.root, args.store)
    except (ValueError, OSError, UnicodeError, zipfile.BadZipFile, tarfile.TarError) as exc:
        result = {'ok': False, 'error': str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
