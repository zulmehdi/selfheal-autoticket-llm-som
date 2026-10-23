"""Retrieve and parse the architect's Markdown runbook knowledge."""

from pathlib import Path
import re


RUNBOOK_DIR = Path(__file__).resolve().parent.parent / "runbooks"


def load_runbooks(runbook_dir=RUNBOOK_DIR):
    catalog = {}
    paths = sorted(Path(runbook_dir).glob("*.md"))
    if not paths:
        raise ValueError(f"No Markdown runbooks found in {runbook_dir}")
    for path in paths:
        incident_type, entry = parse_runbook(path.read_text(encoding="utf-8"), path)
        if incident_type in catalog:
            raise ValueError(f"{path}: duplicate incident type {incident_type}")
        catalog[incident_type] = entry
    if "unknown" not in catalog:
        raise ValueError("Runbooks must include an 'unknown' incident type for fallback triage")
    return catalog


def parse_runbook(document, source):
    """Parse our Markdown template into the architect's JSON-compatible schema."""
    metadata = {}
    sections = {}
    section = None
    for line in document.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            if section in sections:
                raise ValueError(f"{source}: duplicate section {section}")
            sections[section] = []
        elif section is not None:
            sections[section].append(line)
        elif ":" in line and not line.startswith("#"):
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    required = ("Incident type", "Runbook ID", "Priority", "Action")
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        raise ValueError(f"{source}: missing metadata: {', '.join(missing)}")
    if metadata["Priority"] not in {"P1", "P2", "P3"}:
        raise ValueError(f"{source}: priority must be P1, P2, or P3")
    description = "\n".join(sections.get("When to use", [])).strip()
    steps = []
    for line in sections.get("Steps", []):
        if not line.strip():
            continue
        match = re.fullmatch(r"\s*\d+\.\s+(.+)", line)
        if not match:
            raise ValueError(f"{source}: each step must be a numbered Markdown list item")
        steps.append(match.group(1))
    if not description or not steps:
        raise ValueError(f"{source}: requires 'When to use' text and numbered 'Steps'")
    return metadata["Incident type"], {
        "description": description,
        "priority": metadata["Priority"],
        "runbook": {
            "id": metadata["Runbook ID"], "action": metadata["Action"],
            "steps": steps, "source": str(source),
            "context": {
                name: "\n".join(lines).strip()
                for name, lines in sections.items()
                if name not in {"When to use", "Steps"}
            },
            "validation_checks": [
                line.strip()[2:] for line in sections.get("Validation", [])
                if line.strip().startswith("- ")
            ],
        },
    }

