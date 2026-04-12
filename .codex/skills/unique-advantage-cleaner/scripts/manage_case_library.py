from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


FORMAL_EMPTY = "\u5f53\u524d\u8fd8\u6ca1\u6709\u6b63\u5f0f\u8bb0\u5f55\u3002"
HYPOTHESIS_EMPTY = "\u5f53\u524d\u8fd8\u6ca1\u6709\u5047\u8bbe\u7ebf\u7d22\u3002"
REVIEW_EMPTY = "\u5f53\u524d\u8fd8\u6ca1\u6709\u590d\u76d8\u8bb0\u5f55\u3002"
NONE_TEXT = "(\u65e0)"
FORMAL_SECTION_TITLE = "## \u6b63\u5f0f\u6848\u4f8b\u533a"
HYPOTHESIS_SECTION_TITLE = "## \u5047\u8bbe\u7ebf\u7d22\u533a"
REVIEW_SECTION_TITLE = "## \u590d\u76d8\u8bb0\u5f55"
FORMAL_KIND_LABEL = "\u6b63\u5f0f\u6848\u4f8b"
HYPOTHESIS_KIND_LABEL = "\u5047\u8bbe\u7ebf\u7d22"


@dataclass
class Entry:
    kind: str
    entry_id: str
    title: str
    block: str


@dataclass
class Library:
    preamble: str
    formal_entries: list[Entry]
    hypothesis_entries: list[Entry]
    review_section: str


CASE_RE = re.compile(r"^## (?:Case|\u6b63\u5f0f\u6848\u4f8b) (\d{3}) - (.+)$")
HYPOTHESIS_RE = re.compile(r"^## (?:Hypothesis|\u5047\u8bbe\u7ebf\u7d22) (\d{3}) - (.+)$")
DATE_RE = re.compile(r"^- (?:Date|\u65e5\u671f): (.+)$")
SOURCE_RE = re.compile(r"^- (?:Source|\u6765\u6e90): (.+)$")
SUSTAINABILITY_RE = re.compile(r"^- (?:Sustainability score|\u957f\u671f\u53ef\u6301\u7eed\u6027\u8bc4\u5206): (\d+)$")
LEARNING_RE = re.compile(r"^- (?:Learning speed score|\u5b66\u4e60\u901f\u5ea6\u8bc4\u5206): (\d+)$")
EXTERNAL_RE = re.compile(r"^- (?:External validation score|\u5916\u90e8\u9a8c\u8bc1\u8bc4\u5206): (\d+)$")
JUDGMENT_RE = re.compile(r"^- (?:Preliminary judgment|\u521d\u6b65\u5224\u65ad): (.+)$")
STATUS_RE = re.compile(r"^- (?:Status|\u72b6\u6001): (.+)$")


def display_kind(kind: str) -> str:
    if kind == "case":
        return FORMAL_KIND_LABEL
    if kind == "hypothesis":
        return HYPOTHESIS_KIND_LABEL
    return kind


def display_id(kind: str, entry_id: str) -> str:
    return f"{display_kind(kind)}:{entry_id}"


def find_section_index(lines: list[str], candidates: list[str]) -> int:
    for candidate in candidates:
        if candidate in lines:
            return lines.index(candidate)
    raise ValueError(f"Missing section heading. Expected one of: {', '.join(candidates)}")


def parse_blocks(lines: list[str], pattern: re.Pattern[str], kind: str) -> list[Entry]:
    entries: list[Entry] = []
    current_start: int | None = None
    current_id = ""
    current_title = ""

    for index, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            if current_start is not None:
                block = "\n".join(lines[current_start:index]).strip()
                entries.append(Entry(kind=kind, entry_id=current_id, title=current_title, block=block))
            current_start = index
            current_id = match.group(1)
            current_title = match.group(2).strip()

    if current_start is not None:
        block = "\n".join(lines[current_start:]).strip()
        entries.append(Entry(kind=kind, entry_id=current_id, title=current_title, block=block))

    return entries


