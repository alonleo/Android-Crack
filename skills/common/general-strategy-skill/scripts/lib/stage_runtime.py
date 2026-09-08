"""Reverse-project runtime for plan-driven public workers.

Dependencies: Python 3, PyYAML, the repository common library, and project-local
Android tools for execution. Library imports do not execute tools. The CLI loads
the repository environment before work and leaves final acceptance to the Agent.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import zipfile

import yaml

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "skills/common/scripts/lib"))
import common


def contained(base: Path, relative: str | Path, must_exist: bool = True) -> Path:
    base = base.resolve()
    relative = Path(relative)
    if relative.is_absolute() or relative.drive or ".." in relative.parts:
        raise ValueError(f"Expected a contained relative path: {relative}")
    target = (base / relative).resolve()
    if not target.is_relative_to(base) or target == base:
        raise ValueError(f"Path escapes or names the input root: {relative}")
    if must_exist and not target.is_file():
        raise FileNotFoundError(f"Input file missing: {target}")
    return target


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class StageContext:
    repo: Path
    name: str
    type_name: str
    stage: str
    plan_override: Path | None = None

    def __post_init__(self):
        for value in (self.name, self.type_name, self.stage):
            if not value or not re.fullmatch(r"[\w.-]+", value) or value in {".", ".."}:
                raise ValueError(f"Invalid project/type/stage name: {value!r}")

    @property
    def work_dir(self) -> Path:
        return contained(Path(self.repo), Path("crackings") / self.type_name / self.name, False)

    @property
    def project_dir(self) -> Path:
        return contained(self.work_dir, "project", False)

    @property
    def output_dir(self) -> Path:
        tables = [
            Path(self.repo) / f"skills/strategy/{self.type_name}-strategy-skill/stages/sub-stage-register.yaml",
            Path(self.repo) / "skills/common/general-strategy-skill/stages/sub-stage-register.yaml",
        ]
        for table in tables:
            if not table.is_file():
                continue
            data = yaml.safe_load(table.read_text(encoding="utf-8")) or {}
            for entry in data.get("sub_stages", []):
                if entry.get("name") == self.stage:
                    number = str(entry["id"]).zfill(2)
                    return contained(self.work_dir, f"stages/{number}-{self.stage}", False)
        raise ValueError(f"Stage not registered: {self.stage}")

    @property
    def plan_path(self) -> Path:
        if self.plan_override is not None:
            path = Path(self.plan_override)
            if path.is_absolute():
                path = path.resolve().relative_to(self.work_dir)
            return contained(self.work_dir, path, False)
        return contained(self.work_dir, f"plans/{self.stage}.json", False)

    def load_plan(self) -> dict:
        data = json.loads(self.plan_path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict) or not data:
            raise ValueError("A nonempty JSON plan object is required")
        return data

    def project_path(self, relative, must_exist=True) -> Path:
        return contained(self.project_dir, relative, must_exist)

    def input_path(self, relative) -> Path:
        return contained(self.work_dir, relative)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing")
    if temporary.is_symlink():
        raise ValueError(f"Unsafe temporary path: {temporary}")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary.is_file():
            temporary.unlink()


def write_report(ctx: StageContext, result: dict) -> Path:
    document = {**result, "stage": ctx.stage, "name": ctx.name, "type": ctx.type_name,
                "accepted": False, "recorded_at": datetime.now(timezone.utc).isoformat()}
    path = contained(ctx.output_dir, "execution-report.json", False)
    atomic_write(path, json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8"))
    return path


def write_failure(ctx: StageContext, reason: str) -> None:
    path = contained(ctx.work_dir, "status.yaml", False)
    state = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {}
    if not isinstance(state, dict):
        raise ValueError("status.yaml must contain an object")
    state["current_stage"] = ctx.stage
    failed = state.setdefault("failed_stages", [])
    if isinstance(failed, dict):
        failed[ctx.stage] = {"reason": reason}
    elif isinstance(failed, list):
        if ctx.stage not in failed:
            failed.append(ctx.stage)
    else:
        raise ValueError("failed_stages must be a list or object")
    reasons = state.setdefault("stage_failure_reasons", {})
    if not isinstance(reasons, dict):
        raise ValueError("stage_failure_reasons must be an object")
    reasons[ctx.stage] = reason
    completed = state.get("completed_stages")
    if isinstance(completed, list):
        state["completed_stages"] = [s for s in completed if s != ctx.stage and
                                      not (isinstance(s, dict) and s.get("name") == ctx.stage)]
    elif isinstance(completed, dict):
        completed.pop(ctx.stage, None)
    atomic_write(path, yaml.safe_dump(state, allow_unicode=True, sort_keys=False).encode("utf-8"))


def tool_command(variable: str, resolver) -> list[str]:
    """Resolve only explicitly configured tools; do not silently use PATH copies."""
    if not os.environ.get(variable):
        raise ValueError(f"Project environment variable {variable} is required")
    common._tool_cache.pop(variable, None)
    path = Path(resolver()).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Configured {variable} missing: {path}")
    if path.suffix.lower() == ".jar":
        return [str(java_path()), "-jar", str(path)]
    return [str(path)]


def java_path() -> Path:
    home = os.environ.get("JAVA_HOME")
    if not home:
        raise ValueError("Project JAVA_HOME is required")
    path = Path(home) / "bin" / ("java.exe" if os.name == "nt" else "java")
    if not path.is_file():
        raise FileNotFoundError(f"Project Java missing: {path}")
    return path


def verify_signature(apk: Path) -> dict:
    command = tool_command("APKSIGNER", common.apksigner)
    result = subprocess.run([*command, "verify", "--verbose", str(apk)],
                            capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise ValueError(f"APK signature verification failed: {result.stderr or result.stdout}")
    for version in (1, 2, 3):
        if not re.search(rf"Verified using v{version} scheme[^\r\n]*:\s*true", result.stdout, re.I):
            raise ValueError(f"Required v{version} signature missing")
    return {"v1": True, "v2": True, "v3": True}


def build_project(ctx: StageContext) -> dict:
    """Rebuild project-controlled inputs, verify signing, then publish that APK."""
    java = java_path()
    wrapper = ctx.project_path("gradle/wrapper/gradle-wrapper.jar")
    ctx.project_path("gradle/wrapper/gradle-wrapper.properties")
    ctx.project_path("app/src/main/AndroidManifest.xml")
    ctx.project_path("my.keystore.jks")
    if not any((ctx.project_dir / name).is_file() for name in ("settings.gradle", "settings.gradle.kts")):
        raise ValueError("Android Studio project settings are missing")
    if not any((ctx.project_dir / "app" / name).is_file() for name in ("build.gradle", "build.gradle.kts")):
        raise ValueError("App Gradle configuration is missing")
    tool_command("APKSIGNER", common.apksigner)
    ctx.output_dir.mkdir(parents=True, exist_ok=True)
    log = contained(ctx.output_dir, "build.log", False)
    command = [str(java), "-classpath", str(wrapper), "org.gradle.wrapper.GradleWrapperMain",
               "--no-daemon", ":app:clean", ":app:assembleRelease"]
    started = time.time_ns()
    common.log_step(f"{ctx.stage}: release build")
    with log.open("wb") as output:
        result = subprocess.run(command, cwd=ctx.project_dir, stdout=output,
                                stderr=subprocess.STDOUT, timeout=900)
    if result.returncode:
        raise ValueError(f"Release build failed ({result.returncode}); see {log}")
    release_dir = ctx.project_path("app/build/outputs/apk/release", False)
    apks = [p for p in release_dir.glob("*.apk") if p.is_file() and not p.is_symlink()]
    if len(apks) != 1:
        raise ValueError(f"Expected one release APK, found {len(apks)}; split/multi-output builds require a type implementation")
    release = apks[0]
    if not release.stat().st_size or release.stat().st_mtime_ns < started - 2_000_000_000:
        raise ValueError("Release APK is empty or stale")
    with zipfile.ZipFile(release) as archive:
        if "AndroidManifest.xml" not in archive.namelist() or archive.testzip() is not None:
            raise ValueError("Release APK archive is invalid")
    signatures = verify_signature(release)
    patched = ctx.project_path("patched.apk", False)
    atomic_write(patched, release.read_bytes())
    digest = sha256(release)
    if sha256(patched) != digest:
        raise ValueError("Delivered APK differs from release output")
    return {"release_apk": str(release), "patched_apk": str(patched), "sha256": digest,
            "signature": signatures, "build_log": str(log)}


def run_stage(stage: str, handler, argv=None) -> int:
    parser = argparse.ArgumentParser(description=f"Execute the public {stage} stage using project inputs")
    parser.add_argument("--name", default=os.environ.get("NAME"))
    parser.add_argument("--type", default=os.environ.get("TYPE"), dest="type_name")
    parser.add_argument("--plan", type=Path)
    args = parser.parse_args(argv)
    ctx = None
    try:
        ctx = StageContext(REPO, args.name or "", args.type_name or "", stage, args.plan)
        if not ctx.project_dir.is_dir():
            raise FileNotFoundError(f"Project missing: {ctx.project_dir}")
        if not (ctx.repo / "tools/environments/env.sh").is_file():
            raise FileNotFoundError("Project tools/environments/env.sh is missing")
        common._REPO_ROOT = ctx.repo
        common.ensure_env()
        common.log_step(stage)
        result = handler(ctx)
        if not isinstance(result, dict) or not result:
            raise ValueError("Stage returned no execution evidence")
        report = write_report(ctx, {"result": "executed", "details": result})
        common.log_success(f"Execution evidence written; Agent acceptance required: {report}")
        print(json.dumps({"result": "executed", "accepted": False, "report": str(report)}, ensure_ascii=False))
        return 0
    except (Exception, SystemExit) as error:
        common.log_error(str(error))
        if ctx is not None and ctx.work_dir.is_dir():
            try:
                write_report(ctx, {"result": "failed", "error": str(error)})
                write_failure(ctx, str(error))
            except Exception as record_error:
                common.log_error(f"Cannot record failure: {record_error}")
        return 1
