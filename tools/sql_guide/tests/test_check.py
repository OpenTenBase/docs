#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for tools/sql_guide/check.py.

Every case builds a tiny throw-away repository in a temporary directory, so the
tests never touch the real documents and never need a database or a network
connection. The last test class runs the checker against the real repository.

Run with:
    python3 -m unittest discover -s tools/sql_guide/tests -v
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK = Path(__file__).resolve().parents[1] / "check.py"
REPO_ROOT = CHECK.parents[2]

CREATE_SQL = "create table foo(id bigint, str text) distribute by shard(id);"
INSERT_SQL = "insert into foo values(1, 'tencent'), (2, 'shenzhen');"
SELECT_SQL = "select * from foo;"

# ---------------------------------------------------------------------------
# Fixtures modelled on docs/guide/01-quickstart.md and the companion guide.
# ---------------------------------------------------------------------------

SOURCE_HEADER = """# 快速入门

## 使用
* 连接到 CN 主节点执行 SQL

```
"""

SOURCE_BODY = """$ psql -h ${{CoordinateNode_IP}} -p ${{CoordinateNode_PORT}} -U opentenbase -d postgres

postgres=# create database test;
CREATE DATABASE
postgres=# \\c test test
You are now connected to database "test" as user "test".
test=> {create}
CREATE TABLE
test=> {insert}
COPY 2
test=> {select}
 id |   str
----+----------
  1 | tencent
  2 | shenzhen
(2 rows)

```
"""

SOURCE_FIXTURE = SOURCE_HEADER + SOURCE_BODY.format(
    create=CREATE_SQL, insert=INSERT_SQL, select=SELECT_SQL
)


def guide_block(example_id, sql):
    return "<!-- sql-guide-example: {} -->\n```sql\n{}\n```\n".format(example_id, sql)


GUIDE_HEADER = "# 读懂第一条 SQL：建表、插入与查询\n\n正文。\n\n"

GUIDE_FIXTURE = (
    GUIDE_HEADER
    + guide_block("create-foo-table", CREATE_SQL)
    + "\n"
    + guide_block("insert-foo-rows", INSERT_SQL)
    + "\n"
    + guide_block("select-foo-all", SELECT_SQL)
)

MANIFEST_FIXTURE = {
    "schema_version": 1,
    "source_document": "docs/guide/01-quickstart.md",
    "guide_document": "docs/guide/first-three-sql.md",
    "allowed_prompts": ["postgres=#", "test=>"],
    "guide_marker": "sql-guide-example",
    "examples": [
        {"id": "create-foo-table", "statement_prefix": "create table foo"},
        {"id": "insert-foo-rows", "statement_prefix": "insert into foo values"},
        {"id": "select-foo-all", "statement_prefix": "select * from foo"},
    ],
}


