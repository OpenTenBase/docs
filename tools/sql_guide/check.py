#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline source-consistency checker for the first-three-SQL walkthrough.

The checker answers exactly one question: are the three SQL statements quoted
in docs/guide/first-three-sql.md still byte-for-byte identical to the three
statements shown in docs/guide/01-quickstart.md?

Deliberate limits:

* standard library only, no third-party imports;
* reads local files, never opens a network connection;
* never executes SQL and never starts a database;
* only understands the narrow Markdown subset described in README.md;
* proves reference consistency, not technical correctness.

Exit codes: 0 all examples match, 1 document/locator/mismatch problem,
2 invalid CLI arguments or invalid manifest.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_USAGE = 2

SCHEMA_VERSION = 1
DEFAULT_MANIFEST = Path("tools") / "sql_guide" / "examples.json"

# A fenced code block: at most three spaces of indent, then ``` or ~~~ (3+),
# then an optional info string.
FENCE_RE = re.compile(r"^(?P<indent>[ \t]{0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")

# The guide binds an ID to the next fenced block with this HTML comment:
#   <!-- sql-guide-example: create-foo-table -->
MARKER_RE = re.compile(
    r"<!--\s*(?P<key>[A-Za-z0-9_.-]+)\s*:\s*(?P<ident>[A-Za-z0-9_.-]+)\s*-->"
)

PREVIEW_LIMIT = 160


class ManifestError(Exception):
    """The manifest is missing, unreadable, or structurally invalid."""


@dataclass(frozen=True)
class CodeLine:
    number: int
    text: str


@dataclass(frozen=True)
class Fence:
    start_index: int  # 0-based index of the opening fence line
    start_line: int  # 1-based line number of the opening fence
    info: str
    lines: Tuple[CodeLine, ...]
    closed: bool


@dataclass(frozen=True)
class Statement:
    line: int
    sql: str


@dataclass(frozen=True)
class Example:
    id: str
    statement_prefix: str


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    source_document: str
    guide_document: str
    allowed_prompts: Tuple[str, ...]
    guide_marker: str
    examples: Tuple[Example, ...]


@dataclass
class Binding:
    """One ID marker found in the guide, resolved to a SQL line when possible."""

    line: int
    sql: Optional[str] = None
    sql_line: Optional[int] = None
    problem: str = ""


@dataclass
class Result:
    example_id: str
    passed: bool
    reason: str = ""
    source_line: Optional[int] = None
    guide_line: Optional[int] = None
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class Report:
    manifest_path: str
    source_path: str
    guide_path: str
    results: List[Result] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for item in self.results if item.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    def exit_code(self) -> int:
        if self.issues or self.failed:
            return EXIT_MISMATCH
        return EXIT_OK


# --------------------------------------------------------------------------
# Markdown scanning
# --------------------------------------------------------------------------


def parse_fences(text: str) -> List[Fence]:
    """Return every fenced code block in document order.

    An unclosed fence runs to the end of the document; callers do not treat
    that as an error, because the statements we look for are matched by
    content, not by fence boundaries.
    """
    lines = text.splitlines()
    fences: List[Fence] = []
    index = 0
    total = len(lines)

    while index < total:
        match = FENCE_RE.match(lines[index])
        if match is None:
            index += 1
            continue

        token = match.group("fence")
        char = token[0]
        length = len(token)
        info = match.group("info").strip()
        start_index = index
        start_line = index + 1
        index += 1

        body: List[CodeLine] = []
        closed = False
        while index < total:
            stripped = lines[index].strip()
            if len(stripped) >= length and set(stripped) == {char}:
                closed = True
                index += 1
                break
            body.append(CodeLine(index + 1, lines[index]))
            index += 1

        fences.append(Fence(start_index, start_line, info, tuple(body), closed))

    return fences


