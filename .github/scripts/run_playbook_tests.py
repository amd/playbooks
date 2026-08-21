#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

"""
Playbook Test Runner
====================

Extracts and executes test blocks from playbook README.md files.

Test blocks wrap existing code blocks using HTML comments that are invisible
to the website but can be parsed and executed by CI:

    <!-- @test:id=unique-test-name -->
    ```bash
    pip install transformers
    ```
    <!-- @test:end -->

Tests are executed in the order they appear in the README. Place prerequisite
steps (e.g. installing dependencies) before the tests that need them.

Platform inference:
    The target platform for each test is inferred automatically from the
    surrounding @os: tags. Tests inside ``<!-- @os:windows -->`` blocks run
    only on Windows, tests inside ``<!-- @os:linux -->`` blocks run only on
    Linux, and tests outside any @os: block run on all platforms.

Device inference:
    The target device(s) for each test is inferred from surrounding @device:
    tags. Tags support comma-separated values:
        ``<!-- @device:halo -->``       → runs only on halo
        ``<!-- @device:halo,stx -->``   → runs on halo or stx
    Tests outside any @device: block run on all devices. When --device is
    passed on the CLI, tests whose inferred device list doesn't include that
    device are skipped.
    Valid devices: halo, stx, krk, rx7900xt, rx9070xt.

Supported test attributes:
    - id: Unique identifier for the test (required)
    - timeout: Maximum execution time in seconds (default: 300)
    - workdir: Working directory relative to playbook assets folder
    - continue_on_error: true/false - whether to continue if this test fails (default: false)
    - hidden: true/false - if true, hides the code block from the website (default: false)
    - setup: Shell commands to run before the test script (e.g. venv activation).
             For Python tests, wraps execution in a shell that runs the setup first:
                 setup="source llm-env/bin/activate"  →  bash -c "source llm-env/bin/activate && python <script>"
             For shell tests, the setup commands are prepended to the script body.

Setup attribute:
    The `setup` attribute lets you specify shell commands (e.g. venv activation)
    that run before the test script. This is especially useful for Python code
    blocks which are otherwise executed directly with `python <script>`:

        <!-- @test:id=verify-imports setup="source llm-env/bin/activate" -->
        ```python
        import torch
        print(f"PyTorch version: {torch.__version__}")
        ```
        <!-- @test:end -->

    The runner expands this to: `bash -c "source llm-env/bin/activate && python test_verify-imports.py"`
    On Windows, it uses PowerShell instead of bash.

    For shell-based tests, the setup commands are prepended to the script body.

Reusable setup definitions (@setup):
    Instead of repeating raw shell commands in every test's `setup` attribute,
    you can define named, platform-specific setup steps using @setup comments.
    These HTML comments are invisible when the README is rendered as a webpage.

    The platform for each @setup is inferred from surrounding @os: tags.
    If a @setup definition is outside any @os: block, it applies to all platforms.

    Definition syntax (place anywhere in the README before first use):
        <!-- @os:windows -->
        <!-- @setup:id=activate-venv command="llm-env\\Scripts\\activate.bat" -->
        <!-- @os:end -->
        <!-- @os:linux -->
        <!-- @setup:id=activate-venv command="source llm-env/bin/activate" -->
        <!-- @os:end -->

    Or for a command that works on all platforms (outside @os: blocks):
        <!-- @setup:id=some-setup command="some-command" -->

    Then reference by name in test blocks:
        <!-- @test:id=install-deps setup=activate-venv -->
        ```bash
        pip install transformers
        ```
        <!-- @test:end -->

    The runner resolves `setup=activate-venv` to the platform-specific command
    at parse time. If the value doesn't match any @setup id, it is treated as
    a raw shell command for backward compatibility.

Reusable @var definitions (device-aware values):
    Use @var to declare a named value whose resolution depends on the active
    @device: scope. This is the device-aware analog of @setup, intended for
    cases where a single test should exercise a different value (e.g. a model
    id, container tag, or endpoint) depending on which device the runner was
    invoked with via ``--device``.

    Definition syntax (place anywhere in the README before first use). The
    preferred form uses an inline ``device=`` attribute:
        <!-- @var:id=lemonade_model device=halo,halo_box value="gpt-oss-120b-mxfp-GGUF" -->
        <!-- @var:id=lemonade_model device=stx,krk,rx7900xt,rx9070xt value="gpt-oss-20b-mxfp4-GGUF" -->

    The device(s) may also be inferred from a surrounding @device: block:
        <!-- @device:halo,halo_box -->
        <!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
        <!-- @device:end -->

    Or for a value that applies to all devices (no device= and no @device: block):
        <!-- @var:id=api_port value="13305" -->

    Reference inside test code with ``${name}`` syntax:
        <!-- @test:id=chat-test -->
        ```bash
        curl http://127.0.0.1:13305/api/v1/models | grep ${lemonade_model}
        ```
        <!-- @test:end -->

    Substitution is restricted to ``${name}`` placeholders whose name matches a
    declared @var id, so ordinary shell ``$variable`` / ``${env}`` usage is
    never touched. If a declared placeholder cannot be resolved for the active
    device, the runner raises a clear error rather than silently substituting
    an empty string.

Inline #hide marker:
    Lines ending with `#hide` inside a code block are executed by the test runner
    but should be stripped from the rendered website view. This lets you add
    prerequisite commands (e.g. venv activation) that the reader doesn't need to see
    repeated, without hiding the entire block:

        <!-- @test:id=install-deps -->
        ```bash
        source llm-env/bin/activate #hide
        pip install transformers
        ```
        <!-- @test:end -->

    In the coverage/CI log output, #hide lines are prefixed with [hidden] so
    reviewers can see what runs invisibly on the website.

Usage:
    python run_playbook_tests.py --playbook pytorch-rocm-llms --platform windows
    python run_playbook_tests.py --playbook pytorch-rocm-llms --platform windows --device halo
"""

import argparse
import contextlib
import dataclasses
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# TestBlock fields that do not affect execution, so they stay out of signatures
SIGNATURE_EXCLUDED = frozenset({"line_number", "hidden"})


