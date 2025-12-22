from pathlib import Path
import json


# Section parsers
def _get_section_h1(line: str) -> str | None:
    s = line.strip()
    if s.startswith("# "):
        return s[2:]
    return None


def _get_subsection_colon(line: str, next_line: str | None) -> str | None:
    if next_line is None:
        return None
    s = line.rstrip()
    next_s = next_line.strip()
    if s.endswith(":") and next_s.startswith("---"):
        return s[:-1].strip()
    return None


def _get_subsection_h2(line: str) -> str | None:
    s = line.strip()
    if s.startswith("## "):
        return s[3:]
    return None


def _get_subsection_h3(line: str) -> str | None:
    s = line.strip()
    if s.startswith("### "):
        return s[4:]
    return None


def _is_separator_line(line: str) -> bool:
    """
    True if the line is a decorative separator like
    --------------------------------, ________, =====, or ****.
    """
    s = line.strip()
    if len(s) < 3:
        return False
    # allow common separator chars; exclude backticks to keep code fences
    allowed = {"-", "_", "=", "*", "—", "─"}
    return set(s).issubset(allowed)


# Ingestion function
def ingest_file(file_path: Path) -> list[dict]:
    results: list[dict] = []
    current_section: str | None = None
    current_subsection: str | None = None
    current_subsub: str | None = None
    content: list[str] = []
    collecting = False

    def _save():
        nonlocal collecting, content, current_section, current_subsection, current_subsub, results
        # drop decorative lines that might have slipped in
        filtered = [ln for ln in content if not _is_separator_line(ln)]
        if not collecting or not filtered or current_section is None:
            content.clear()
            return

        results.append(
            {
                "section": current_section,
                "subsection": current_subsection,
                "subsubsection": current_subsub,
                "content": filtered,
            }
        )
        content.clear()

    with file_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else None

        section = _get_section_h1(line)
        if section:
            _save()
            current_section = section
            current_subsection = None
            current_subsub = None
            collecting = True
            continue

        subsection = _get_subsection_colon(line, next_line) or _get_subsection_h2(line)
        if subsection:
            _save()
            current_subsection = subsection
            current_subsub = None
            collecting = True
            continue

        subsub = _get_subsection_h3(line)
        if subsub:
            _save()
            current_subsub = subsub
            collecting = True
            continue

        if collecting:
            s = line.rstrip()
            if _is_separator_line(s):
                continue
            content.append(s)

    _save()  # Save any remaining content after the loop

    return results


# Ingestion on all the files in directory
def run_full_ingestion():
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "data"
    for md_path in data_dir.glob("*/*.md"):
        chunks = ingest_file(md_path)
        out_dir = md_path.parent / "chunked_reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{md_path.stem}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