def extract_source_statements(text: str, prompts: Sequence[str]) -> List[Statement]:
    """Pull candidate statements out of fenced blocks in the source document.

    Only lines that start with one of the declared prompts qualify. Everything
    else inside a fence -- command output, meta-commands, shell lines -- is
    ignored, so no output line can be mistaken for a statement.
    """
    ordered = sorted(prompts, key=len, reverse=True)
    statements: List[Statement] = []

    for fence in parse_fences(text):
        for code_line in fence.lines:
            stripped = code_line.text.strip()
            for prompt in ordered:
                if not stripped.startswith(prompt):
                    continue
                sql = stripped[len(prompt) :].strip()
                if sql:
                    statements.append(Statement(code_line.number, sql))
                break

    return statements


def load_manifest(path: Path) -> Manifest:
    """Read and validate the manifest, raising ManifestError on any defect."""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ManifestError("manifest not found: {}".format(path)) from None
    except OSError as exc:
        raise ManifestError("manifest unreadable: {} ({})".format(path, exc)) from None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestError(
            "manifest is not valid JSON: {} (line {}, column {})".format(
                path, exc.lineno, exc.colno
            )
        ) from None

    if not isinstance(data, dict):
        raise ManifestError("manifest root must be a JSON object")

    allowed_keys = {
        "schema_version",
        "source_document",
        "guide_document",
        "allowed_prompts",
        "guide_marker",
        "examples",
    }
    unknown = sorted(set(data) - allowed_keys)
    if unknown:
        raise ManifestError(
            "manifest has unsupported key(s): {}".format(", ".join(unknown))
        )
    missing = sorted(allowed_keys - set(data))
    if missing:
        raise ManifestError(
            "manifest is missing key(s): {}".format(", ".join(missing))
        )

    version = data["schema_version"]
    if not isinstance(version, int) or isinstance(version, bool):
        raise ManifestError("schema_version must be an integer")
    if version != SCHEMA_VERSION:
        raise ManifestError(
            "unsupported schema_version {}, expected {}".format(
                version, SCHEMA_VERSION
            )
        )

    for key in ("source_document", "guide_document", "guide_marker"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ManifestError("{} must be a non-empty string".format(key))

    prompts = data["allowed_prompts"]
    if not isinstance(prompts, list) or not prompts:
        raise ManifestError("allowed_prompts must be a non-empty list")
    for prompt in prompts:
        if not isinstance(prompt, str) or not prompt:
            raise ManifestError("every allowed_prompts entry must be a non-empty string")

    raw_examples = data["examples"]
    if not isinstance(raw_examples, list) or not raw_examples:
        raise ManifestError("examples must be a non-empty list")

    examples: List[Example] = []
    seen_ids = set()
    for position, item in enumerate(raw_examples, start=1):
        if not isinstance(item, dict):
            raise ManifestError("examples[{}] must be a JSON object".format(position))
        extra = sorted(set(item) - {"id", "statement_prefix"})
        if extra:
            raise ManifestError(
                "examples[{}] has unsupported key(s): {}".format(
                    position, ", ".join(extra)
                )
            )
        example_id = item.get("id")
        prefix = item.get("statement_prefix")
        if not isinstance(example_id, str) or not example_id.strip():
            raise ManifestError("examples[{}].id must be a non-empty string".format(position))
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", example_id):
            raise ManifestError(
                "examples[{}].id must match [A-Za-z0-9_.-]+, got {!r}".format(
                    position, example_id
                )
            )
        if not isinstance(prefix, str) or not prefix.strip():
            raise ManifestError(
                "examples[{}].statement_prefix must be a non-empty string".format(position)
            )
        if example_id in seen_ids:
            raise ManifestError("duplicate example id: {}".format(example_id))
        seen_ids.add(example_id)
        examples.append(Example(example_id, prefix))

    return Manifest(
        schema_version=version,
        source_document=data["source_document"],
        guide_document=data["guide_document"],
        allowed_prompts=tuple(prompts),
        guide_marker=data["guide_marker"],
        examples=tuple(examples),
    )


def bind_guide(text: str, marker: str) -> Tuple[Dict[str, List[Binding]], List[str]]:
    """Resolve every `<!-- marker: id -->` in the guide to the block after it.

    A binding is only accepted when the marker is followed by nothing but blank
    lines and then a single-line ```sql fence. Anything else is reported, never
    silently skipped.
    """
    lines = text.splitlines()
    fences = parse_fences(text)
    bindings: Dict[str, List[Binding]] = {}
    issues: List[str] = []

    for index, raw in enumerate(lines):
        match = MARKER_RE.search(raw)
        if match is None or match.group("key") != marker:
            continue

        ident = match.group("ident")
        marker_line = index + 1
        fence = next((item for item in fences if item.start_index > index), None)
        if fence is None:
            bindings.setdefault(ident, []).append(
                Binding(marker_line, problem="marker is not followed by a code fence")
            )
            continue

        gap = [text_line for text_line in lines[index + 1 : fence.start_index] if text_line.strip()]
        if gap:
            bindings.setdefault(ident, []).append(
                Binding(
                    marker_line,
                    problem="non-blank content between marker (line {}) and fence (line {})".format(
                        marker_line, fence.start_line
                    ),
                )
            )
            continue

        info_tokens = fence.info.split()
        if not info_tokens or info_tokens[0].lower() != "sql":
            bindings.setdefault(ident, []).append(
                Binding(
                    marker_line,
                    problem="marker is not followed by a ```sql fence (fence at line {})".format(
                        fence.start_line
                    ),
                )
            )
            continue

        body = [item for item in fence.lines if item.text.strip()]
        if len(body) != 1:
            bindings.setdefault(ident, []).append(
                Binding(
                    marker_line,
                    problem="expected exactly one SQL line in the fenced block at line {}, found {}".format(
                        fence.start_line, len(body)
                    ),
                )
            )
            continue

        if not fence.closed:
            issues.append(
                "fenced block at line {} is never closed".format(fence.start_line)
            )

        bindings.setdefault(ident, []).append(
            Binding(marker_line, body[0].text.strip(), body[0].number)
        )

    return bindings, issues


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------


def first_difference(left: str, right: str) -> int:
    """Return the 0-based index of the first differing character."""
    for position, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return position
    return min(len(left), len(right))


def preview(value: str) -> str:
    if len(value) <= PREVIEW_LIMIT:
        return value
    return value[: PREVIEW_LIMIT - 3] + "..."


def evaluate(
    manifest: Manifest,
    source_text: str,
    guide_text: str,
) -> Tuple[List[Result], List[str]]:
    statements = extract_source_statements(source_text, manifest.allowed_prompts)
    bindings, issues = bind_guide(guide_text, manifest.guide_marker)
    results: List[Result] = []

    known_ids = {example.id for example in manifest.examples}
    for ident, found in sorted(bindings.items()):
        if ident not in known_ids:
            for item in found:
                issues.append(
                    "guide line {}: marker id {!r} is not declared in the manifest".format(
                        item.line, ident
                    )
                )

    for example in manifest.examples:
        bound = bindings.get(example.id, [])

        if not bound:
            results.append(
                Result(
                    example.id,
                    False,
                    "guide marker not found; expected <!-- {}: {} -->".format(
                        manifest.guide_marker, example.id
                    ),
                )
            )
            continue

        if len(bound) > 1:
            lines = ", ".join(str(item.line) for item in bound)
            results.append(
                Result(
                    example.id,
                    False,
                    "guide marker appears {} times (lines {}); each id must appear once".format(
                        len(bound), lines
                    ),
                )
            )
            continue

        single = bound[0]
        if single.problem or single.sql is None:
            results.append(
                Result(example.id, False, single.problem, guide_line=single.line)
            )
            continue

        candidates = [
            item for item in statements if item.sql.startswith(example.statement_prefix)
        ]

        if not candidates:
            results.append(
                Result(
                    example.id,
                    False,
                    "source statement not found; no prompted line starts with {!r}".format(
                        example.statement_prefix
                    ),
                    guide_line=single.sql_line,
                    actual=single.sql,
                )
            )
            continue

        if len(candidates) > 1:
            lines = ", ".join(str(item.line) for item in candidates)
            results.append(
                Result(
                    example.id,
                    False,
                    "source statement is ambiguous: {} candidates with prefix {!r} at lines {}; "
                    "refusing to pick one".format(
                        len(candidates), example.statement_prefix, lines
                    ),
                    guide_line=single.sql_line,
                    actual=single.sql,
                )
            )
            continue

        source = candidates[0]
        if source.sql == single.sql:
            results.append(
                Result(
                    example.id,
                    True,
                    source_line=source.line,
                    guide_line=single.sql_line,
                )
            )
            continue

        offset = first_difference(source.sql, single.sql)
        results.append(
            Result(
                example.id,
                False,
                "statement differs from source at column {} (source line {})".format(
                    offset + 1, source.line
                ),
                source_line=source.line,
                guide_line=single.sql_line,
                expected=source.sql,
                actual=single.sql,
            )
        )

    return results, issues


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def render_text(report: Report) -> str:
    lines = [
        "sql-guide source consistency check",
        "  manifest: {}".format(report.manifest_path),
        "  source:   {}".format(report.source_path),
        "  guide:    {}".format(report.guide_path),
        "",
    ]

    for result in report.results:
        if result.passed:
            lines.append(
                "PASS  {:<22} guide:{} <- source:{}".format(
                    result.example_id, result.guide_line, result.source_line
                )
            )
            continue

        lines.append("FAIL  {}".format(result.example_id))
        lines.append("      reason: {}".format(result.reason))
        if result.guide_line is not None:
            lines.append("      guide:  {}:{}".format(report.guide_path, result.guide_line))
        if result.source_line is not None:
            lines.append("      source: {}:{}".format(report.source_path, result.source_line))
        if result.expected is not None:
            lines.append("      expected: {}".format(result.expected))
        if result.actual is not None:
            lines.append("      actual:   {}".format(result.actual))

    if report.issues:
        lines.append("")
        lines.append("scope issues:")
        for issue in report.issues:
            lines.append("  - {}".format(issue))

    lines.append("")
    lines.append(
        "summary: {} examples, {} passed, {} failed".format(
            report.total, report.passed, report.failed
        )
    )
    return "\n".join(lines)


def render_json(report: Report) -> str:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "summary": {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "status": "pass" if report.total and not report.failed and not report.issues else "fail",
        },
        "files": {
            "manifest": report.manifest_path,
            "source": report.source_path,
            "guide": report.guide_path,
        },
        "results": [
            {
                "id": result.example_id,
                "status": "pass" if result.passed else "fail",
                "reason": result.reason,
                "source": {"path": report.source_path, "line": result.source_line},
                "guide": {"path": report.guide_path, "line": result.guide_line},
                "expected": preview(result.expected) if result.expected is not None else None,
                "actual": preview(result.actual) if result.actual is not None else None,
            }
            for result in report.results
        ],
        "issues": list(report.issues),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check.py",
        description=(
            "Compare the SQL statements quoted in the companion guide with the "
            "statements in the source document. Offline, read-only, never executes SQL."
        ),
    )
    parser.add_argument(
        "--root",
        default=".",
        help="repository root that contains the manifest and both documents (default: .)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="report format (default: text)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print("error: --root is not a directory: {}".format(root), file=sys.stderr)
        return EXIT_USAGE

    manifest_path = (root / DEFAULT_MANIFEST).resolve()

    try:
        manifest = load_manifest(manifest_path)
    except ManifestError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return EXIT_USAGE

    source_path = (root / manifest.source_document).resolve()
    guide_path = (root / manifest.guide_document).resolve()

    source_text = ""
    guide_text = ""
    missing: List[str] = []
    for label, path in (("source", source_path), ("guide", guide_path)):
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            missing.append("{} document not found: {}".format(label, manifest.source_document if label == "source" else manifest.guide_document))
            continue
        except OSError as exc:
            missing.append(
                "{} document unreadable: {} ({})".format(
                    label, path, exc
                )
            )
            continue
        if label == "source":
            source_text = text
        else:
            guide_text = text

    report = Report(
        manifest_path=str(DEFAULT_MANIFEST),
        source_path=manifest.source_document,
        guide_path=manifest.guide_document,
    )

    if missing:
        for example in manifest.examples:
            report.results.append(
                Result(example.id, False, "; ".join(missing))
            )
    else:
        results, issues = evaluate(manifest, source_text, guide_text)
        report.results = results
        report.issues = issues

    if args.output_format == "json":
        print(render_json(report))
    else:
        print(render_text(report))

    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