VALID_DEVICES = {"halo", "stx", "krk", "rx7900xt", "rx9070xt", "r9700"}


@dataclass
class TestBlock:
    """Represents a single test block extracted from a playbook."""

    id: str
    platform: str = "all"  # inferred from surrounding @os: tags
    device: str = "all"  # inferred from surrounding @device: tags (comma-separated)
    timeout: int = 300
    workdir: Optional[str] = None
    continue_on_error: bool = False
    hidden: bool = False
    setup: Optional[str] = None
    language: str = "bash"
    code: str = ""
    line_number: int = 0


@dataclass
class TestResult:
    """Result of running a single test."""

    test_id: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    error_message: str = ""
    skipped: bool = False


@dataclass
class PlaybookTestSuite:
    """Collection of tests for a playbook."""

    playbook_id: str
    tests: list[TestBlock] = field(default_factory=list)
    results: list[TestResult] = field(default_factory=list)


def find_playbook_path(playbook_id: str, repo_root: Optional[Path] = None) -> Optional[Path]:
    """Find the playbook directory by ID."""
    # repo_root is injectable so the selector can read a base checkout too
    repo_root = repo_root or Path(__file__).parent.parent.parent

    # Check core and supplemental directories
    for category in ["core", "supplemental"]:
        playbook_path = repo_root / "playbooks" / category / playbook_id
        if playbook_path.exists() and (playbook_path / "README.md").exists():
            return playbook_path

    return None


def load_merged_metadata(locale: str, category: str, playbook_id: str, repo_root: Optional[Path] = None) -> dict:
    """Load localized metadata, optionally inheriting canonical English fields."""
    repo_root = repo_root or Path(__file__).parent.parent.parent
    localized_file = (
        repo_root / "localized-playbooks" / locale / category / playbook_id / "playbook.json"
    )
    english_file = repo_root / "playbooks" / category / playbook_id / "playbook.json"

    localized_metadata = {}
    if localized_file.is_file():
        localized_metadata = json.loads(localized_file.read_text(encoding="utf-8"))

    localized_only = localized_metadata.get("localized_only", True)
    if not isinstance(localized_only, bool):
        raise ValueError(f"'localized_only' in {localized_file} must be a boolean")

    metadata = {}
    if not localized_only and english_file.is_file():
        metadata.update(json.loads(english_file.read_text(encoding="utf-8")))
    metadata.update(localized_metadata)
    metadata["localized_only"] = localized_only

    if metadata.get("id") != playbook_id:
        raise ValueError(
            f"Metadata ID mismatch for '{playbook_id}': found {metadata.get('id')!r}"
        )
    if localized_only or not english_file.is_file():
        missing = sorted(
            {"id", "title", "description", "supported_platforms"} - metadata.keys()
        )
        if missing:
            kind = "Strict localized" if localized_only else "Localized-only"
            raise ValueError(
                f"{kind} playbook '{playbook_id}' is missing: {', '.join(missing)}"
            )
    return metadata


def materialize_localized_playbook(
    locale: str,
    playbook_id: str,
    destination: Path,
    localized_only: bool = True,
    repo_root: Optional[Path] = None,
) -> Path:
    """Build the effective localized playbook tree in ``destination``."""
    repo_root = repo_root or Path(__file__).parent.parent.parent
    matches = [
        repo_root / "localized-playbooks" / locale / category / playbook_id
        for category in ("core", "supplemental")
        if (repo_root / "localized-playbooks" / locale / category / playbook_id).is_dir()
    ]
    if not matches:
        raise ValueError(
            "Localized playbook directory does not exist: "
            f"localized-playbooks/{locale}/{{core,supplemental}}/{playbook_id}"
        )
    if len(matches) > 1:
        raise ValueError(
            f"Localized playbook ID '{playbook_id}' exists in both core and supplemental"
        )

    localized_source = matches[0]
    layers = [localized_source]
    if not localized_only:
        layers.insert(0, repo_root / "playbooks" / localized_source.parent.name / playbook_id)
    for layer in layers:
        if layer.is_dir():
            shutil.copytree(layer, destination, dirs_exist_ok=True)
    if not (destination / "README.md").is_file():
        raise ValueError(
            f"No effective README.md found for localized playbook "
            f"'{locale}/{localized_source.parent.name}/{playbook_id}'"
        )
    return destination


def load_dependency_registry(locale: str, localized_only: bool = True, repo_root: Optional[Path] = None) -> dict:
    """Load localized dependency metadata using the selected fallback policy."""
    repo_root = repo_root or Path(__file__).parent.parent.parent
    english = repo_root / "playbooks" / "dependencies" / "registry.json"
    localized = repo_root / "localized-playbooks" / locale / "dependencies" / "registry.json"
    registry_paths = (localized,) if localized_only else (english, localized)
    merged = {}
    for registry_path in registry_paths:
        if not registry_path.is_file():
            continue
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"Unable to read dependency registry {registry_path}: {error}"
            ) from error
        dependencies = registry.get("dependencies", {})
        if not isinstance(dependencies, dict):
            raise ValueError(f"'dependencies' in {registry_path} must be an object")
        merged.update(dependencies)
    return merged


def resolve_localized_require_tags(
    locale: str,
    content: str,
    localized_only: bool = True,
    repo_root: Optional[Path] = None,
) -> str:
    """Expand @require tags using localized dependency overlays."""
    repo_root = repo_root or Path(__file__).parent.parent.parent
    deps_map = load_dependency_registry(locale, localized_only, repo_root)
    localized_root = repo_root / "localized-playbooks" / locale / "dependencies"
    english_root = repo_root / "playbooks" / "dependencies"

    def replace(match: re.Match) -> str:
        parts = []
        for dep_id in (d.strip() for d in match.group(1).split(",") if d.strip()):
            dep_info = deps_map.get(dep_id)
            if not isinstance(dep_info, dict) or not dep_info.get("file"):
                if localized_only:
                    raise ValueError(
                        f"@require dependency '{dep_id}' is missing valid localized metadata"
                    )
                print(f"Warning: @require dependency '{dep_id}' not found in registry")
                continue
            relative_file = dep_info["file"]
            localized_candidate = localized_root / relative_file
            if localized_only and not localized_candidate.resolve().is_relative_to(
                localized_root.resolve()
            ):
                raise ValueError(
                    f"Localized dependency path escapes its directory: {relative_file!r}"
                )
            candidates = [localized_candidate]
            if not localized_only:
                candidates.append(english_root / relative_file)
            dep_file = next((candidate for candidate in candidates if candidate.is_file()), None)
            if dep_file is None:
                if localized_only:
                    raise ValueError(
                        f"Localized dependency file for '{dep_id}' was not found"
                    )
                print(f"Warning: dependency file for '{dep_id}' was not found")
                continue
            print(f"Resolved dependency '{dep_id}' from {dep_file}")
            parts.append(dep_file.read_text(encoding="utf-8"))
        return "\n".join(parts) if parts else match.group(0)

    return re.sub(r"<!-- @require:([a-z0-9-,]+) -->", replace, content)