class CheckerTestCase(unittest.TestCase):
    """Base class: builds a fixture repository and runs the checker on it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "tools" / "sql_guide").mkdir(parents=True)
        (self.root / "docs" / "guide").mkdir(parents=True)
        self.manifest_path = self.root / "tools" / "sql_guide" / "examples.json"
        self.source_path = self.root / "docs" / "guide" / "01-quickstart.md"
        self.guide_path = self.root / "docs" / "guide" / "first-three-sql.md"
        self.write_manifest()
        self.write_source(SOURCE_FIXTURE)
        self.write_guide(GUIDE_FIXTURE)

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixture helpers ---------------------------------------------------

    def write_manifest(self, payload=None, raw=None):
        if raw is not None:
            self.manifest_path.write_text(raw, encoding="utf-8")
            return
        data = MANIFEST_FIXTURE if payload is None else payload
        self.manifest_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def write_source(self, text):
        self.source_path.write_text(text, encoding="utf-8")

    def write_guide(self, text):
        self.guide_path.write_text(text, encoding="utf-8")

    def line_of(self, path, needle):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if needle in line:
                return number
        raise AssertionError("fixture does not contain {!r}".format(needle))

    # -- runner ------------------------------------------------------------

    def run_check(self, *extra):
        completed = subprocess.run(
            [sys.executable, str(CHECK), "--root", str(self.root), *extra],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.returncode, completed.stdout, completed.stderr


class TestHappyPath(CheckerTestCase):
    """T01: the three correct examples pass with exit code 0."""

    def test_t01_all_examples_pass(self):
        code, out, err = self.run_check()
        self.assertEqual(code, 0, msg=err)
        self.assertIn("summary: 3 examples, 3 passed, 0 failed", out)
        self.assertEqual(out.count("PASS  "), 3)
        self.assertNotIn("FAIL", out)

    def test_t01_reports_source_line_numbers(self):
        _, out, _ = self.run_check()
        self.assertIn("guide:{} <- source:{}".format(
            self.line_of(self.guide_path, CREATE_SQL),
            self.line_of(self.source_path, CREATE_SQL),
        ), out)


class TestMismatch(CheckerTestCase):
    """T02 and T08: any byte-level drift is a failure with a precise location."""

    def test_t02_changed_string_literal_fails(self):
        changed = INSERT_SQL.replace("'shenzhen'", "'Shanghai'")
        self.write_guide(GUIDE_FIXTURE.replace(INSERT_SQL, changed))
        code, out, err = self.run_check()
        self.assertEqual(code, 1, msg=err)
        self.assertIn("FAIL  insert-foo-rows", out)
        self.assertIn("differs from source", out)
        self.assertIn("summary: 3 examples, 2 passed, 1 failed", out)

    def test_t02_failure_points_at_the_edited_line(self):
        changed = INSERT_SQL.replace("'shenzhen'", "'Shanghai'")
        self.write_guide(GUIDE_FIXTURE.replace(INSERT_SQL, changed))
        _, out, _ = self.run_check()
        expected_line = self.line_of(self.guide_path, changed)
        self.assertIn("guide:  docs/guide/first-three-sql.md:{}".format(expected_line), out)

    def test_t08_internal_space_is_not_normalised(self):
        spaced = INSERT_SQL.replace("'shenzhen'", "'shen zhen'")
        self.write_guide(GUIDE_FIXTURE.replace(INSERT_SQL, spaced))
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("differs from source", out)

    def test_t08_trailing_semicolon_is_compared(self):
        self.write_guide(GUIDE_FIXTURE.replace(SELECT_SQL, "select * from foo"))
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("FAIL  select-foo-all", out)


class TestSourceLocating(CheckerTestCase):
    """T03, T04, T05, T07: how the source document is located."""

    def test_t03_missing_source_document(self):
        self.source_path.unlink()
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("source document not found: docs/guide/01-quickstart.md", out)
        self.assertIn("summary: 3 examples, 0 passed, 3 failed", out)

    def test_t04_source_statement_missing(self):
        self.write_source(SOURCE_FIXTURE.replace("test=> " + INSERT_SQL + "\n", ""))
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("source statement not found", out)
        self.assertIn("FAIL  insert-foo-rows", out)

    def test_t05_two_matching_statements_are_ambiguous(self):
        duplicated = SOURCE_FIXTURE.replace(
            "test=> " + INSERT_SQL + "\n",
            "test=> " + INSERT_SQL + "\ntest=> " + INSERT_SQL + "\n",
        )
        self.write_source(duplicated)
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("ambiguous", out)
        self.assertIn("refusing to pick one", out)

    def test_t07_output_lines_are_not_treated_as_statements(self):
        # The fixture already mixes prompts, meta-commands and output; a clean
        # pass proves that only prompted lines were read, and that the prefix
        # match did not pick up "CREATE TABLE" or "COPY 2".
        code, out, _ = self.run_check()
        self.assertEqual(code, 0)
        self.assertNotIn("COPY 2", out)

    def test_t07_statement_outside_a_fence_is_ignored(self):
        injected = SOURCE_FIXTURE + "\ntest=> select * from foo;\n"
        self.write_source(injected)
        code, _, _ = self.run_check()
        self.assertEqual(code, 0, msg="a prompt line outside a fence must not be scanned")


class TestGuideBinding(CheckerTestCase):
    """T06: the guide side of the binding must be unique and well formed."""

    def test_t06_missing_marker(self):
        self.write_guide(
            GUIDE_FIXTURE.replace(guide_block("insert-foo-rows", INSERT_SQL), "")
        )
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("guide marker not found", out)
        self.assertIn("FAIL  insert-foo-rows", out)

    def test_t06_duplicate_marker(self):
        block = guide_block("create-foo-table", CREATE_SQL)
        self.write_guide(GUIDE_FIXTURE + "\n" + block)
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("appears 2 times", out)

    def test_t06_marker_without_fence(self):
        self.write_guide(
            GUIDE_FIXTURE.replace(
                guide_block("select-foo-all", SELECT_SQL),
                "<!-- sql-guide-example: select-foo-all -->\n",
            )
        )
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("not followed by", out)

    def test_t06_multi_line_block_is_rejected(self):
        block = "<!-- sql-guide-example: create-foo-table -->\n```sql\n{}\n{}\n```\n".format(
            CREATE_SQL, SELECT_SQL
        )
        self.write_guide(
            GUIDE_FIXTURE.replace(guide_block("create-foo-table", CREATE_SQL), block)
        )
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("expected exactly one SQL line", out)

    def test_t06_unknown_marker_id_is_reported(self):
        self.write_guide(
            GUIDE_FIXTURE + "\n" + guide_block("not-in-manifest", SELECT_SQL)
        )
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("is not declared in the manifest", out)


class TestManifestValidation(CheckerTestCase):
    """T09: a broken manifest is a usage error, never a silent pass."""

    def test_t09_invalid_json(self):
        self.write_manifest(raw="{ not json ")
        code, out, err = self.run_check()
        self.assertEqual(code, 2)
        self.assertIn("not valid JSON", err)
        self.assertEqual(out, "")

    def test_t09_missing_key(self):
        payload = dict(MANIFEST_FIXTURE)
        payload.pop("guide_marker")
        self.write_manifest(payload)
        code, _, err = self.run_check()
        self.assertEqual(code, 2)
        self.assertIn("missing key", err)

    def test_t09_unknown_key(self):
        payload = json.loads(json.dumps(MANIFEST_FIXTURE))
        payload["unexpected"] = True
        self.write_manifest(payload)
        code, _, err = self.run_check()
        self.assertEqual(code, 2)
        self.assertIn("unsupported key", err)

    def test_t09_unsupported_schema_version(self):
        payload = json.loads(json.dumps(MANIFEST_FIXTURE))
        payload["schema_version"] = 99
        self.write_manifest(payload)
        code, _, err = self.run_check()
        self.assertEqual(code, 2)
        self.assertIn("unsupported schema_version", err)

    def test_t09_missing_manifest(self):
        self.manifest_path.unlink()
        code, _, err = self.run_check()
        self.assertEqual(code, 2)
        self.assertIn("manifest not found", err)

    def test_t09_bad_root(self):
        completed = subprocess.run(
            [sys.executable, str(CHECK), "--root", str(self.root / "absent")],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("not a directory", completed.stderr)

    def test_t09_bad_cli_argument(self):
        completed = subprocess.run(
            [sys.executable, str(CHECK), "--format", "yaml"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 2)


class TestJsonReport(CheckerTestCase):
    """T10: the JSON report is machine readable and agrees with the text one."""

    def test_t10_json_report_is_consistent(self):
        code, out, _ = self.run_check("--format", "json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["summary"]["total"], 3)
        self.assertEqual(payload["summary"]["passed"], 3)
        self.assertEqual(payload["summary"]["failed"], 0)
        self.assertEqual(payload["summary"]["status"], "pass")
        self.assertEqual(len(payload["results"]), 3)
        self.assertEqual(payload["issues"], [])
        for item in payload["results"]:
            self.assertEqual(item["status"], "pass")
            self.assertIsInstance(item["guide"]["line"], int)
            self.assertIsInstance(item["source"]["line"], int)

    def test_t10_json_reports_failures_without_dumping_files(self):
        self.write_guide(GUIDE_FIXTURE.replace(INSERT_SQL, INSERT_SQL.replace("tencent", "tencnet")))
        code, out, _ = self.run_check("--format", "json")
        self.assertEqual(code, 1)
        payload = json.loads(out)
        self.assertEqual(payload["summary"]["failed"], 1)
        failed = [item for item in payload["results"] if item["status"] == "fail"]
        self.assertEqual(len(failed), 1)
        self.assertIn("differs from source", failed[0]["reason"])

    def test_t10_help_exits_zero(self):
        completed = subprocess.run(
            [sys.executable, str(CHECK), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("--format", completed.stdout)


class TestRealRepository(unittest.TestCase):
    """The documents shipped in this repository must satisfy the checker."""

    def test_real_repository_passes(self):
        completed = subprocess.run(
            [sys.executable, str(CHECK), "--root", str(REPO_ROOT)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stdout + completed.stderr)
        self.assertIn("3 examples, 3 passed, 0 failed", completed.stdout)

    def test_real_repository_json_passes(self):
        completed = subprocess.run(
            [sys.executable, str(CHECK), "--root", str(REPO_ROOT), "--format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["summary"]["status"], "pass")


if __name__ == "__main__":
    unittest.main(verbosity=2)
