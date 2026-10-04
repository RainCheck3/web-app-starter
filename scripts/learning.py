"""Local-only learning capture. Python 3.9+, standard library, no network calls."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

HOOK_MARKER = "# founder-learning-hook-v1"


def git(*args: str, required: bool = True) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if required and result.returncode:
        raise ValueError(result.stderr.strip() or "Git command failed.")
    return result.stdout.strip() if result.returncode == 0 else ""


def root() -> Path:
    return Path(git("rev-parse", "--show-toplevel")).resolve()


def notebook() -> tuple[Path, str]:
    location = git("config", "--local", "--get", "learning.notebook", required=False)
    project = git("config", "--local", "--get", "learning.project", required=False)
    if not location or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", project):
        raise ValueError("Learning capture is not configured. Run the setup command.")
    path = Path(location).expanduser().resolve()
    if path.is_relative_to(root()):
        raise ValueError("The private notebook must be outside the product repository.")
    return path, project


def write_new(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    except FileExistsError:
        pass


def setup(args: argparse.Namespace) -> None:
    repo = root()
    path = Path(args.notebook).expanduser().resolve()
    project = args.project or repo.name
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", project):
        raise ValueError(
            "Project ID must use letters, numbers, underscores, or hyphens."
        )
    if path.is_relative_to(repo):
        raise ValueError("The private notebook must be outside the product repository.")
    if not args.no_hook and git("config", "--get", "core.hooksPath", required=False):
        raise ValueError(
            "A hooks manager is configured. Run setup with --no-hook, then call "
            "'python3 scripts/learning.py record --kind commit' "
            "from its post-commit hook."
        )
    hook = Path(git("rev-parse", "--git-path", "hooks/post-commit")).resolve()
    if (
        not args.no_hook
        and hook.exists()
        and HOOK_MARKER not in hook.read_text(encoding="utf-8")
    ):
        raise ValueError(
            "An existing post-commit hook was found; it was not overwritten."
        )

    git("config", "--local", "learning.notebook", str(path))
    git("config", "--local", "learning.project", project)
    git("config", "--local", "learning.python", sys.executable)
    path.mkdir(parents=True, exist_ok=True)
    write_new(
        path / "README.md",
        "# Founder notebook\n\nPrivate local records. No automatic push.\n\n"
        "- `products/<project>/events/`: observed commits, builds, and checks.\n"
        "- `products/<project>/notes/`: engineering, product, and revenue learnings.\n"
        "- `weekly/`: reviews grounded in those records.\n"
        "- `playbook.md`: reusable lessons with evidence and limits.\n\n"
        "Builds and deployments are distinct. Demand needs customer evidence.\n"
        "Back up this folder or put it in a separate private repository.\n",
    )
    write_new(
        path / "direction.md",
        "# Direction\n\n- Available hours per week: unknown\n"
        "- Monthly spending limit: unknown\n- Income goal and date: unknown\n"
        "- Current product / audience: not selected\n"
        "- Next assumption to test: unknown\n",
    )
    write_new(
        path / "playbook.md",
        "# Playbook\n\nPromote lessons here only with evidence.\n"
        "Include scope, evidence links, confidence, and the proposed change.\n",
    )
    write_new(
        path / "products" / project / "overview.md",
        f"# {project}\n\n- Audience: unknown\n- Problem: unknown\n"
        "- Value proposition: unknown\n- Pricing hypothesis: unknown\n"
        "- Current experiment and success criteria: not defined\n",
    )
    registration = path / "products" / project / "project.json"
    registration.write_text(
        json.dumps({"project": project, "path": str(repo)}, indent=2) + "\n",
        encoding="utf-8",
    )
    if args.no_hook:
        print(
            f"Learning capture configured without hook: {path / 'products' / project}"
        )
        return
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(
        "#!/bin/sh\n" + HOOK_MARKER + "\n"
        "repo=$(git rev-parse --show-toplevel) || exit 0\n"
        f'{shlex.quote(sys.executable)} "$repo/scripts/learning.py" '
        'record --kind commit || printf "%s\\n" '
        '"Learning capture failed; commit was preserved." >&2\nexit 0\n',
        encoding="utf-8",
    )
    hook.chmod(0o755)
    print(f"Learning capture enabled: {path / 'products' / project}")


def capture(args: argparse.Namespace) -> None:
    path, project = notebook()
    now = datetime.now(timezone.utc)
    revision = git("rev-parse", "--verify", "HEAD", required=False) or "uncommitted"
    if args.kind == "commit" and revision == "uncommitted":
        raise ValueError("No commit exists yet.")
    if args.kind == "deployment" and not args.evidence:
        raise ValueError(
            "Deployment records require a verified URL or release reference."
        )
    record = {
        "recorded_at": now.isoformat(),
        "project": project,
        "kind": args.kind,
        "revision": revision,
        "working_tree_dirty": bool(git("status", "--porcelain")),
        "exit_code": args.exit_code,
        "evidence": args.evidence or "local command / Git hook",
    }
    if args.kind == "commit":
        record["subject"] = git("log", "-1", "--format=%s")
    event_id = (
        f"commit-{revision}"
        if args.kind == "commit"
        else f"{now.strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}"
    )
    destination = path / "products" / project / "events" / f"{event_id}.md"
    write_new(
        destination,
        f"# {args.kind.capitalize()} evidence\n\n```json\n"
        + json.dumps(record, indent=2)
        + "\n```\n\nObserved event only. Product and revenue impact are unknown.\n",
    )
    print(destination)


def note(args: argparse.Namespace) -> None:
    path, project = notebook()
    content = sys.stdin.read().strip()
    if not content:
        raise ValueError("Provide the learning note as Markdown on standard input.")
    now = datetime.now(timezone.utc)
    filename = f"{now.strftime('%Y%m%dT%H%M%S%fZ')}-{uuid.uuid4().hex[:8]}.md"
    destination = path / "products" / project / "notes" / filename
    write_new(
        destination,
        f"# {args.area.capitalize()} learning\n\nRecorded: {now.isoformat()}\n\n"
        + content
        + "\n",
    )
    print(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    configure = commands.add_parser("setup")
    configure.add_argument("--notebook", required=True)
    configure.add_argument("--project")
    configure.add_argument("--no-hook", action="store_true")
    configure.set_defaults(handler=setup)
    event = commands.add_parser("record")
    event.add_argument(
        "--kind", choices=["commit", "build", "check", "deployment"], required=True
    )
    event.add_argument("--exit-code", type=int, default=0)
    event.add_argument("--evidence")
    event.set_defaults(handler=capture)
    learning = commands.add_parser("note")
    learning.add_argument(
        "--area", choices=["engineering", "product", "revenue"], required=True
    )
    learning.set_defaults(handler=note)
    args = parser.parse_args()
    try:
        args.handler(args)
    except (ValueError, OSError) as error:
        print(f"Learning capture: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