def parse_test_attributes(attr_string: str) -> dict:
    """Parse test attributes from the @test tag."""
    attrs = {}

    # Match key=value or key="value with spaces"
    pattern = r'(\w+)=(?:"([^"]+)"|(\S+))'
    for match in re.finditer(pattern, attr_string):
        key = match.group(1)
        value = match.group(2) if match.group(2) else match.group(3)

        # Type conversion
        if key == "timeout":
            value = int(value)
        elif key == "continue_on_error":
            value = value.lower() == "true"
        elif key == "hidden":
            value = value.lower() == "true"

        attrs[key] = value

    return attrs


def extract_setup_definitions(content: str) -> dict[str, dict[str, str]]:
    """Extract reusable @setup definitions from README content.

    Supports @setup definitions wrapped in @os: blocks, where the platform is
    inferred from the surrounding tag.  Handles arbitrarily nested ``@os:``
    blocks (e.g. when ``@require`` injects dependency content that itself
    contains ``@os:`` sections) by using a stack-based parser.

        <!-- @os:windows -->
        <!-- @setup:id=activate-venv command="llm-env\\Scripts\\activate.bat" -->
        <!-- @os:end -->
        <!-- @os:linux -->
        <!-- @setup:id=activate-venv command="source llm-env/bin/activate" -->
        <!-- @os:end -->

    Definitions outside any @os: block apply to all platforms:
        <!-- @setup:id=some-setup command="some-command" -->

    Returns a dict mapping setup_id -> {platform: command}, e.g.:
        {"activate-venv": {"linux": "source llm-env/bin/activate", "windows": "llm-env\\Scripts\\activate.bat"}}
    """
    setup_defs: dict[str, dict[str, str]] = {}
    setup_pattern = r"<!-- @setup:([^>]+) -->"

    os_blocks = _find_nested_blocks(
        content,
        r"<!-- @os:(windows|linux) -->",
        "<!-- @os:end -->",
    )

    for setup_match in re.finditer(setup_pattern, content):
        match_pos = setup_match.start()
        attr_string = setup_match.group(1)
        attrs = parse_test_attributes(attr_string)

        setup_id = attrs.get("id")
        if not setup_id:
            line_number = content[:match_pos].count("\n") + 1
            print(
                f"Warning: @setup definition at line {line_number} missing 'id', skipping"
            )
            continue

        command = attrs.get("command")
        if not command:
            line_number = content[:match_pos].count("\n") + 1
            print(
                f"Warning: @setup '{setup_id}' at line {line_number} has no command"
            )
            continue

        # Determine platform from the innermost enclosing @os: block
        platform = None
        for value, start, end in os_blocks:
            if start <= match_pos < end:
                platform = value
                break  # blocks are sorted innermost-first

        if setup_id not in setup_defs:
            setup_defs[setup_id] = {}

        if platform:
            setup_defs[setup_id][platform] = command
        else:
            setup_defs[setup_id]["linux"] = command
            setup_defs[setup_id]["windows"] = command

    return setup_defs


def resolve_setup(
    setup_value: Optional[str],
    setup_defs: dict[str, dict[str, str]],
    target_platform: str,
) -> Optional[str]:
    """Resolve a setup attribute value.

    If the value matches a defined @setup id, returns the platform-specific
    command. Otherwise returns the raw value (backward compatible).
    """
    if not setup_value:
        return None

    if setup_value in setup_defs:
        platform_cmds = setup_defs[setup_value]
        resolved = platform_cmds.get(target_platform)
        if resolved:
            return resolved
        print(
            f"  Warning: Setup '{setup_value}' has no command for platform '{target_platform}'"
        )
        return None

    # Not a reference — treat as a raw shell command (backward compatible)
    return setup_value


def extract_var_definitions(content: str) -> dict[str, dict[str, str]]:
    """Extract reusable @var definitions from README content.

    The target device(s) for a definition can be specified two ways:

    1. An inline ``device=`` attribute on the @var tag itself (preferred, as it
       reads in a single line and renders cleanly on the website):

        <!-- @var:id=lemonade_model device=halo,halo_box value="gpt-oss-120b-mxfp-GGUF" -->
        <!-- @var:id=lemonade_model device=stx,krk,rx7900xt,rx9070xt value="gpt-oss-20b-mxfp4-GGUF" -->

    2. A surrounding @device: block, where the device(s) are inferred from the
       enclosing tag:

        <!-- @device:halo,halo_box -->
        <!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
        <!-- @device:end -->
        <!-- @device:stx,krk,rx7900xt,rx9070xt -->
        <!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
        <!-- @device:end -->

    The inline ``device=`` attribute takes precedence over the enclosing block.
    Comma-separated device lists fan out into one key per device in the
    returned mapping.

    Definitions with neither an inline ``device=`` nor an enclosing @device:
    block apply to all devices and are stored under the ``"all"`` key:
        <!-- @var:id=api_port value="13305" -->

    Returns a dict mapping var_id -> {device: value}, e.g.:
        {"lemonade_model": {
            "halo": "gpt-oss-120b-mxfp-GGUF",
            "halo_box": "gpt-oss-120b-mxfp-GGUF",
            "stx": "gpt-oss-20b-mxfp4-GGUF",
            ...
        }}
    """
    var_defs: dict[str, dict[str, str]] = {}
    var_pattern = r"<!-- @var:([^>]+) -->"

    device_blocks = _find_nested_blocks(
        content,
        r"<!-- @device:([\w,]+) -->",
        "<!-- @device:end -->",
    )

    for var_match in re.finditer(var_pattern, content):
        match_pos = var_match.start()
        attr_string = var_match.group(1)
        attrs = parse_test_attributes(attr_string)

        var_id = attrs.get("id")
        if not var_id:
            line_number = content[:match_pos].count("\n") + 1
            print(
                f"Warning: @var definition at line {line_number} missing 'id', skipping"
            )
            continue

        value = attrs.get("value")
        if value is None:
            line_number = content[:match_pos].count("\n") + 1
            print(
                f"Warning: @var '{var_id}' at line {line_number} has no value"
            )
            continue

        # Determine target devices: an inline device= attribute takes
        # precedence; otherwise fall back to the innermost enclosing
        # @device: block.
        device_value: Optional[str] = attrs.get("device")
        if device_value is None:
            for dev_val, start, end in device_blocks:
                if start <= match_pos < end:
                    device_value = dev_val
                    break  # blocks are sorted innermost-first

        if var_id not in var_defs:
            var_defs[var_id] = {}

        if device_value:
            for dev in (d.strip() for d in device_value.split(",")):
                if dev:
                    var_defs[var_id][dev] = value
        else:
            var_defs[var_id]["all"] = value

    return var_defs


