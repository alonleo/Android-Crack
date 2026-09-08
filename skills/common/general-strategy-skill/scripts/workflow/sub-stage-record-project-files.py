#!/usr/bin/env python3
"""Reverse-project stage: hash AS sources and record verified release identity.

Dependencies: Python 3, PyYAML, project environment and configured apksigner.
Inputs: NAME/TYPE project with source, signing key, release and patched.apk.
Outputs: output-project-manifest.yaml and dir-index.yaml in the project work dir.
Records evidence only; does not declare preceding stages or device acceptance.
"""
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from stage_runtime import atomic_write, contained, run_stage, sha256, verify_signature


def execute(ctx):
    for required in ("app/src/main/AndroidManifest.xml", "gradle/wrapper/gradle-wrapper.jar",
                     "gradle/wrapper/gradle-wrapper.properties", "my.keystore.jks"):
        ctx.project_path(required)
    for base, names in ((ctx.project_dir, ("settings.gradle", "settings.gradle.kts")),
                        (ctx.project_dir / "app", ("build.gradle", "build.gradle.kts"))):
        if not any((base / name).is_file() for name in names):
            raise ValueError(f"Gradle configuration missing in {base}")
    patched = ctx.project_path("patched.apk")
    release_dir = ctx.project_path("app/build/outputs/apk/release", False)
    releases = [p for p in release_dir.glob("*.apk") if p.is_file() and not p.is_symlink()]
    if len(releases) != 1 or not patched.stat().st_size:
        raise ValueError("Expected one release APK and a nonempty patched.apk")
    release = releases[0]
    digest = sha256(patched)
    if digest != sha256(release):
        raise ValueError("patched.apk differs from the project release APK")
    signature = verify_signature(patched)
    files = []
    for path in sorted(ctx.project_dir.rglob("*")):
        relative = path.relative_to(ctx.project_dir)
        if set(relative.parts) & {".git", ".gradle", "build", "__pycache__"}:
            continue
        if path.is_symlink():
            raise ValueError(f"Source inventory requires regular files, found symlink: {relative}")
        if path.is_file():
            checked = ctx.project_path(relative)
            files.append({"path": relative.as_posix(), "bytes": checked.stat().st_size, "sha256": sha256(checked)})
    manifest = {"schema_version": 1, "name": ctx.name, "type": ctx.type_name,
                "project": "project", "files": files,
                "release": {"path": release.relative_to(ctx.project_dir).as_posix(),
                            "sha256": digest, "signature": signature}, "accepted": False}
    manifest_path = contained(ctx.work_dir, "output-project-manifest.yaml", False)
    index_path = contained(ctx.work_dir, "dir-index.yaml", False)
    index = {}
    if index_path.is_file():
        original = index_path.read_text(encoding="utf-8")
        try:
            previous = yaml.safe_load(original)
        except yaml.YAMLError:
            previous = None
        index = previous if isinstance(previous, dict) else {"legacy_content": original}
    index.update(name=ctx.name, type=ctx.type_name)
    existing = index.get("entries", [])
    if not isinstance(existing, list) or any(not isinstance(item, dict) or not item.get("path") for item in existing):
        raise ValueError("Existing index entries must be a list of path records")
    entries = {entry["path"]: dict(entry) for entry in existing}
    for path in sorted(ctx.work_dir.iterdir()):
        if path.name == "dir-index.yaml":
            continue
        if path.is_symlink():
            raise ValueError(f"Unsafe project index entry: {path}")
        entries.setdefault(path.name, {}).update(path=path.name, kind="directory" if path.is_dir() else "file")
    entries.setdefault(manifest_path.name, {}).update(path=manifest_path.name, kind="file")
    index["entries"] = list(entries.values())
    atomic_write(manifest_path, yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False).encode("utf-8"))
    atomic_write(index_path, yaml.safe_dump(index, allow_unicode=True, sort_keys=False).encode("utf-8"))
    return {"manifest": str(manifest_path), "index": str(index_path),
            "source_file_count": len(files), "release_sha256": digest}


if __name__ == "__main__":
    raise SystemExit(run_stage("record-project-files", execute))