def parse_library(path: Path) -> Library:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    try:
        entries_index = find_section_index(lines, [FORMAL_SECTION_TITLE, "## Entries"])
        hypothesis_index = find_section_index(lines, [HYPOTHESIS_SECTION_TITLE, "## Hypothesis Notes"])
        review_index = find_section_index(lines, [REVIEW_SECTION_TITLE, "## Review Notes"])
    except ValueError as exc:
        raise SystemExit(f"Archive format is invalid: {exc}") from exc

    preamble = "\n".join(lines[: entries_index + 1]).rstrip()
    formal_lines = lines[entries_index + 1 : hypothesis_index]
    hypothesis_lines = lines[hypothesis_index + 1 : review_index]
    review_lines = lines[review_index:]

    formal_entries = parse_blocks(formal_lines, CASE_RE, "case")
    hypothesis_entries = parse_blocks(hypothesis_lines, HYPOTHESIS_RE, "hypothesis")
    review_section = "\n".join(review_lines).strip()
    if review_section in {"## Review Notes", REVIEW_SECTION_TITLE}:
        review_section = f"{REVIEW_SECTION_TITLE}\n\n{REVIEW_EMPTY}"

    return Library(
        preamble=preamble,
        formal_entries=formal_entries,
        hypothesis_entries=hypothesis_entries,
        review_section=review_section,
    )


def match_first(pattern: re.Pattern[str], text: str) -> str | None:
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return None


def build_index_data(library: Library, library_path: Path) -> dict:
    formal_cases = []
    for entry in library.formal_entries:
        formal_cases.append(
            {
                "id": f"case:{entry.entry_id}",
                "display_id": display_id("case", entry.entry_id),
                "number": entry.entry_id,
                "kind": "case",
                "kind_label": FORMAL_KIND_LABEL,
                "title": entry.title,
                "date": match_first(DATE_RE, entry.block),
                "source": match_first(SOURCE_RE, entry.block),
                "scores": {
                    "sustainability": int(match_first(SUSTAINABILITY_RE, entry.block) or 0),
                    "learning_speed": int(match_first(LEARNING_RE, entry.block) or 0),
                    "external_validation": int(match_first(EXTERNAL_RE, entry.block) or 0),
                },
                "preliminary_judgment": match_first(JUDGMENT_RE, entry.block),
            }
        )

    hypothesis_notes = []
    for entry in library.hypothesis_entries:
        hypothesis_notes.append(
            {
                "id": f"hypothesis:{entry.entry_id}",
                "display_id": display_id("hypothesis", entry.entry_id),
                "number": entry.entry_id,
                "kind": "hypothesis",
                "kind_label": HYPOTHESIS_KIND_LABEL,
                "title": entry.title,
                "date": match_first(DATE_RE, entry.block),
                "source": match_first(SOURCE_RE, entry.block),
                "status": match_first(STATUS_RE, entry.block),
            }
        )

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(library_path.as_posix()),
        "counts": {
            "formal": len(formal_cases),
            "hypothesis": len(hypothesis_notes),
        },
        "formal_cases": formal_cases,
        "hypothesis_notes": hypothesis_notes,
    }


def default_index_path(library_path: Path) -> Path:
    return library_path.with_name("case-index.json")


def write_index(index_path: Path, index_data: dict) -> None:
    index_path.write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_index(index_path: Path) -> dict:
    return json.loads(index_path.read_text(encoding="utf-8"))


def index_is_stale(library_path: Path, index_path: Path) -> bool:
    if not index_path.exists():
        return True
    return index_path.stat().st_mtime < library_path.stat().st_mtime


def sync_index(library_path: Path, index_path: Path, library: Library | None = None) -> dict:
    current_library = library or parse_library(library_path)
    index_data = build_index_data(current_library, library_path)
    write_index(index_path, index_data)
    return index_data