def substitute_vars(
    code: str,
    var_defs: dict[str, dict[str, str]],
    target_device: Optional[str],
    test_id: str,
) -> str:
    """Substitute ``${name}`` placeholders in *code* using *var_defs*.

    Only placeholders whose name matches a declared @var id are substituted;
    every other ``${...}`` (e.g. ordinary shell variable references) is left
    untouched. Resolution for a declared name prefers the value mapped to
    *target_device*, falling back to the ``"all"`` value if present.

    Raises ``ValueError`` if a declared placeholder cannot be resolved for the
    active device — silent substitution of an empty string would cause subtle
    test failures downstream.
    """
    if not var_defs:
        return code

    placeholder_pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

    def _replace(match: re.Match) -> str:
        name = match.group(1)
        if name not in var_defs:
            return match.group(0)
        mapping = var_defs[name]
        resolved: Optional[str] = None
        if target_device and target_device in mapping:
            resolved = mapping[target_device]
        elif "all" in mapping:
            resolved = mapping["all"]
        if resolved is None:
            device_repr = target_device or "<unspecified>"
            available = ", ".join(sorted(mapping.keys())) or "<none>"
            raise ValueError(
                f"Test '{test_id}' references @var '${{{name}}}' but no value "
                f"is defined for device '{device_repr}'. "
                f"Available device(s) for this var: {available}."
            )
        return resolved

    return placeholder_pattern.sub(_replace, code)


def resolve_require_tags(content: str, repo_root: Optional[Path] = None) -> str:
    """Resolve @require tags by inlining dependency content.

    Finds ``<!-- @require:dep-id -->`` tags in the README content and replaces
    them with the actual dependency file contents from the central
    ``playbooks/dependencies/`` folder.  This allows the test extractor to
    discover @test blocks that live inside shared dependency files.
    """
    repo_root = repo_root or Path(__file__).parent.parent.parent
    dependencies_root = repo_root / "playbooks" / "dependencies"
    registry_path = dependencies_root / "registry.json"

    if not registry_path.exists():
        return content

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return content

    deps_map = registry.get("dependencies", {})

    require_pattern = r"<!-- @require:([a-z0-9-,]+) -->"

    def _replace_require(match: re.Match) -> str:
        dep_ids = [d.strip() for d in match.group(1).split(",") if d.strip()]
        parts: list[str] = []
        for dep_id in dep_ids:
            dep_info = deps_map.get(dep_id)
            if not dep_info:
                print(f"Warning: @require dependency '{dep_id}' not found in registry")
                continue
            dep_file = dependencies_root / dep_info["file"]
            if not dep_file.exists():
                print(f"Warning: Dependency file '{dep_file}' does not exist")
                continue
            parts.append(dep_file.read_text(encoding="utf-8"))
        return "\n".join(parts) if parts else match.group(0)

    return re.sub(require_pattern, _replace_require, content)


def _find_nested_blocks(
    content: str,
    open_pattern: str,
    close_literal: str,
) -> list[tuple[str, int, int]]:
    """Find properly nested tag blocks using a stack-based parser.

    Returns a list of ``(value, block_start, block_end)`` tuples sorted by
    span size ascending (innermost first).  ``value`` is the capture group
    from the opening tag (e.g. ``"linux"`` for ``<!-- @os:linux -->``).
    """
    open_re = re.compile(open_pattern)
    close_re = re.compile(re.escape(close_literal))

    # Collect close positions first so we can skip any open match that
    # coincides exactly with a close. This guards against permissive open
    # patterns (e.g. ``@device:([\w,]+)``) that would otherwise also match
    # the close tag ``@device:end`` and corrupt the nesting stack.
    close_positions = {m.start() for m in close_re.finditer(content)}

    events: list[tuple[int, str, str]] = []  # (pos, 'open'|'close', value)
    for m in open_re.finditer(content):
        if m.start() in close_positions:
            continue
        events.append((m.start(), "open", m.group(1)))
    for pos in close_positions:
        events.append((pos, "close", ""))
    events.sort(key=lambda e: e[0])

    stack: list[tuple[str, int]] = []  # (value, start_pos)
    blocks: list[tuple[str, int, int]] = []
    for pos, kind, value in events:
        if kind == "open":
            stack.append((value, pos))
        elif kind == "close" and stack:
            open_value, open_pos = stack.pop()
            close_end = pos + len(close_literal)
            blocks.append((open_value, open_pos, close_end))

    blocks.sort(key=lambda b: b[2] - b[1])
    return blocks


