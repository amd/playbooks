#!/usr/bin/env python3
"""
Playbook Test Coverage Preview
===============================

Launches a lightweight local server that renders playbook README files with
visible test coverage annotations — showing exactly which code blocks are
tested by CI, their test IDs, platform targets, timeouts, and dependency chains.

Usage:
    python .github/scripts/preview_tests.py [--port PORT]

Then open http://localhost:8089 in your browser.

Features:
    - Visual badges on tested code blocks (green for visible, purple for hidden)
    - Test metadata display (ID, platform, timeout, dependencies)
    - Test result overlay when results exist (pass/fail/skip)
    - Coverage statistics per playbook
    - Dark theme matching the Halo website
"""

import argparse
import http.server
import json
import mimetypes
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote


# ─── Paths ──────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLAYBOOKS_ROOT = REPO_ROOT / "playbooks"
TEST_RESULTS_ROOT = REPO_ROOT / "test-results"


# ─── Utility Functions ──────────────────────────────────────────────────────


def parse_test_attributes(attr_string: str) -> dict:
    """Parse key=value attributes from a @test tag string."""
    attrs = {}
    for match in re.finditer(r'(\w+)=(?:"([^"]+)"|(\S+))', attr_string):
        key = match.group(1)
        value = match.group(2) if match.group(2) else match.group(3)
        if key == "timeout":
            value = int(value)
        elif key in ("continue_on_error", "hidden"):
            value = value.lower() == "true"
        elif key == "depends_on":
            value = [d.strip() for d in value.split(",") if d.strip()]
        attrs[key] = value
    return attrs