def render_library(library: Library) -> str:
    formal_body = "\n\n".join(entry.block for entry in library.formal_entries) if library.formal_entries else FORMAL_EMPTY
    hypothesis_body = (
        "\n\n".join(entry.block for entry in library.hypothesis_entries)
        if library.hypothesis_entries
        else HYPOTHESIS_EMPTY
    )

    return (
        f"{library.preamble}\n\n"
        f"{formal_body}\n\n"
        f"{HYPOTHESIS_SECTION_TITLE}\n\n"
        f"{hypothesis_body}\n\n"
        f"{library.review_section.rstrip()}\n"
    )


def print_list(library: Library) -> None:
    print("FORMAL CASES")
    if library.formal_entries:
        for entry in library.formal_entries:
            print(f"case:{entry.entry_id} | {entry.title}")
    else:
        print("(none)")

    print("")
    print("HYPOTHESIS NOTES")
    if library.hypothesis_entries:
        for entry in library.hypothesis_entries:
            print(f"hypothesis:{entry.entry_id} | {entry.title}")
    else:
        print("(none)")

    print("")
    print(f"COUNTS formal={len(library.formal_entries)} hypothesis={len(library.hypothesis_entries)}")


def print_index_list(index_data: dict) -> None:
    print(FORMAL_KIND_LABEL)
    formal_cases = index_data.get("formal_cases", [])
    if formal_cases:
        for entry in formal_cases:
            print(f"{entry.get('display_id', entry['id'])} | {entry['title']}")
    else:
        print(NONE_TEXT)

    print("")
    print(HYPOTHESIS_KIND_LABEL)
    hypothesis_notes = index_data.get("hypothesis_notes", [])
    if hypothesis_notes:
        for entry in hypothesis_notes:
            print(f"{entry.get('display_id', entry['id'])} | {entry['title']}")
    else:
        print(NONE_TEXT)

    print("")
    counts = index_data.get("counts", {})
    print(f"\u6570\u91cf {FORMAL_KIND_LABEL}={counts.get('formal', 0)} {HYPOTHESIS_KIND_LABEL}={counts.get('hypothesis', 0)}")