def _infer_platform(content: str, position: int) -> str:
    """Infer the platform for a test based on surrounding @os: tags.

    Handles arbitrarily nested ``@os:`` blocks by finding the innermost
    enclosing block that contains *position*.
    """
    blocks = _find_nested_blocks(
        content,
        r"<!-- @os:(windows|linux) -->",
        "<!-- @os:end -->",
    )
    for value, start, end in blocks:
        if start <= position < end:
            return value
    return "all"


def _infer_device(content: str, position: int) -> str:
    """Infer the target device(s) for a test based on surrounding @device: tags.

    Handles arbitrarily nested ``@device:`` blocks by finding the innermost
    enclosing block that contains *position*.
    """
    blocks = _find_nested_blocks(
        content,
        r"<!-- @device:([\w,]+) -->",
        "<!-- @device:end -->",
    )
    for value, start, end in blocks:
        if start <= position < end:
            return value
    return "all"


def extract_tests(readme_path: Path, target_platform: str, target_device: Optional[str] = None,
                  repo_root: Optional[Path] = None, locale: str = "",
                  localized_only: bool = True) -> list[TestBlock]:
    """Extract test blocks from a README.md file."""
    content = readme_path.read_text(encoding="utf-8")

    # Resolve @require tags so tests inside dependencies are discovered
    if locale:
        content = resolve_localized_require_tags(
            locale, content, localized_only, repo_root=repo_root
        )
    else:
        content = resolve_require_tags(content, repo_root)

    tests = []

    # Parse reusable setup definitions first
    setup_defs = extract_setup_definitions(content)
    if setup_defs:
        print(
            f"Found {len(setup_defs)} setup definition(s): {', '.join(setup_defs.keys())}"
        )

    # Parse reusable device-aware @var definitions
    var_defs = extract_var_definitions(content)
    if var_defs:
        print(
            f"Found {len(var_defs)} var definition(s): {', '.join(var_defs.keys())}"
        )

    # Pattern to match test blocks:
    # <!-- @test:id=name ... -->
    # ```language
    # code
    # ```
    # <!-- @test:end -->
    pattern = r"<!-- @test:([^>]+) -->\s*```(\w+)?\s*\n(.*?)```\s*<!-- @test:end -->"

    for match in re.finditer(pattern, content, re.DOTALL):
        attr_string = match.group(1)
        language = match.group(2) or "bash"
        code = match.group(3).strip()

        # Calculate line number for error reporting
        line_number = content[: match.start()].count("\n") + 1

        attrs = parse_test_attributes(attr_string)

        if "id" not in attrs:
            print(
                f"Warning: Test block at line {line_number} missing 'id' attribute, skipping"
            )
            continue

        # Infer platform and device from surrounding tags
        inferred_platform = _infer_platform(content, match.start())
        inferred_device = _infer_device(content, match.start())

        test = TestBlock(
            id=attrs["id"],
            platform=inferred_platform,
            device=inferred_device,
            timeout=attrs.get("timeout", 300),
            workdir=attrs.get("workdir"),
            continue_on_error=attrs.get("continue_on_error", False),
            hidden=attrs.get("hidden", False),
            setup=resolve_setup(attrs.get("setup"), setup_defs, target_platform),
            language=language,
            code=code,
            line_number=line_number,
        )

        # Filter by platform
        if test.platform != "all" and test.platform != target_platform:
            print(
                f"Skipping test '{test.id}' (platform={test.platform}, running on {target_platform})"
            )
            continue

        # Filter by device
        if target_device and test.device != "all":
            allowed_devices = {d.strip() for d in test.device.split(",")}
            if target_device not in allowed_devices:
                print(
                    f"Skipping test '{test.id}' (device={test.device}, running on {target_device})"
                )
                continue

        # Substitute ${var} placeholders using device-aware @var definitions.
        # Only declared var names are touched; ordinary shell ${env} references
        # are preserved. Unresolved declared references raise loudly.
        if var_defs:
            test.code = substitute_vars(test.code, var_defs, target_device, test.id)

        tests.append(test)

    # Deduplicate tests by ID, keeping the first occurrence (README order).
    # Duplicates arise when @require tags inline the same dependency content
    # into multiple @os: blocks, or when device variants share an ID.
    seen_ids: set[str] = set()
    unique_tests: list[TestBlock] = []
    for t in tests:
        if t.id not in seen_ids:
            seen_ids.add(t.id)
            unique_tests.append(t)
    return unique_tests