def scan_playbooks() -> list[dict]:
    """Scan all playbooks and return metadata with test coverage info."""
    playbooks = []
    for category in ["core", "supplemental"]:
        cat_path = PLAYBOOKS_ROOT / category
        if not cat_path.exists():
            continue
        for folder in sorted(cat_path.iterdir()):
            if not folder.is_dir():
                continue
            json_path = folder / "playbook.json"
            readme_path = folder / "README.md"
            if not json_path.exists():
                continue
            try:
                meta = json.loads(json_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            test_count = 0
            hidden_count = 0
            total_code_blocks = 0

            if readme_path.exists():
                content = readme_path.read_text(encoding="utf-8")
                for m in re.finditer(r"<!-- @test:([^>]+) -->", content):
                    test_count += 1
                    a = parse_test_attributes(m.group(1))
                    if a.get("hidden", False):
                        hidden_count += 1
                total_code_blocks = len(re.findall(r"```\w*\s*\n", content))

            # Check for test results
            results_summary = None
            rpath = TEST_RESULTS_ROOT / meta["id"] / "summary.json"
            if rpath.exists():
                try:
                    results_summary = json.loads(rpath.read_text(encoding="utf-8"))
                except Exception:
                    pass

            playbooks.append(
                {
                    "id": meta["id"],
                    "title": meta.get("title", meta["id"]),
                    "category": category,
                    "platforms": meta.get("platforms", []),
                    "test_count": test_count,
                    "hidden_count": hidden_count,
                    "visible_test_count": test_count - hidden_count,
                    "total_code_blocks": total_code_blocks,
                    "has_results": results_summary is not None,
                    "results_summary": results_summary,
                }
            )

    return playbooks


def transform_for_preview(content: str, playbook_id: str) -> tuple[str, list[dict]]:
    """
    Transform README markdown for preview:
    - Replace @test annotations with visible HTML marker divs
    - Strip @os tags but keep all content
    - Strip other annotation tags
    - Fix asset paths
    """
    tests = []

    # Replace @test blocks with visible markers
    test_pattern = (
        r"<!-- @test:([^>]+) -->\s*(```(\w+)?\s*\n[\s\S]*?```)\s*<!-- @test:end -->"
    )

    def replace_test(match):
        attr_str = match.group(1)
        code_block = match.group(2)
        attrs = parse_test_attributes(attr_str)

        test_id = attrs.get("id", "unknown")
        platform = attrs.get("platform", "all")
        timeout = attrs.get("timeout", 300)
        hidden = attrs.get("hidden", False)
        depends_on = attrs.get("depends_on", [])

        tests.append(
            {
                "id": test_id,
                "platform": platform,
                "timeout": timeout,
                "hidden": hidden,
                "depends_on": depends_on,
            }
        )

        deps = ",".join(depends_on) if depends_on else ""
        marker = (
            f'<div class="tb"'
            f' data-id="{test_id}"'
            f' data-platform="{platform}"'
            f' data-timeout="{timeout}"'
            f' data-hidden="{"true" if hidden else "false"}"'
            f' data-depends="{deps}">'
            f"</div>\n\n"
        )
        return marker + code_block

    result = re.sub(test_pattern, replace_test, content, flags=re.DOTALL)

    # Strip OS tags but keep content
    result = re.sub(r"<!-- @os:(?:windows|linux|all) -->", "", result)
    result = re.sub(r"<!-- @os:end -->", "", result)

    # Strip other annotation tags
    result = re.sub(
        r"<!-- @(?:preinstalled|preinstalled:end|require:[^>]+|setup:[^>]+|setup-content|setup-content:end) -->",
        "",
        result,
    )

    # Transform relative image paths to API routes
    result = re.sub(
        r"!\[([^\]]*)\]\((?!https?://|/)([^)]+)\)",
        lambda m: f"![{m.group(1)}](/api/playbooks/{playbook_id}/{m.group(2)})",
        result,
    )
    result = re.sub(
        r'src="(?!https?://|/)([^"]+)"',
        lambda m: f'src="/api/playbooks/{playbook_id}/{m.group(1)}"',
        result,
    )

    return result, tests


def get_playbook_content(playbook_id: str):
    """Load and transform a playbook for preview."""
    for category in ["core", "supplemental"]:
        folder = PLAYBOOKS_ROOT / category / playbook_id
        readme_path = folder / "README.md"
        json_path = folder / "playbook.json"

        if not readme_path.exists() or not json_path.exists():
            continue

        meta = json.loads(json_path.read_text(encoding="utf-8"))
        content = readme_path.read_text(encoding="utf-8")
        transformed, tests = transform_for_preview(content, playbook_id)

        # Load test results if available
        results_map = {}
        rpath = TEST_RESULTS_ROOT / playbook_id / "summary.json"
        if rpath.exists():
            try:
                summary = json.loads(rpath.read_text(encoding="utf-8"))
                for r in summary.get("results", []):
                    results_map[r["test_id"]] = {
                        "success": r["success"],
                        "skipped": r.get("skipped", False),
                        "duration": r.get("duration", 0),
                        "error": r.get("error_message", ""),
                    }
            except Exception:
                pass

        for test in tests:
            r = results_map.get(test["id"])
            if r:
                test["result"] = r

        return {
            "id": meta["id"],
            "title": meta.get("title", meta["id"]),
            "category": category,
            "content": transformed,
            "tests": tests,
        }

    return None


# ─── HTTP Server ────────────────────────────────────────────────────────────


class PreviewHandler(http.server.BaseHTTPRequestHandler):
    """Serves the preview SPA and API endpoints."""

    def log_message(self, format, *args):
        pass  # Suppress default logging

    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        if path in ("/", ""):
            self._send_html(HTML_TEMPLATE)
        elif path == "/api/playbooks":
            self._send_json(scan_playbooks())
        elif path.startswith("/api/playbooks/"):
            parts = path.split("/")
            if len(parts) >= 4:
                pid = parts[3]
                if len(parts) > 4:
                    self._serve_asset(pid, "/".join(parts[4:]))
                else:
                    data = get_playbook_content(pid)
                    if data:
                        self._send_json(data)
                    else:
                        self.send_error(404)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def _send_html(self, content: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _serve_asset(self, playbook_id: str, asset_path: str):
        for category in ["core", "supplemental"]:
            fpath = PLAYBOOKS_ROOT / category / playbook_id / asset_path
            if fpath.exists() and fpath.is_file():
                mime, _ = mimetypes.guess_type(str(fpath))
                self.send_response(200)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.end_headers()
                self.wfile.write(fpath.read_bytes())
                return
        self.send_error(404)


# ─── HTML Template ──────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Playbook Test Coverage Preview</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark-dimmed.min.css">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <style>
    /* ── Reset & Base ──────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d0d0d; color: #e0e0e0; }

    /* ── Layout ────────────────────────────────────────── */
    .app { display: flex; flex-direction: column; height: 100vh; }
    .layout { display: flex; flex: 1; overflow: hidden; }

    /* ── Header ────────────────────────────────────────── */
    header {
      display: flex; align-items: center; gap: 16px;
      padding: 12px 24px;
      background: #141414; border-bottom: 1px solid #282828;
      flex-shrink: 0;
    }
    header h1 { font-size: 16px; font-weight: 700; color: #D4915D; letter-spacing: -0.3px; }
    header .subtitle { font-size: 12px; color: #666; }
    .header-badge {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 3px 10px; border-radius: 10px;
      font-size: 11px; font-weight: 600;
      background: #1a2e1a; color: #4ade80; border: 1px solid #2d5a2d;
    }
    .header-badge.warn { background: #2e2a1a; color: #fbbf24; border-color: #5a4d2d; }

    /* ── Sidebar ───────────────────────────────────────── */
    .sidebar {
      width: 300px; flex-shrink: 0;
      background: #111; border-right: 1px solid #282828;
      overflow-y: auto; padding: 12px 0;
    }
    .sidebar-section { padding: 8px 16px 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #555; }
    .sidebar-item {
      display: flex; align-items: center; gap: 10px;
      padding: 10px 16px; cursor: pointer;
      transition: background 0.15s;
      border-left: 3px solid transparent;
    }
    .sidebar-item:hover { background: #1a1a1a; }
    .sidebar-item.active { background: #1a1a1a; border-left-color: #D4915D; }
    .sidebar-item .title { font-size: 13px; font-weight: 500; color: #ccc; flex: 1; min-width: 0; }
    .sidebar-item.active .title { color: #fff; }
    .sidebar-item .title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .sidebar-item .count {
      display: inline-flex; align-items: center; justify-content: center;
      min-width: 22px; height: 22px; padding: 0 6px;
      border-radius: 11px; font-size: 11px; font-weight: 700;
      flex-shrink: 0;
    }
    .sidebar-item .count.has-tests { background: #1a2e1a; color: #4ade80; }
    .sidebar-item .count.no-tests { background: #1e1e1e; color: #555; }
    .sidebar-item .dot {
      width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
    }
    .sidebar-item .dot.tested { background: #22c55e; }
    .sidebar-item .dot.untested { background: #333; }

    /* ── Main Content ──────────────────────────────────── */
    .main { flex: 1; overflow-y: auto; padding: 32px 40px; }
    .main.empty { display: flex; align-items: center; justify-content: center; }
    .empty-state { text-align: center; color: #555; }
    .empty-state svg { width: 64px; height: 64px; margin-bottom: 16px; opacity: 0.3; }
    .empty-state h2 { font-size: 18px; color: #777; margin-bottom: 8px; }
    .empty-state p { font-size: 13px; }

    /* ── Stats Bar ─────────────────────────────────────── */
    .stats-bar {
      display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
      padding: 12px 16px; margin-bottom: 24px;
      background: #161616; border: 1px solid #282828; border-radius: 10px;
    }
    .stat {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 4px 10px; border-radius: 8px;
      font-size: 12px; font-weight: 500;
      background: #1e1e1e; color: #aaa;
    }
    .stat .num { font-weight: 700; color: #fff; }
    .stat.green .num { color: #4ade80; }
    .stat.purple .num { color: #a78bfa; }
    .stat.amber .num { color: #fbbf24; }
    .stat.red .num { color: #f87171; }
    .stat-divider { width: 1px; height: 20px; background: #333; }
    .stat.coverage { background: #1a2e1a; border: 1px solid #2d5a2d; color: #4ade80; font-weight: 700; }
    .stat.coverage.low { background: #2e1a1a; border-color: #5a2d2d; color: #f87171; }
    .stat.coverage.mid { background: #2e2a1a; border-color: #5a4d2d; color: #fbbf24; }

    /* ── Results Bar ───────────────────────────────────── */
    .results-bar {
      display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
      padding: 10px 16px; margin-bottom: 24px;
      background: #161616; border: 1px solid #282828; border-radius: 10px;
      font-size: 12px;
    }
    .results-bar .label { color: #888; font-weight: 600; margin-right: 4px; }
    .results-bar .pill {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 3px 10px; border-radius: 8px; font-weight: 600;
    }
    .results-bar .pill.pass { background: #1a2e1a; color: #4ade80; }
    .results-bar .pill.fail { background: #2e1a1a; color: #f87171; }
    .results-bar .pill.skip { background: #2e2a1a; color: #fbbf24; }

    /* ── Content Title ─────────────────────────────────── */
    .content-header { margin-bottom: 24px; }
    .content-header h2 { font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 4px; }
    .content-header .meta { font-size: 12px; color: #666; }

    /* ── Markdown Styles ───────────────────────────────── */
    .md h1 { font-size: 28px; font-weight: 800; color: #fff; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 1px solid #282828; }
    .md h2 { font-size: 22px; font-weight: 700; color: #fff; margin: 28px 0 12px; }
    .md h3 { font-size: 17px; font-weight: 600; color: #ddd; margin: 20px 0 8px; }
    .md h4 { font-size: 14px; font-weight: 600; color: #bbb; margin: 16px 0 6px; }
    .md p { font-size: 14px; line-height: 1.7; color: #bbb; margin: 10px 0; }
    .md ul, .md ol { padding-left: 24px; margin: 10px 0; }
    .md li { font-size: 14px; line-height: 1.7; color: #bbb; margin: 4px 0; }
    .md a { color: #D4915D; text-decoration: none; }
    .md a:hover { text-decoration: underline; }
    .md blockquote { border-left: 3px solid #D4915D; padding: 8px 16px; margin: 12px 0; background: #1a1a1a; border-radius: 0 6px 6px 0; }
    .md blockquote p { color: #999; }
    .md hr { border: none; border-top: 1px solid #282828; margin: 24px 0; }
    .md img { max-width: 100%; border-radius: 8px; margin: 12px 0; }
    .md table { width: 100%; border-collapse: collapse; margin: 12px 0; }
    .md th, .md td { padding: 8px 12px; border: 1px solid #333; font-size: 13px; }
    .md th { background: #1a1a1a; font-weight: 600; color: #ccc; text-align: left; }
    .md td { color: #aaa; }
    .md strong { color: #ddd; }
    .md em { color: #bbb; }

    /* ── Code Blocks ───────────────────────────────────── */
    .md code {
      font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
      font-size: 13px;
    }
    .md :not(pre) > code {
      background: #1e1e1e; padding: 2px 6px; border-radius: 4px;
      color: #e0e0e0; font-size: 12px; border: 1px solid #333;
    }
    .md pre {
      background: #0a0a0a; border: 1px solid #282828; border-radius: 8px;
      padding: 16px; margin: 12px 0; overflow-x: auto;
    }
    .md pre code { background: none; padding: 0; border: none; border-radius: 0; color: #e0e0e0; }

    /* ── Tested Block Wrapper ──────────────────────────── */
    .tested-block {
      margin: 12px 0; border-radius: 8px; overflow: hidden;
      border: 1px solid #2d5a2d;
    }
    .tested-block.hidden { border-color: #4a2d6a; }
    .tested-block.has-result-pass { border-color: #2d5a2d; }
    .tested-block.has-result-fail { border-color: #5a2d2d; }
    .tested-block.has-result-skip { border-color: #5a4d2d; }

    .tested-block pre {
      margin: 0 !important; border: none !important;
      border-radius: 0 !important;
    }

    /* ── Test Badge Header ─────────────────────────────── */
    .badge-header {
      display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
      padding: 7px 12px;
      background: linear-gradient(135deg, #0a2e1a 0%, #0d3520 100%);
      font-size: 11px;
    }
    .badge-header.hidden-test {
      background: linear-gradient(135deg, #1a1533 0%, #201840 100%);
    }
    .badge-header.result-fail {
      background: linear-gradient(135deg, #2e1515 0%, #351818 100%);
    }
    .badge-header.result-skip {
      background: linear-gradient(135deg, #2e2815 0%, #352e18 100%);
    }

    .badge-pill {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 2px 8px; border-radius: 10px;
      font-size: 10px; font-weight: 600;
      font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
    }

    .badge-pill.label { background: #166534; color: #4ade80; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-pill.label.is-hidden { background: #3b1a6a; color: #a78bfa; }
    .badge-pill.id { background: rgba(255,255,255,0.08); color: #ccc; }
    .badge-pill.platform { background: rgba(255,255,255,0.06); color: #999; }
    .badge-pill.timeout { background: rgba(255,255,255,0.04); color: #777; }
    .badge-pill.depends { background: rgba(212,145,93,0.15); color: #D4915D; }

    .badge-pill.result {
      margin-left: auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      text-transform: uppercase; letter-spacing: 0.5px;
    }
    .badge-pill.result.pass { background: #166534; color: #4ade80; }
    .badge-pill.result.fail { background: #7f1d1d; color: #f87171; }
    .badge-pill.result.skip { background: #78350f; color: #fbbf24; }

    /* ── Scrollbar ─────────────────────────────────────── */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #444; }

    /* ── Loading ────────────────────────────────────────── */
    .loading { display: flex; align-items: center; justify-content: center; padding: 48px; }
    .spinner { width: 32px; height: 32px; border: 3px solid #333; border-top-color: #D4915D; border-radius: 50%; animation: spin 0.8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Legend ─────────────────────────────────────────── */
    .legend {
      display: flex; flex-wrap: wrap; gap: 16px; align-items: center;
      padding: 10px 16px; margin-bottom: 24px;
      background: #131313; border: 1px solid #242424; border-radius: 8px;
      font-size: 11px; color: #666;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-swatch { width: 12px; height: 12px; border-radius: 3px; border: 1px solid rgba(255,255,255,0.1); }
    .legend-swatch.tested { background: #0a2e1a; border-color: #2d5a2d; }
    .legend-swatch.hidden { background: #1a1533; border-color: #4a2d6a; }
    .legend-swatch.untested { background: #0a0a0a; border-color: #282828; }
    .legend-swatch.passed { background: #166534; border-color: #22c55e; }
    .legend-swatch.failed { background: #7f1d1d; border-color: #ef4444; }
    .legend-swatch.skipped { background: #78350f; border-color: #f59e0b; }
  </style>
</head>
<body>
  <div class="app">
    <header>
      <h1>Playbook Test Coverage</h1>
      <span class="subtitle">Preview which code blocks are tested by CI</span>
      <div id="global-stats" style="margin-left:auto; display:flex; gap:8px;"></div>
    </header>
    <div class="layout">
      <aside class="sidebar" id="sidebar">
        <div class="loading"><div class="spinner"></div></div>
      </aside>
      <div class="main empty" id="main">
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
          </svg>
          <h2>Select a playbook</h2>
          <p>Choose a playbook from the sidebar to preview test coverage</p>
        </div>
      </div>
    </div>
  </div>

  <script>
    // ── State ────────────────────────────────────────────
    let allPlaybooks = [];
    let currentId = null;

    // ── Initialize ───────────────────────────────────────
    async function init() {
      try {
        allPlaybooks = await fetch('/api/playbooks').then(r => r.json());
        renderSidebar();
        renderGlobalStats();
        // Auto-select first playbook with tests
        const first = allPlaybooks.find(p => p.test_count > 0) || allPlaybooks[0];
        if (first) selectPlaybook(first.id);
      } catch (err) {
        document.getElementById('sidebar').innerHTML =
          '<div style="padding:16px;color:#f87171;">Failed to load playbooks</div>';
      }
    }

    // ── Render Sidebar ───────────────────────────────────
    function renderSidebar() {
      const sidebar = document.getElementById('sidebar');
      let html = '';

      // Group by category
      const categories = {};
      allPlaybooks.forEach(p => {
        if (!categories[p.category]) categories[p.category] = [];
        categories[p.category].push(p);
      });

      for (const [cat, playbooks] of Object.entries(categories)) {
        html += `<div class="sidebar-section">${cat}</div>`;
        playbooks.forEach(p => {
          const countClass = p.test_count > 0 ? 'has-tests' : 'no-tests';
          const dotClass = p.test_count > 0 ? 'tested' : 'untested';
          html += `
            <div class="sidebar-item" data-id="${p.id}" onclick="selectPlaybook('${p.id}')">
              <span class="dot ${dotClass}"></span>
              <span class="title" title="${p.title}">${p.title}</span>
              <span class="count ${countClass}">${p.test_count}</span>
            </div>`;
        });
      }

      sidebar.innerHTML = html;
    }

    // ── Global Stats ─────────────────────────────────────
    function renderGlobalStats() {
      const total = allPlaybooks.length;
      const withTests = allPlaybooks.filter(p => p.test_count > 0).length;
      const totalTests = allPlaybooks.reduce((s, p) => s + p.test_count, 0);
      const el = document.getElementById('global-stats');
      el.innerHTML = `
        <span class="header-badge">${totalTests} total tests</span>
        <span class="header-badge ${withTests < total ? 'warn' : ''}">${withTests}/${total} playbooks tested</span>
      `;
    }

    // ── Select Playbook ──────────────────────────────────
    async function selectPlaybook(id) {
      currentId = id;

      // Update sidebar active state
      document.querySelectorAll('.sidebar-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === id);
      });

      const main = document.getElementById('main');
      main.className = 'main';
      main.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

      try {
        const data = await fetch(`/api/playbooks/${id}`).then(r => r.json());
        renderContent(data);
      } catch (err) {
        main.innerHTML = '<div style="padding:32px;color:#f87171;">Failed to load playbook</div>';
      }
    }

    // ── Render Content ───────────────────────────────────
    function renderContent(data) {
      const main = document.getElementById('main');
      const meta = allPlaybooks.find(p => p.id === data.id) || {};

      // Build stats bar
      const cov = meta.total_code_blocks > 0
        ? Math.round((meta.visible_test_count / meta.total_code_blocks) * 100) : 0;
      const covClass = cov >= 60 ? '' : (cov >= 30 ? 'mid' : 'low');

      let statsHtml = `
        <div class="stats-bar">
          <span class="stat green"><span class="num">${meta.visible_test_count || 0}</span> visible tests</span>
          <span class="stat purple"><span class="num">${meta.hidden_count || 0}</span> hidden tests</span>
          <span class="stat"><span class="num">${meta.total_code_blocks || 0}</span> code blocks</span>
          <span class="stat-divider"></span>
          <span class="stat coverage ${covClass}">${cov}% coverage</span>
        </div>`;

      // Build results bar if available
      let resultsHtml = '';
      if (meta.has_results && meta.results_summary) {
        const rs = meta.results_summary;
        resultsHtml = `
          <div class="results-bar">
            <span class="label">Last Test Run:</span>
            <span class="pill pass">${rs.passed || 0} passed</span>
            <span class="pill fail">${rs.failed || 0} failed</span>
            <span class="pill skip">${rs.skipped || 0} skipped</span>
          </div>`;
      }

      // Legend
      const legendHtml = `
        <div class="legend">
          <span style="font-weight:600;color:#888;">Legend:</span>
          <span class="legend-item"><span class="legend-swatch tested"></span> Tested (visible on site)</span>
          <span class="legend-item"><span class="legend-swatch hidden"></span> Hidden test (not on site)</span>
          <span class="legend-item"><span class="legend-swatch untested"></span> Not tested</span>
          ${meta.has_results ? `
            <span style="margin-left:8px">|</span>
            <span class="legend-item"><span class="legend-swatch passed"></span> Passed</span>
            <span class="legend-item"><span class="legend-swatch failed"></span> Failed</span>
            <span class="legend-item"><span class="legend-swatch skipped"></span> Skipped</span>
          ` : ''}
        </div>`;

      // Render markdown
      marked.setOptions({
        gfm: true,
        breaks: false,
        highlight: function(code, lang) {
          if (lang && hljs.getLanguage(lang)) {
            try { return hljs.highlight(code, { language: lang }).value; } catch (e) {}
          }
          return hljs.highlightAuto(code).value;
        }
      });

      const rendered = marked.parse(data.content);

      main.innerHTML = `
        <div class="content-header">
          <h2>${data.title}</h2>
          <div class="meta">${data.category} &middot; ${data.id}</div>
        </div>
        ${statsHtml}
        ${resultsHtml}
        ${legendHtml}
        <div class="md" id="md-content">${rendered}</div>
      `;

      // Post-process: turn marker divs into visible badges
      processTestBadges(data.tests);
    }

    // ── Process Test Badges ──────────────────────────────
    function processTestBadges(tests) {
      document.querySelectorAll('#md-content .tb').forEach(marker => {
        const id = marker.dataset.id;
        const platform = marker.dataset.platform;
        const timeout = marker.dataset.timeout;
        const isHidden = marker.dataset.hidden === 'true';
        const depends = marker.dataset.depends ? marker.dataset.depends.split(',').filter(Boolean) : [];

        // Find matching test for results
        const test = tests.find(t => t.id === id);
        const result = test && test.result;

        // Determine result status
        let resultStatus = '';
        if (result) {
          if (result.skipped) resultStatus = 'skip';
          else if (result.success) resultStatus = 'pass';
          else resultStatus = 'fail';
        }

        // Platform icon
        const platformIcon = platform === 'windows' ? '\u229E'
          : platform === 'linux' ? '\u2318' : '\u25C9';

        // Build badge header
        const badgeHeader = document.createElement('div');
        let headerClass = 'badge-header';
        if (isHidden) headerClass += ' hidden-test';
        if (resultStatus === 'fail') headerClass += ' result-fail';
        if (resultStatus === 'skip') headerClass += ' result-skip';
        badgeHeader.className = headerClass;

        let pillsHtml = '';
        pillsHtml += `<span class="badge-pill label ${isHidden ? 'is-hidden' : ''}">${isHidden ? '\u{1F441} Hidden Test' : '\u2713 Tested'}</span>`;
        pillsHtml += `<span class="badge-pill id">${id}</span>`;
        pillsHtml += `<span class="badge-pill platform">${platformIcon} ${platform}</span>`;
        pillsHtml += `<span class="badge-pill timeout">\u23F1 ${timeout}s</span>`;
        if (depends.length > 0) {
          pillsHtml += `<span class="badge-pill depends">\u2192 ${depends.join(', ')}</span>`;
        }
        if (result) {
          const dur = result.duration ? ` (${result.duration.toFixed(1)}s)` : '';
          let statusLabel = '';
          if (result.skipped) statusLabel = 'Skipped';
          else if (result.success) statusLabel = 'Passed';
          else statusLabel = 'Failed';
          pillsHtml += `<span class="badge-pill result ${resultStatus}">${statusLabel}${dur}</span>`;
        }
        badgeHeader.innerHTML = pillsHtml;

        // Find the next <pre> sibling
        let nextPre = marker.nextElementSibling;
        // Skip whitespace text nodes (already handled by nextElementSibling)
        // But sometimes marked.js might wrap things differently
        if (nextPre && nextPre.tagName !== 'PRE') {
          // Try one more
          const after = nextPre.nextElementSibling;
          if (after && after.tagName === 'PRE') nextPre = after;
        }

        if (nextPre && nextPre.tagName === 'PRE') {
          // Create wrapper
          const wrapper = document.createElement('div');
          wrapper.className = 'tested-block' + (isHidden ? ' hidden' : '');
          if (resultStatus) wrapper.className += ` has-result-${resultStatus}`;

          nextPre.parentNode.insertBefore(wrapper, marker);
          wrapper.appendChild(badgeHeader);
          wrapper.appendChild(nextPre);
          marker.remove();
        } else {
          // Fallback: just replace the marker with the badge
          marker.replaceWith(badgeHeader);
        }
      });
    }

    // ── Boot ─────────────────────────────────────────────
    init();
  </script>
</body>
</html>"""


# ─── Entry Point ────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Preview playbook test coverage")
    parser.add_argument("--port", type=int, default=8089, help="Port (default: 8089)")
    args = parser.parse_args()

    print()
    print("  +---------------------------------------+")
    print("  |  Playbook Test Coverage Preview       |")
    print(f"  |  http://localhost:{str(args.port):<20s}|")
    print("  |  Press Ctrl+C to stop                |")
    print("  +---------------------------------------+")
    print()

    server = http.server.HTTPServer(("localhost", args.port), PreviewHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