def normalize_targets(raw_targets: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in raw_targets:
        token = raw.strip().lower()
        token = token.replace(" ", "")
        token = token.replace("：", ":")
        if not token:
            continue
        if token in {"all", "\u5168\u90e8", "\u5168\u90e8\u6e05\u7a7a"}:
            normalized.append("all")
            continue
        if token in {"formal:all", "formalall", "\u6b63\u5f0f\u6848\u4f8b:all", "\u6b63\u5f0f\u6848\u4f8ball", "\u6b63\u5f0f\u6848\u4f8b\u5168\u90e8"}:
            normalized.append("formal:all")
            continue
        if token in {"hypothesis:all", "hypothesisall", "\u5047\u8bbe\u7ebf\u7d22:all", "\u5047\u8bbe\u7ebf\u7d22all", "\u5047\u8bbe\u7ebf\u7d22\u5168\u90e8"}:
            normalized.append("hypothesis:all")
            continue

        case_match = re.fullmatch(r"(?:case|\u6b63\u5f0f\u6848\u4f8b):?(\d{3})", token)
        if case_match:
            normalized.append(f"case:{case_match.group(1)}")
            continue

        hypothesis_match = re.fullmatch(r"(?:hypothesis|\u5047\u8bbe\u7ebf\u7d22):?(\d{3})", token)
        if hypothesis_match:
            normalized.append(f"hypothesis:{hypothesis_match.group(1)}")
            continue

        normalized.append(token)
    if not normalized:
        raise SystemExit("\u6ca1\u6709\u63d0\u4f9b\u5220\u9664\u76ee\u6807\u3002")
    return normalized


def delete_entries(library: Library, targets: list[str]) -> tuple[list[Entry], Library]:
    normalized = normalize_targets(targets)

    if "all" in normalized:
        removed = [*library.formal_entries, *library.hypothesis_entries]
        return removed, Library(library.preamble, [], [], library.review_section)

    remove_formal_all = "formal:all" in normalized
    remove_hypothesis_all = "hypothesis:all" in normalized

    requested_formal_ids = {
        token.split(":", 1)[1]
        for token in normalized
        if token.startswith("case:")
    }
    requested_hypothesis_ids = {
        token.split(":", 1)[1]
        for token in normalized
        if token.startswith("hypothesis:")
    }

    known_formal_ids = {entry.entry_id for entry in library.formal_entries}
    known_hypothesis_ids = {entry.entry_id for entry in library.hypothesis_entries}

    missing_formal = sorted(requested_formal_ids - known_formal_ids)
    missing_hypothesis = sorted(requested_hypothesis_ids - known_hypothesis_ids)
    if missing_formal or missing_hypothesis:
        messages = []
        if missing_formal:
            messages.append("\u7f3a\u5c11\u6b63\u5f0f\u6848\u4f8b\u7f16\u53f7: " + ", ".join(missing_formal))
        if missing_hypothesis:
            messages.append("\u7f3a\u5c11\u5047\u8bbe\u7ebf\u7d22\u7f16\u53f7: " + ", ".join(missing_hypothesis))
        raise SystemExit("; ".join(messages))

    removed: list[Entry] = []
    remaining_formal: list[Entry] = []
    remaining_hypothesis: list[Entry] = []

    for entry in library.formal_entries:
        if remove_formal_all or entry.entry_id in requested_formal_ids:
            removed.append(entry)
        else:
            remaining_formal.append(entry)

    for entry in library.hypothesis_entries:
        if remove_hypothesis_all or entry.entry_id in requested_hypothesis_ids:
            removed.append(entry)
        else:
            remaining_hypothesis.append(entry)

    return removed, Library(
        preamble=library.preamble,
        formal_entries=remaining_formal,
        hypothesis_entries=remaining_hypothesis,
        review_section=library.review_section,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="\u5217\u51fa\u6216\u6e05\u7406\u72ec\u7279\u4f18\u52bf\u6848\u4f8b\u5e93\u3002")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--file", required=True, help="strength-system/case-library.md \u7684\u8def\u5f84")
    list_parser.add_argument("--index", help="strength-system/case-index.json \u7684\u8def\u5f84")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--file", required=True, help="strength-system/case-library.md \u7684\u8def\u5f84")
    delete_parser.add_argument("--index", help="strength-system/case-index.json \u7684\u8def\u5f84")
    delete_parser.add_argument("--target", action="append", required=True, help="\u5220\u9664\u76ee\u6807")

    reindex_parser = subparsers.add_parser("reindex")
    reindex_parser.add_argument("--file", required=True, help="strength-system/case-library.md \u7684\u8def\u5f84")
    reindex_parser.add_argument("--index", help="strength-system/case-index.json \u7684\u8def\u5f84")

    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args()
    path = Path(args.file).resolve()
    if not path.exists():
        raise SystemExit(f"\u6ca1\u6709\u627e\u5230\u6848\u4f8b\u5e93: {path}")
    index_path = Path(args.index).resolve() if getattr(args, "index", None) else default_index_path(path)

    if args.command == "list":
        if index_is_stale(path, index_path):
            sync_index(path, index_path)
        print_index_list(read_index(index_path))
        return 0

    library = parse_library(path)

    if args.command == "reindex":
        index_data = sync_index(path, index_path, library)
        counts = index_data["counts"]
        print("\u7d22\u5f15\u5df2\u66f4\u65b0")
        print(f"{FORMAL_KIND_LABEL}={counts['formal']} {HYPOTHESIS_KIND_LABEL}={counts['hypothesis']}")
        return 0

    if args.command == "delete":
        removed, updated = delete_entries(library, args.target)
        path.write_text(render_library(updated), encoding="utf-8")
        sync_index(path, index_path, updated)
        print("\u5df2\u5220\u9664")
        if removed:
            for entry in removed:
                print(f"{display_id(entry.kind, entry.entry_id)} | {entry.title}")
        else:
            print(NONE_TEXT)
        print("")
        print(
            f"\u6570\u91cf {FORMAL_KIND_LABEL}={len(updated.formal_entries)} "
            f"{HYPOTHESIS_KIND_LABEL}={len(updated.hypothesis_entries)}"
        )
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