def run_test(
    test: TestBlock,
    playbook_path: Path,
    results_dir: Path,
) -> TestResult:
    """Execute a single test block."""
    print(f"\n{'='*60}")
    print(f"Running test: {test.id}")
    print(f"Language: {test.language}")
    print(f"Timeout: {test.timeout}s")
    if test.setup:
        print(f"Setup: {test.setup}")
    print(f"{'='*60}")

    # Determine working directory
    if test.workdir:
        workdir = playbook_path / "assets" / test.workdir
    else:
        workdir = playbook_path / "assets"

    # Ensure working directory exists
    workdir.mkdir(parents=True, exist_ok=True)

    # Process #hide lines: strip the marker for execution, annotate in coverage log
    code_lines = test.code.splitlines()
    effective_lines = []
    for line in code_lines:
        if line.rstrip().endswith("#hide"):
            # Strip the #hide marker so it doesn't interfere with execution
            effective_lines.append(re.sub(r"\s*#hide\s*$", "", line))
        else:
            effective_lines.append(line)
    effective_code = "\n".join(effective_lines)

    # Determine shell and script extension based on language and platform
    is_windows = sys.platform == "win32"

    # If setup is provided, prepend it to shell-based tests or wrap Python tests
    setup_prefix = test.setup if test.setup else None

    if test.language in ["bash", "sh", "shell"]:
        if is_windows:
            if setup_prefix:
                # Use cmd.exe instead of PowerShell so .bat setup commands
                # (e.g. venv activation) run in the same session and their
                # environment changes persist for subsequent commands.
                shell_cmd = ["cmd", "/c"]
                lines = [l for l in effective_code.strip().splitlines() if l.strip()]
                script_content = " && ".join([setup_prefix] + lines)
            else:
                shell_cmd = ["powershell", "-Command"]
                script_content = effective_code
        else:
            shell_cmd = ["bash", "-c"]
            script_content = effective_code
            if setup_prefix:
                script_content = f"{setup_prefix}\n{script_content}"
    elif test.language in ["cmd", "batch"]:
        shell_cmd = ["cmd", "/c"]
        script_content = effective_code
        if setup_prefix:
            # Use && so setup and code share the same cmd.exe session
            lines = [l for l in effective_code.strip().splitlines() if l.strip()]
            script_content = " && ".join([setup_prefix] + lines)
    elif test.language in ["powershell", "pwsh", "ps1"]:
        shell_cmd = ["powershell", "-Command"]
        script_content = effective_code
        if setup_prefix:
            script_content = f"{setup_prefix}\n{script_content}"
    elif test.language == "python":
        # For Python code blocks, write to temp file and execute
        script_file = results_dir / f"test_{test.id}.py"
        script_file.write_text(effective_code, encoding="utf-8")
        if setup_prefix:
            # Wrap in a shell so setup commands (e.g. venv activation) run first
            if is_windows:
                shell_cmd = ["cmd", "/c"]
                script_content = f'{setup_prefix} && python "{script_file}"'
            else:
                shell_cmd = ["bash", "-c"]
                script_content = f'{setup_prefix} && python "{script_file}"'
        else:
            shell_cmd = ["python", str(script_file)]
            script_content = None
    else:
        # Default to shell execution
        if is_windows:
            if setup_prefix:
                shell_cmd = ["cmd", "/c"]
                lines = [l for l in effective_code.strip().splitlines() if l.strip()]
                script_content = " && ".join([setup_prefix] + lines)
            else:
                shell_cmd = ["powershell", "-Command"]
                script_content = effective_code
        else:
            shell_cmd = ["bash", "-c"]
            script_content = effective_code
            if setup_prefix:
                script_content = f"{setup_prefix}\n{script_content}"

    # Build the command
    if script_content is not None:
        if shell_cmd == ["cmd", "/c"]:
            # Pass as a single string so subprocess sends it directly to
            # CreateProcess.  Using a list here would go through list2cmdline
            # which escapes inner quotes with \" — but cmd.exe doesn't
            # recognise \" as an escape, causing garbled file paths.
            cmd = f"cmd /c {script_content}"
        else:
            cmd = shell_cmd + [script_content]
    else:
        cmd = shell_cmd

    print(f"Working directory: {workdir}")
    cmd_preview = cmd if isinstance(cmd, str) else ' '.join(cmd[:2])
    print(f"Command: {cmd_preview[:60]}...")

    # Display code with #hide lines annotated for coverage view
    display_lines = []
    for line in code_lines:
        if line.rstrip().endswith("#hide"):
            clean = re.sub(r"\s*#hide\s*$", "", line)
            display_lines.append(f"  [hidden] {clean}")
        else:
            display_lines.append(f"           {line}")
    display_code = "\n".join(display_lines)
    print(f"\nCode:\n{display_code[:500]}{'...' if len(display_code) > 500 else ''}\n")

    # Execute the test
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=test.timeout,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        duration = time.time() - start_time

        # Save output to files
        stdout_file = results_dir / f"{test.id}_stdout.txt"
        stderr_file = results_dir / f"{test.id}_stderr.txt"
        stdout_file.write_text(result.stdout, encoding="utf-8")
        stderr_file.write_text(result.stderr, encoding="utf-8")

        success = result.returncode == 0

        print(f"Exit code: {result.returncode}")
        print(f"Duration: {duration:.2f}s")
        console_log_chars = 10000
        if result.stdout:
            print(f"STDOUT (last {console_log_chars} chars):\n{result.stdout[-console_log_chars:]}")
        if result.stderr:
            print(f"STDERR (last {console_log_chars} chars):\n{result.stderr[-console_log_chars:]}")

        return TestResult(
            test_id=test.id,
            success=success,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=duration,
        )

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        error_msg = f"Test timed out after {test.timeout} seconds"
        print(f"TIMEOUT: {error_msg}")
        return TestResult(
            test_id=test.id,
            success=False,
            exit_code=-1,
            stdout="",
            stderr="",
            duration=duration,
            error_message=error_msg,
        )
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Test execution failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        return TestResult(
            test_id=test.id,
            success=False,
            exit_code=-1,
            stdout="",
            stderr="",
            duration=duration,
            error_message=error_msg,
        )


