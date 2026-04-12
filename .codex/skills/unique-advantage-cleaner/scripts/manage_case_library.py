from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


FORMAL_EMPTY = "当前还没有正式记录。"
HYPOTHESIS_EMPTY = "当前还没有假设线索。"
REVIEW_EMPTY = "当前还没有复盘记录。"
NONE_TEXT = "(无)"
FORMAL_KIND_LABEL = "正式案例"
HYPOTHESIS_KIND_LABEL = "假设线索"
REVIEW_SECTION_TITLE = "## 复盘记录"
OVERVIEW_TITLE = "# 独特优势案例总览"
CASES_DIRNAME = "cases"
HYPOTHESES_DIRNAME = "hypotheses"
REVIEWS_FILENAME = "reviews.md"
OVERVIEW_FILENAME = "case-library.md"
INDEX_FILENAME = "case-index.json"
LEGACY_FORMAL_SECTION_TITLE = "## 正式案例区"
LEGACY_HYPOTHESIS_SECTION_TITLE = "## 假设线索区"
LEGACY_REVIEW_SECTION_TITLE = "## 复盘记录"


@dataclass
class Entry:
    kind: str
    entry_id: str
    title: str
    block: str
    path: Path


@dataclass
class Archive:
    root: Path
    formal_entries: list[Entry]
    hypothesis_entries: list[Entry]
    reviews_text: str


@dataclass
class LegacyLibrary:
    formal_entries: list[Entry]
    hypothesis_entries: list[Entry]
    review_section: str


CASE_RE = re.compile(r"^## (?:Case|正式案例) (\d{3}) - (.+)$")
HYPOTHESIS_RE = re.compile(r"^## (?:Hypothesis|假设线索) (\d{3}) - (.+)$")
DATE_RE = re.compile(r"^- (?:Date|日期): (.+)$")
SOURCE_RE = re.compile(r"^- (?:Source|来源): (.+)$")
SUSTAINABILITY_RE = re.compile(r"^- (?:Sustainability score|长期可持续性评分): (\d+)$")
LEARNING_RE = re.compile(r"^- (?:Learning speed score|学习速度评分): (\d+)$")
EXTERNAL_RE = re.compile(r"^- (?:External validation score|外部验证评分): (\d+)$")
JUDGMENT_RE = re.compile(r"^- (?:Preliminary judgment|初步判断): (.+)$")
STATUS_RE = re.compile(r"^- (?:Status|状态): (.+)$")


def display_kind(kind: str) -> str:
    if kind == "case":
        return FORMAL_KIND_LABEL
    if kind == "hypothesis":
        return HYPOTHESIS_KIND_LABEL
    return kind


def display_id(kind: str, entry_id: str) -> str:
    return f"{display_kind(kind)}:{entry_id}"


def root_path(root: Path | None, file_path: str | None) -> Path:
    if root is not None:
        return root.resolve()
    if file_path:
        return Path(file_path).resolve().parent
    raise SystemExit("请提供 --root 或 --file。")


def cases_dir(root: Path) -> Path:
    return root / CASES_DIRNAME


def hypotheses_dir(root: Path) -> Path:
    return root / HYPOTHESES_DIRNAME


def reviews_path(root: Path) -> Path:
    return root / REVIEWS_FILENAME


def overview_path(root: Path) -> Path:
    return root / OVERVIEW_FILENAME


def default_index_path(root: Path) -> Path:
    return root / INDEX_FILENAME


def default_reviews_text() -> str:
    return f"{REVIEW_SECTION_TITLE}\n\n{REVIEW_EMPTY}\n"


def is_default_review_text(text: str) -> bool:
    normalized = text.strip()
    return normalized in {REVIEW_SECTION_TITLE, default_reviews_text().strip()}


def match_first(pattern: re.Pattern[str], text: str) -> str | None:
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return None


