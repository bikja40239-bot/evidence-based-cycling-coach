"""Offline repository checks; these do not evaluate coaching effectiveness."""

from pathlib import Path
import os
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


SKILL_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/training.md",
    "references/nutrition-recovery.md",
    "references/creator-method.md",
    "references/evidence.md",
)
REPO_FILES = (
    "README.md", "CLAUDE.md", "AGENTS.md", "docs/maintenance.md",
    ".github/workflows/validate.yml", "requirements-dev.txt", ".gitignore",
    "scripts/validate_repository.py", "tests/test_validation.py",
)
LINK = re.compile(r"\]\(([^\s)]+)\)")
SOURCE = re.compile(r"\*\*([TNMGD]\d{2})｜")
CITATION = re.compile(r"\[([TNMGD]\d{2}(?:,[TNMGD]\d{2})*)\]")
PRIVATE = re.compile(
    r"(?:[A-Za-z]:[\\/]Users[\\/]|/Users/|/home/)|"
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"
)


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors = []
    texts = {}
    for name in SKILL_FILES + REPO_FILES:
        if not (root / name).is_file():
            errors.append(f"Missing file: {name}")

    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or path.suffix not in {".md", ".yaml", ".yml"}:
            continue
        if not path.is_file():
            continue
        name = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(f"Invalid UTF-8: {name}")
            continue
        texts[name] = text
        if "\ufffd" in text:
            errors.append(f"Replacement character: {name}")
        if PRIVATE.search(text):
            errors.append(f"Local path or credential: {name}")
        if path.suffix == ".md":
            for dest in LINK.findall(text):
                parsed = urlsplit(dest.strip("<>"))
                if parsed.scheme in {"https", "http", "mailto"}:
                    continue
                if parsed.scheme or parsed.netloc:
                    errors.append(f"Unsupported link: {name}: {dest}")
                    continue
                if not parsed.path:
                    continue  # This check validates file targets, not heading anchors.
                target = (path.parent / unquote(parsed.path)).resolve()
                if not target.is_relative_to(root) or not target.is_file():
                    errors.append(f"Broken local link: {name}: {dest}")

    entry = texts.get("SKILL.md", "")
    try:
        parts = entry.split("---", 2)
        if parts[0].strip() or len(parts) != 3:
            raise ValueError("missing frontmatter")
        metadata = yaml.safe_load(parts[1])
        if not isinstance(metadata, dict):
            raise ValueError("frontmatter must be a mapping")
        if metadata.get("name") != "evidence-based-cycling-coach":
            raise ValueError("unexpected skill name")
        if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
            raise ValueError("empty description")
    except (ValueError, yaml.YAMLError) as exc:
        errors.append(f"Invalid skill metadata: {exc}")

    try:
        ui = yaml.safe_load(texts.get("agents/openai.yaml", ""))
        interface = ui["interface"]
        short = interface["short_description"]
        prompt = interface["default_prompt"]
        if not isinstance(short, str) or not 25 <= len(short) <= 64:
            raise ValueError("short_description must have 25-64 characters")
        if not isinstance(prompt, str) or "$evidence-based-cycling-coach" not in prompt:
            raise ValueError("default prompt must invoke the skill")
    except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"Invalid UI metadata: {exc}")

    definitions = SOURCE.findall(texts.get("references/evidence.md", ""))
    defined = set(definitions)
    if len(definitions) != len(defined):
        errors.append("Duplicate evidence ID")
    if len(defined) != 32:
        errors.append(f"Expected 32 evidence IDs, found {len(defined)}")
    for name, text in texts.items():
        for group in CITATION.findall(text):
            for source in group.split(","):
                if source not in defined:
                    errors.append(f"Undefined evidence ID: {name}: {source}")

    agents = root / "AGENTS.md"
    if agents.is_symlink():
        if os.readlink(agents) != "CLAUDE.md":
            errors.append("AGENTS.md must link to CLAUDE.md")
    elif not (os.name == "nt" and texts.get("AGENTS.md", "").strip() == "CLAUDE.md"):
        errors.append("AGENTS.md must be a relative symlink to CLAUDE.md")
    rules = texts.get("CLAUDE.md", "")
    if len(rules.splitlines()) > 300 or len(rules.encode("utf-8")) > 15_000:
        errors.append("CLAUDE.md exceeds the rule-size budget")

    try:
        workflow = yaml.load(texts.get(".github/workflows/validate.yml", ""), Loader=yaml.BaseLoader)
        if not {"push", "pull_request"} <= set(workflow["on"]):
            raise ValueError("push and pull_request triggers are required")
        if workflow["permissions"] != {"contents": "read"}:
            raise ValueError("CI must use read-only contents permission")
    except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"Invalid CI configuration: {exc}")
    return errors


if __name__ == "__main__":
    problems = validate(Path(__file__).resolve().parents[1])
    if problems:
        print("\n".join(f"ERROR: {problem}" for problem in problems))
        sys.exit(1)
    print("PASS: Skill files, metadata, local links, 32 evidence IDs, privacy scan, rules and CI configuration")