def write_failure_metadata(
    results_dir: Path,
    playbook_id: str,
    platform: str,
    device: Optional[str],
    test: TestBlock,
    result: TestResult,
) -> None:
    """Persist a structured record of a failed test for downstream consumers.

    The CI ``Create failure issues`` step reads these files to build GitHub
    issues that contain everything needed to reproduce the failure (the full
    test code, the recorded logs, and the matrix entry that produced it).
    """
    failures_dir = results_dir / "failures"
    failures_dir.mkdir(parents=True, exist_ok=True)

    # Bound the captured log size so issue bodies stay within GitHub's limits.
    max_log_chars = 10000
    stdout_excerpt = result.stdout[-max_log_chars:] if result.stdout else ""
    stderr_excerpt = result.stderr[-max_log_chars:] if result.stderr else ""

    payload = {
        "playbook_id": playbook_id,
        "platform": platform,
        "device": device,
        "test": {
            "id": test.id,
            "language": test.language,
            "code": test.code,
            "setup": test.setup,
            "workdir": test.workdir,
            "timeout": test.timeout,
            "platform": test.platform,
            "device": test.device,
            "line_number": test.line_number,
        },
        "result": {
            "exit_code": result.exit_code,
            "duration": result.duration,
            "error_message": result.error_message,
            "stdout_excerpt": stdout_excerpt,
            "stderr_excerpt": stderr_excerpt,
            "stdout_truncated": bool(result.stdout) and len(result.stdout) > max_log_chars,
            "stderr_truncated": bool(result.stderr) and len(result.stderr) > max_log_chars,
        },
    }

    failure_file = failures_dir / f"{test.id}.json"
    failure_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _run_playbook_tests_at_path(
    playbook_id: str,
    platform: str,
    device: Optional[str],
    playbook_path: Path,
    locale: str = "",
    localized_only: bool = True,
) -> bool:
    """Run all tests for a playbook."""
    print(f"\n{'#'*60}")
    print(f"# Testing Playbook: {playbook_id}")
    print(f"# Platform: {platform}")
    if device:
        print(f"# Device: {device}")
    print(f"{'#'*60}\n")

    readme_path = playbook_path / "README.md"
    print(f"Playbook path: {playbook_path}")
    print(f"README path: {readme_path}")

    # Create results directory (use absolute path so it works from any workdir)
    results_dir = Path.cwd() / "test-results" / playbook_id
    results_dir.mkdir(parents=True, exist_ok=True)

    # Extract tests
    tests = extract_tests(
        readme_path, platform, device, locale=locale, localized_only=localized_only
    )

    if not tests:
        print(f"\nNo tests found for platform '{platform}' in {playbook_id}")
        # Write empty results
        (results_dir / "no_tests.txt").write_text(
            f"No tests found for platform '{platform}' in playbook '{playbook_id}'",
            encoding="utf-8",
        )
        if locale:
            (results_dir / "locale.txt").write_text(f"{locale}\n", encoding="utf-8")
        return True

    print(f"\nFound {len(tests)} test(s) to run (in README order):")
    for test in tests:
        device_info = f", device={test.device}" if test.device != "all" else ""
        print(
            f"  - {test.id} (platform={test.platform}{device_info}, timeout={test.timeout}s)"
        )

    # Run tests
    suite = PlaybookTestSuite(playbook_id=playbook_id, tests=tests)
    all_passed = True

    skip_remaining = False

    for test in tests:
        if skip_remaining:
            print(f"\n{'='*60}")
            print(f"Skipping test: {test.id} (previous test failed)")
            print(f"{'='*60}")
            suite.results.append(
                TestResult(
                    test_id=test.id,
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="",
                    duration=0.0,
                    error_message="Skipped due to previous test failure",
                    skipped=True,
                )
            )
            continue

        result = run_test(test, playbook_path, results_dir)
        suite.results.append(result)

        if not result.success and not result.skipped:
            write_failure_metadata(
                results_dir, playbook_id, platform, device, test, result
            )
            if test.continue_on_error:
                print(
                    f"\nTest '{test.id}' failed but continue_on_error=true, continuing..."
                )
            else:
                all_passed = False
                skip_remaining = True
                print(
                    f"\nTest '{test.id}' failed — skipping remaining tests in this playbook."
                )

    # Write summary
    summary = {
        "playbook_id": playbook_id,
        "locale": locale,
        "platform": platform,
        "total_tests": len(tests),
        "passed": sum(1 for r in suite.results if r.success),
        "failed": sum(1 for r in suite.results if not r.success and not r.skipped),
        "skipped": sum(1 for r in suite.results if r.skipped),
        "results": [
            {
                "test_id": r.test_id,
                "success": r.success,
                "skipped": r.skipped,
                "exit_code": r.exit_code,
                "duration": r.duration,
                "error_message": r.error_message,
            }
            for r in suite.results
        ],
    }

    summary_file = results_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if locale:
        (results_dir / "locale.txt").write_text(f"{locale}\n", encoding="utf-8")

    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Playbook: {playbook_id}")
    print(f"Platform: {platform}")
    print(f"Total: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"{'='*60}\n")

    for result in suite.results:
        if result.skipped:
            status = "[SKIP]"
        elif result.success:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        print(f"  {status}: {result.test_id} ({result.duration:.2f}s)")
        if result.error_message:
            print(f"         {result.error_message}")

    return all_passed


def run_playbook_tests(
    playbook_id: str,
    platform: str,
    device: Optional[str] = None,
    locale: str = "",
    localized_only: bool = True,
) -> bool:
    """Run canonical or localized tests for one playbook."""
    if not locale:
        playbook_path = find_playbook_path(playbook_id)
        if not playbook_path:
            print(f"Error: Playbook '{playbook_id}' not found")
            return False
        return _run_playbook_tests_at_path(
            playbook_id, platform, device, playbook_path
        )

    temp_parent = Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir())
    try:
        temp_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="localized-playbook-", dir=temp_parent
        ) as temp_dir:
            playbook_path = materialize_localized_playbook(
                locale, playbook_id, Path(temp_dir), localized_only
            )
            return _run_playbook_tests_at_path(
                playbook_id,
                platform,
                device,
                playbook_path,
                locale=locale,
                localized_only=localized_only,
            )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return False


# --- Test selection support -------------------------------------------------
# The matrix builder (build_test_matrix.py) imports these to compute, for one
# checkout, what each (playbook, platform, device) entry would execute. It runs
# them against both the head tree and a materialised base tree using THIS
# extractor, so only content differs between the two sides. A separate harness
# path check forces the full matrix whenever the extractor itself changed, which
# is what makes applying one extractor to both trees safe.

def list_playbook_ids(repo_root: Path) -> list[str]:
    ids = set()
    for category in ("core", "supplemental"):
        base = repo_root / "playbooks" / category
        if base.is_dir():
            ids.update(p.name for p in base.iterdir() if (p / "playbook.json").exists())
    return sorted(ids)


def build_matrix_entries(repo_root: Path) -> list[dict]:
    """Expand every playbook.json into CI matrix entries."""
    entries = []
    for playbook_id in list_playbook_ids(repo_root):
        for category in ("core", "supplemental"):
            meta_file = repo_root / "playbooks" / category / playbook_id / "playbook.json"
            if not meta_file.exists():
                continue
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"Warning: cannot read {meta_file}: {exc}", file=sys.stderr)
                break
            required = meta.get("required_platforms", {})
            for device, platforms in meta.get("tested_platforms", {}).items():
                for platform in platforms:
                    os_label = "Windows" if platform == "windows" else "Linux"
                    entries.append({
                        "playbook": playbook_id,
                        "platform": platform,
                        "arch": device,
                        "runner": json.dumps(["self-hosted", os_label, device]),
                        "runner_labels": f"self-hosted,{os_label},{device}",
                        "required": platform in set(required.get(device, [])),
                    })
            break
    return entries