def relative_posix(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def first_nonempty_line(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def parse_entry_file(path: Path, pattern: re.Pattern[str], kind: str) -> Entry:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"条目文件为空: {path}")
    header = first_nonempty_line(text)
    if header is None:
        raise SystemExit(f"条目文件为空: {path}")
    match = pattern.match(header)
    if not match:
        raise SystemExit(f"条目文件格式无效: {path}")
    return Entry(
        kind=kind,
        entry_id=match.group(1),
        title=match.group(2).strip(),
        block=text,
        path=path,
    )


def ensure_unique_ids(entries: list[Entry], kind: str) -> None:
    seen: dict[str, Path] = {}
    for entry in entries:
        if entry.entry_id in seen:
            raise SystemExit(
                f"{display_kind(kind)} 编号重复: {entry.entry_id} ({seen[entry.entry_id]} 和 {entry.path})"
            )
        seen[entry.entry_id] = entry.path


def load_entries(root: Path, directory_name: str, pattern: re.Pattern[str], kind: str) -> list[Entry]:
    directory = root / directory_name
    if not directory.exists():
        return []
    entries = [parse_entry_file(path, pattern, kind) for path in sorted(directory.glob("*.md"))]
    entries.sort(key=lambda entry: entry.entry_id)
    ensure_unique_ids(entries, kind)
    return entries


def read_reviews(root: Path) -> str:
    path = reviews_path(root)
    if not path.exists():
        return default_reviews_text().strip()
    text = path.read_text(encoding="utf-8").strip()
    return text or default_reviews_text().strip()


def ensure_archive_layout(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    cases_dir(root).mkdir(parents=True, exist_ok=True)
    hypotheses_dir(root).mkdir(parents=True, exist_ok=True)
    if not reviews_path(root).exists():
        reviews_path(root).write_text(default_reviews_text(), encoding="utf-8")


def parse_archive(root: Path) -> Archive:
    if not root.exists():
        raise SystemExit(f"没有找到档案目录: {root}")
    return Archive(
        root=root,
        formal_entries=load_entries(root, CASES_DIRNAME, CASE_RE, "case"),
        hypothesis_entries=load_entries(root, HYPOTHESES_DIRNAME, HYPOTHESIS_RE, "hypothesis"),
        reviews_text=read_reviews(root),
    )


def build_index_data(archive: Archive) -> dict:
    formal_cases = []
    for entry in archive.formal_entries:
        formal_cases.append(
            {
                "id": f"case:{entry.entry_id}",
                "title": entry.title,
                "path": relative_posix(entry.path, archive.root),
                "date": match_first(DATE_RE, entry.block),
                "scores": {
                    "sustainability": int(match_first(SUSTAINABILITY_RE, entry.block) or 0),
                    "learning_speed": int(match_first(LEARNING_RE, entry.block) or 0),
                    "external_validation": int(match_first(EXTERNAL_RE, entry.block) or 0),
                },
                "judgment": match_first(JUDGMENT_RE, entry.block),
            }
        )

    hypothesis_notes = []
    for entry in archive.hypothesis_entries:
        hypothesis_notes.append(
            {
                "id": f"hypothesis:{entry.entry_id}",
                "title": entry.title,
                "path": relative_posix(entry.path, archive.root),
                "date": match_first(DATE_RE, entry.block),
                "status": match_first(STATUS_RE, entry.block),
            }
        )

    return {
        "version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(archive.root.as_posix()),
        "counts": {
            "formal": len(formal_cases),
            "hypothesis": len(hypothesis_notes),
        },
        "formal_cases": formal_cases,
        "hypothesis_notes": hypothesis_notes,
    }


def format_entry_overview(entry: Entry, root: Path) -> str:
    date = match_first(DATE_RE, entry.block) or "-"
    path_text = relative_posix(entry.path, root)
    if entry.kind == "case":
        judgment = match_first(JUDGMENT_RE, entry.block) or "-"
        return (
            f"- {display_id(entry.kind, entry.entry_id)} | {entry.title} | 日期: {date} | "
            f"判断: {judgment} | 文件: `{path_text}`"
        )
    status = match_first(STATUS_RE, entry.block) or "-"
    return (
        f"- {display_id(entry.kind, entry.entry_id)} | {entry.title} | 日期: {date} | "
        f"状态: {status} | 文件: `{path_text}`"
    )


def review_overview_lines(reviews_text: str) -> str:
    if is_default_review_text(reviews_text):
        return REVIEW_EMPTY
    headings = []
    for line in reviews_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") and stripped != REVIEW_SECTION_TITLE:
            headings.append(stripped[3:])
    if headings:
        lines = [f"- 文件: `{REVIEWS_FILENAME}`"]
        lines.extend(f"- {heading}" for heading in headings)
        return "\n".join(lines)
    return f"- 文件: `{REVIEWS_FILENAME}`\n- 已有复盘记录。"


def render_overview(archive: Archive) -> str:
    formal_body = (
        "\n".join(format_entry_overview(entry, archive.root) for entry in archive.formal_entries)
        if archive.formal_entries
        else FORMAL_EMPTY
    )
    hypothesis_body = (
        "\n".join(format_entry_overview(entry, archive.root) for entry in archive.hypothesis_entries)
        if archive.hypothesis_entries
        else HYPOTHESIS_EMPTY
    )
    review_body = review_overview_lines(archive.reviews_text)
    return (
        f"{OVERVIEW_TITLE}\n\n"
        "## 固定定义\n\n"
        "独特优势只按这 3 个标准判断：\n\n"
        "1. 长期可持续\n"
        "2. 学习速度更快\n"
        "3. 做得更好且有外部验证\n\n"
        "## 数据层\n\n"
        "- 正式案例源目录: `strength-system/cases/`\n"
        "- 假设线索源目录: `strength-system/hypotheses/`\n"
        "- 复盘记录文件: `strength-system/reviews.md`\n"
        "- 生成索引: `strength-system/case-index.json`\n"
        "- 生成人类总览: `strength-system/case-library.md`\n\n"
        "## 正式案例目录\n\n"
        f"{formal_body}\n\n"
        "## 假设线索目录\n\n"
        f"{hypothesis_body}\n\n"
        "## 复盘记录\n\n"
        f"{review_body}\n"
    )


def write_index(index_path: Path, index_data: dict) -> None:
    index_path.write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def read_index(index_path: Path) -> dict:
    return json.loads(index_path.read_text(encoding="utf-8"))


def write_overview(root: Path, archive: Archive) -> None:
    overview_path(root).write_text(render_overview(archive), encoding="utf-8")


def source_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    if cases_dir(root).exists():
        paths.extend(sorted(cases_dir(root).glob("*.md")))
    if hypotheses_dir(root).exists():
        paths.extend(sorted(hypotheses_dir(root).glob("*.md")))
    if reviews_path(root).exists():
        paths.append(reviews_path(root))
    return paths


def generated_files_are_stale(root: Path, index_path: Path) -> bool:
    overview = overview_path(root)
    if not index_path.exists() or not overview.exists():
        return True
    sources = source_paths(root)
    if not sources:
        return False
    latest_source_mtime = max(path.stat().st_mtime for path in sources)
    return index_path.stat().st_mtime < latest_source_mtime or overview.stat().st_mtime < latest_source_mtime


def sync_index(root: Path, index_path: Path, archive: Archive | None = None) -> dict:
    ensure_archive_layout(root)
    current_archive = archive or parse_archive(root)
    index_data = build_index_data(current_archive)
    write_index(index_path, index_data)
    write_overview(root, current_archive)
    return index_data


def print_index_list(index_data: dict) -> None:
    def display_index_id(raw_id: str) -> str:
        prefix, _, number = raw_id.partition(":")
        if prefix == "case" and number:
            return f"{FORMAL_KIND_LABEL}:{number}"
        if prefix == "hypothesis" and number:
            return f"{HYPOTHESIS_KIND_LABEL}:{number}"
        return raw_id

    print(FORMAL_KIND_LABEL)
    formal_cases = index_data.get("formal_cases", [])
    if formal_cases:
        for entry in formal_cases:
            print(f"{display_index_id(entry['id'])} | {entry['title']}")
    else:
        print(NONE_TEXT)

    print("")
    print(HYPOTHESIS_KIND_LABEL)
    hypothesis_notes = index_data.get("hypothesis_notes", [])
    if hypothesis_notes:
        for entry in hypothesis_notes:
            print(f"{display_index_id(entry['id'])} | {entry['title']}")
    else:
        print(NONE_TEXT)

    print("")
    counts = index_data.get("counts", {})
    print(f"数量 {FORMAL_KIND_LABEL}={counts.get('formal', 0)} {HYPOTHESIS_KIND_LABEL}={counts.get('hypothesis', 0)}")


def normalize_targets(raw_targets: list[str]) -> list[str]:
    normalized: list[str] = []
    for raw in raw_targets:
        token = raw.strip().lower()
        token = token.replace(" ", "")
        token = token.replace("：", ":")
        if not token:
            continue
        if token in {"all", "全部", "全部清空"}:
            normalized.append("all")
            continue
        if token in {"formal:all", "formalall", "正式案例:all", "正式案例all", "正式案例全部"}:
            normalized.append("formal:all")
            continue
        if token in {"hypothesis:all", "hypothesisall", "假设线索:all", "假设线索all", "假设线索全部"}:
            normalized.append("hypothesis:all")
            continue

        case_match = re.fullmatch(r"(?:case|正式案例):?(\d{3})", token)
        if case_match:
            normalized.append(f"case:{case_match.group(1)}")
            continue

        hypothesis_match = re.fullmatch(r"(?:hypothesis|假设线索):?(\d{3})", token)
        if hypothesis_match:
            normalized.append(f"hypothesis:{hypothesis_match.group(1)}")
            continue

        normalized.append(token)
    if not normalized:
        raise SystemExit("没有提供删除目标。")
    return normalized


def write_default_reviews(root: Path) -> None:
    reviews_path(root).write_text(default_reviews_text(), encoding="utf-8")


def delete_entries(root: Path, archive: Archive, targets: list[str]) -> tuple[list[Entry], Archive]:
    normalized = normalize_targets(targets)

    if "all" in normalized:
        removed = [*archive.formal_entries, *archive.hypothesis_entries]
        for entry in removed:
            if entry.path.exists():
                entry.path.unlink()
        write_default_reviews(root)
        return removed, parse_archive(root)

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

    known_formal_ids = {entry.entry_id for entry in archive.formal_entries}
    known_hypothesis_ids = {entry.entry_id for entry in archive.hypothesis_entries}

    missing_formal = sorted(requested_formal_ids - known_formal_ids)
    missing_hypothesis = sorted(requested_hypothesis_ids - known_hypothesis_ids)
    if missing_formal or missing_hypothesis:
        messages = []
        if missing_formal:
            messages.append("缺少正式案例编号: " + ", ".join(missing_formal))
        if missing_hypothesis:
            messages.append("缺少假设线索编号: " + ", ".join(missing_hypothesis))
        raise SystemExit("; ".join(messages))

    removed: list[Entry] = []
    for entry in archive.formal_entries:
        if remove_formal_all or entry.entry_id in requested_formal_ids:
            if entry.path.exists():
                entry.path.unlink()
            removed.append(entry)

    for entry in archive.hypothesis_entries:
        if remove_hypothesis_all or entry.entry_id in requested_hypothesis_ids:
            if entry.path.exists():
                entry.path.unlink()
            removed.append(entry)

    return removed, parse_archive(root)


def find_section_index(lines: list[str], candidates: list[str]) -> int:
    for candidate in candidates:
        if candidate in lines:
            return lines.index(candidate)
    raise ValueError(f"缺少章节标题。期望之一: {', '.join(candidates)}")


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
                entries.append(
                    Entry(kind=kind, entry_id=current_id, title=current_title, block=block, path=Path())
                )
            current_start = index
            current_id = match.group(1)
            current_title = match.group(2).strip()

    if current_start is not None:
        block = "\n".join(lines[current_start:]).strip()
        entries.append(Entry(kind=kind, entry_id=current_id, title=current_title, block=block, path=Path()))

    return entries


def parse_legacy_library(path: Path) -> LegacyLibrary:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    try:
        entries_index = find_section_index(lines, [LEGACY_FORMAL_SECTION_TITLE, "## Entries"])
        hypothesis_index = find_section_index(lines, [LEGACY_HYPOTHESIS_SECTION_TITLE, "## Hypothesis Notes"])
        review_index = find_section_index(lines, [LEGACY_REVIEW_SECTION_TITLE, "## Review Notes"])
    except ValueError as exc:
        raise SystemExit(f"旧版档案格式无效: {exc}") from exc

    formal_lines = lines[entries_index + 1 : hypothesis_index]
    hypothesis_lines = lines[hypothesis_index + 1 : review_index]
    review_lines = lines[review_index:]

    formal_entries = parse_blocks(formal_lines, CASE_RE, "case")
    hypothesis_entries = parse_blocks(hypothesis_lines, HYPOTHESIS_RE, "hypothesis")
    review_section = "\n".join(review_lines).strip()
    if review_section in {"## Review Notes", REVIEW_SECTION_TITLE}:
        review_section = default_reviews_text().strip()

    return LegacyLibrary(
        formal_entries=formal_entries,
        hypothesis_entries=hypothesis_entries,
        review_section=review_section,
    )


def looks_like_legacy_library(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return (
        LEGACY_FORMAL_SECTION_TITLE in text
        and LEGACY_HYPOTHESIS_SECTION_TITLE in text
        and OVERVIEW_TITLE not in text
    )


def has_material_new_source(root: Path) -> bool:
    if cases_dir(root).exists() and any(cases_dir(root).glob("*.md")):
        return True
    if hypotheses_dir(root).exists() and any(hypotheses_dir(root).glob("*.md")):
        return True
    reviews_file = reviews_path(root)
    if reviews_file.exists():
        reviews_text = reviews_file.read_text(encoding="utf-8").strip()
        if reviews_text and not is_default_review_text(reviews_text):
            return True
    return False


def ensure_not_legacy_root(root: Path, file_path: str | None) -> None:
    legacy_candidate = Path(file_path).resolve() if file_path else overview_path(root)
    if looks_like_legacy_library(legacy_candidate) and not has_material_new_source(root):
        raise SystemExit(
            "检测到旧版单文件档案，请先运行 migrate-legacy："
            "manage_case_library.py migrate-legacy --file strength-system/case-library.md --root strength-system"
        )


def entry_target_path(root: Path, kind: str, entry_id: str) -> Path:
    if kind == "case":
        return cases_dir(root) / f"{entry_id}.md"
    if kind == "hypothesis":
        return hypotheses_dir(root) / f"{entry_id}.md"
    raise SystemExit(f"未知条目类型: {kind}")


def ensure_migration_target_is_clean(root: Path, force: bool) -> None:
    if force:
        return
    existing_cases = list(cases_dir(root).glob("*.md")) if cases_dir(root).exists() else []
    existing_hypotheses = list(hypotheses_dir(root).glob("*.md")) if hypotheses_dir(root).exists() else []
    if existing_cases or existing_hypotheses:
        raise SystemExit("目标目录已经包含条目文件；如需覆盖，请使用 --force。")
    reviews_file = reviews_path(root)
    if reviews_file.exists():
        reviews_text = reviews_file.read_text(encoding="utf-8").strip()
        if reviews_text and not is_default_review_text(reviews_text):
            raise SystemExit("reviews.md 已存在且包含内容；如需覆盖，请使用 --force。")


def migrate_legacy(library_path: Path, root: Path, index_path: Path, force: bool) -> dict:
    if not library_path.exists():
        raise SystemExit(f"没有找到旧版档案: {library_path}")
    legacy = parse_legacy_library(library_path)
    ensure_archive_layout(root)
    ensure_migration_target_is_clean(root, force)

    for entry in legacy.formal_entries:
        target = entry_target_path(root, entry.kind, entry.entry_id)
        if target.exists() and not force:
            raise SystemExit(f"目标文件已存在: {target}")
        target.write_text(entry.block.rstrip() + "\n", encoding="utf-8")

    for entry in legacy.hypothesis_entries:
        target = entry_target_path(root, entry.kind, entry.entry_id)
        if target.exists() and not force:
            raise SystemExit(f"目标文件已存在: {target}")
        target.write_text(entry.block.rstrip() + "\n", encoding="utf-8")

    reviews_path(root).write_text(legacy.review_section.rstrip() + "\n", encoding="utf-8")
    archive = parse_archive(root)
    return sync_index(root, index_path, archive)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="列出、迁移或清理独特优势案例档案。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--root", help="strength-system 根目录路径")
    list_parser.add_argument("--file", help="兼容参数：case-library.md 路径")
    list_parser.add_argument("--index", help="strength-system/case-index.json 的路径")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--root", help="strength-system 根目录路径")
    delete_parser.add_argument("--file", help="兼容参数：case-library.md 路径")
    delete_parser.add_argument("--index", help="strength-system/case-index.json 的路径")
    delete_parser.add_argument("--target", action="append", required=True, help="删除目标")

    reindex_parser = subparsers.add_parser("reindex")
    reindex_parser.add_argument("--root", help="strength-system 根目录路径")
    reindex_parser.add_argument("--file", help="兼容参数：case-library.md 路径")
    reindex_parser.add_argument("--index", help="strength-system/case-index.json 的路径")

    migrate_parser = subparsers.add_parser("migrate-legacy")
    migrate_parser.add_argument("--file", required=True, help="旧版 strength-system/case-library.md 的路径")
    migrate_parser.add_argument("--root", help="目标 strength-system 根目录路径")
    migrate_parser.add_argument("--index", help="strength-system/case-index.json 的路径")
    migrate_parser.add_argument("--force", action="store_true", help="允许覆盖目标结构")

    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "migrate-legacy":
        library_path = Path(args.file).resolve()
        root = root_path(Path(args.root) if args.root else None, args.file)
        index_path = Path(args.index).resolve() if args.index else default_index_path(root)
        index_data = migrate_legacy(library_path, root, index_path, args.force)
        counts = index_data["counts"]
        print("旧版档案已迁移")
        print(f"{FORMAL_KIND_LABEL}={counts['formal']} {HYPOTHESIS_KIND_LABEL}={counts['hypothesis']}")
        return 0

    root = root_path(Path(args.root) if args.root else None, getattr(args, "file", None))
    index_path = Path(args.index).resolve() if getattr(args, "index", None) else default_index_path(root)
    if not root.exists():
        raise SystemExit(f"没有找到档案目录: {root}")
    ensure_not_legacy_root(root, getattr(args, "file", None))

    if args.command == "list":
        if generated_files_are_stale(root, index_path):
            sync_index(root, index_path)
        print_index_list(read_index(index_path))
        return 0

    ensure_archive_layout(root)
    archive = parse_archive(root)

    if args.command == "reindex":
        index_data = sync_index(root, index_path, archive)
        counts = index_data["counts"]
        print("索引和总览已更新")
        print(f"{FORMAL_KIND_LABEL}={counts['formal']} {HYPOTHESIS_KIND_LABEL}={counts['hypothesis']}")
        return 0

    if args.command == "delete":
        removed, updated = delete_entries(root, archive, args.target)
        sync_index(root, index_path, updated)
        print("已删除")
        if removed:
            for entry in removed:
                print(f"{display_id(entry.kind, entry.entry_id)} | {entry.title}")
        else:
            print(NONE_TEXT)
        print("")
        print(
            f"数量 {FORMAL_KIND_LABEL}={len(updated.formal_entries)} "
            f"{HYPOTHESIS_KIND_LABEL}={len(updated.hypothesis_entries)}"
        )
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