def list_localized_playbook_ids(repo_root: Path, locale: str) -> list[str]:
    ids = set()
    for category in ("core", "supplemental"):
        base = repo_root / "localized-playbooks" / locale / category
        if base.is_dir():
            ids.update(p.name for p in base.iterdir() if (p / "playbook.json").exists())
    return sorted(ids)


def build_localized_matrix_entries(repo_root: Path, locale: str) -> list[dict]:
    """Expand localized metadata into the self-hosted CI matrix format."""
    slug = re.sub(r"[^a-z0-9]+", "-", locale.lower()).strip("-")
    if not slug:
        raise ValueError(f"Unable to generate a runner label from locale {locale!r}")
    if not (repo_root / "localized-playbooks" / locale).is_dir():
        raise ValueError(
            f"Localized content directory does not exist: localized-playbooks/{locale}"
        )

    entries = []
    for playbook_id in list_localized_playbook_ids(repo_root, locale):
        for category in ("core", "supplemental"):
            localized_dir = repo_root / "localized-playbooks" / locale / category / playbook_id
            if not localized_dir.is_dir():
                continue
            metadata = load_merged_metadata(locale, category, playbook_id, repo_root)
            localized_only = metadata["localized_only"]
            if localized_only and not (localized_dir / "README.md").is_file():
                raise ValueError(
                    f"Localized README.md not found for strict localized playbook "
                    f"'{locale}/{category}/{playbook_id}'"
                )
            if not localized_only and not (
                (localized_dir / "README.md").is_file()
                or (repo_root / "playbooks" / category / playbook_id / "README.md").is_file()
            ):
                raise ValueError(
                    f"No effective README.md found for localized playbook "
                    f"'{locale}/{category}/{playbook_id}'"
                )
            tested = metadata.get("tested_platforms", {})
            required = metadata.get("required_platforms", {})
            if not tested:
                print(
                    f"Skipping '{playbook_id}': no tested_platforms metadata",
                    file=sys.stderr,
                )
                break
            if not isinstance(tested, dict):
                raise ValueError(
                    f"'tested_platforms' for '{playbook_id}' must be an object"
                )
            if not isinstance(required, dict):
                raise ValueError(
                    f"'required_platforms' for '{playbook_id}' must be an object"
                )
            for device, platforms in tested.items():
                if not isinstance(device, str) or not device:
                    raise ValueError(
                        f"Invalid device name for '{playbook_id}': {device!r}"
                    )
                if not isinstance(platforms, list):
                    raise ValueError(
                        f"tested_platforms.{device} for '{playbook_id}' must be an array"
                    )
                required_for_device = required.get(device, [])
                if not isinstance(required_for_device, list):
                    raise ValueError(
                        f"required_platforms.{device} for '{playbook_id}' must be an array"
                    )
                for platform in platforms:
                    if platform not in {"windows", "linux"}:
                        raise ValueError(
                            f"Unsupported platform '{platform}' for '{playbook_id}'"
                        )
                    label = f"localized-{slug}-{device}-{platform}"
                    entries.append({
                        "locale": locale,
                        "playbook": playbook_id,
                        "platform": platform,
                        "arch": device,
                        "runner": json.dumps(["self-hosted", label]),
                        "runner_label": label,
                        "runner_labels": f"self-hosted,{label}",
                        "required": platform in set(required_for_device),
                        "localized_only": localized_only,
                    })
            break
    return entries


def assets_digest(assets_dir: Path) -> Optional[str]:
    """Digest an assets tree. None means "cannot be signed", which forces a run.

    A symlink escaping the tree is unsignable: its target content is not covered
    here, so a change to that target would otherwise be invisible.
    """
    if not assets_dir.is_dir():
        return ""
    root = assets_dir.resolve()
    digest = hashlib.sha256()
    for path in sorted(assets_dir.rglob("*")):
        rel = str(path.relative_to(assets_dir)).replace(os.sep, "/")
        if path.is_symlink():
            try:
                target = path.resolve()
            except OSError:
                return None
            if not target.is_relative_to(root):
                return None
            digest.update(rel.encode("utf-8") + b"\x02" + os.readlink(path).encode("utf-8"))
        elif path.is_file():
            digest.update(rel.encode("utf-8"))
            digest.update(b"\x01" if os.access(path, os.X_OK) else b"\x00")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def entry_signature(repo_root: Path, playbook_id: str, platform: str,
                    device: str) -> Optional[str]:
    """Signature of what a checkout would execute for one entry, or None.

    None means the signature could not be computed (missing playbook, extraction
    error); the caller must then treat the entry as not-provably-equal and run it.
    """
    playbook_path = find_playbook_path(playbook_id, repo_root=repo_root)
    if playbook_path is None:
        return None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            tests = extract_tests(playbook_path / "README.md", platform, device,
                                  repo_root=repo_root)
    except Exception:
        return None
    # @require inlines shared dependency markdown, so its assets are in scope too
    own = assets_digest(playbook_path / "assets")
    shared = assets_digest(repo_root / "playbooks" / "dependencies" / "assets")
    if own is None or shared is None:
        return None
    payload = [
        {k: v for k, v in dataclasses.asdict(t).items() if k not in SIGNATURE_EXCLUDED}
        for t in tests
    ]
    blob = json.dumps([payload, own, shared], sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Run playbook tests")
    parser.add_argument("--playbook", required=True, help="Playbook ID to test")
    parser.add_argument(
        "--platform",
        required=True,
        choices=["windows", "linux"],
        help="Target platform",
    )
    parser.add_argument(
        "--device",
        choices=sorted(VALID_DEVICES),
        default=None,
        help="Target device (filters @device: blocks)",
    )
    parser.add_argument(
        "--locale",
        nargs="?",
        const="",
        default="",
        help=(
            "Localized content locale; an omitted value selects English "
            "(supports PowerShell, which drops explicit empty arguments)"
        ),
    )
    parser.add_argument(
        "--localized-only",
        type=str.lower,
        choices=["true", "false"],
        default="true",
        help="Disable canonical fallback for localized content",
    )
    args = parser.parse_args()

    success = run_playbook_tests(
        args.playbook,
        args.platform,
        args.device,
        locale=args.locale,
        localized_only=args.localized_only == "true",
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
