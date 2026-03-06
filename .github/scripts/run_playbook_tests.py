#!/usr/bin/env python3
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
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


VALID_DEVICES = {"halo", "stx", "krk", "rx7900xt", "rx9070xt"}


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


def find_playbook_path(playbook_id: str) -> Optional[Path]:
    """Find the playbook directory by ID."""
    repo_root = Path(__file__).parent.parent.parent

    # Check core and supplemental directories
    for category in ["core", "supplemental"]:
        playbook_path = repo_root / "playbooks" / category / playbook_id
        if playbook_path.exists() and (playbook_path / "README.md").exists():
            return playbook_path

    return None


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
    inferred from the surrounding tag:

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

    # First, extract @setup definitions inside @os: blocks
    os_block_pattern = r"<!-- @os:(windows|linux) -->([\s\S]*?)<!-- @os:end -->"
    setup_pattern = r"<!-- @setup:([^>]+) -->"

    # Track which character ranges are inside @os: blocks
    os_ranges: list[tuple[int, int]] = []

    for os_match in re.finditer(os_block_pattern, content):
        platform = os_match.group(1)
        block_content = os_match.group(2)
        block_start = os_match.start()
        os_ranges.append((os_match.start(), os_match.end()))

        for setup_match in re.finditer(setup_pattern, block_content):
            attr_string = setup_match.group(1)
            attrs = parse_test_attributes(attr_string)

            setup_id = attrs.get("id")
            if not setup_id:
                abs_pos = block_start + setup_match.start()
                line_number = content[:abs_pos].count("\n") + 1
                print(
                    f"Warning: @setup definition at line {line_number} missing 'id', skipping"
                )
                continue

            command = attrs.get("command")
            if not command:
                abs_pos = block_start + setup_match.start()
                line_number = content[:abs_pos].count("\n") + 1
                print(
                    f"Warning: @setup '{setup_id}' at line {line_number} has no command"
                )
                continue

            if setup_id not in setup_defs:
                setup_defs[setup_id] = {}
            setup_defs[setup_id][platform] = command

    # Then, find @setup definitions outside any @os: block (applies to all platforms)
    for setup_match in re.finditer(setup_pattern, content):
        # Skip if this match falls within an @os: block
        match_pos = setup_match.start()
        inside_os_block = any(
            start <= match_pos < end for start, end in os_ranges
        )
        if inside_os_block:
            continue

        attr_string = setup_match.group(1)
        attrs = parse_test_attributes(attr_string)

        setup_id = attrs.get("id")
        if not setup_id:
            line_number = content[: match_pos].count("\n") + 1
            print(
                f"Warning: @setup definition at line {line_number} missing 'id', skipping"
            )
            continue

        command = attrs.get("command")
        if not command:
            line_number = content[: match_pos].count("\n") + 1
            print(
                f"Warning: @setup '{setup_id}' at line {line_number} has no command"
            )
            continue

        if setup_id not in setup_defs:
            setup_defs[setup_id] = {}
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


def resolve_require_tags(content: str) -> str:
    """Resolve @require tags by inlining dependency content.

    Finds ``<!-- @require:dep-id -->`` tags in the README content and replaces
    them with the actual dependency file contents from the central
    ``playbooks/dependencies/`` folder.  This allows the test extractor to
    discover @test blocks that live inside shared dependency files.
    """
    repo_root = Path(__file__).parent.parent.parent
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


def _infer_platform(content: str, position: int) -> str:
    """Infer the platform for a test based on surrounding @os: tags.

    If the test is inside an ``<!-- @os:windows -->`` block, returns "windows".
    If inside an ``<!-- @os:linux -->`` block, returns "linux".
    Otherwise returns "all".
    """
    os_block_pattern = r"<!-- @os:(windows|linux) -->([\s\S]*?)<!-- @os:end -->"
    for os_match in re.finditer(os_block_pattern, content):
        if os_match.start() <= position < os_match.end():
            return os_match.group(1)
    return "all"


def _infer_device(content: str, position: int) -> str:
    """Infer the target device(s) for a test based on surrounding @device: tags.

    If the test is inside a ``<!-- @device:halo,stx -->`` block, returns "halo,stx".
    If inside ``<!-- @device:halo -->`` returns "halo".
    Otherwise returns "all".
    """
    device_block_pattern = r"<!-- @device:([\w,]+) -->([\s\S]*?)<!-- @device:end -->"
    for m in re.finditer(device_block_pattern, content):
        if m.start() <= position < m.end():
            return m.group(1)
    return "all"


def extract_tests(readme_path: Path, target_platform: str, target_device: Optional[str] = None) -> list[TestBlock]:
    """Extract test blocks from a README.md file."""
    content = readme_path.read_text(encoding="utf-8")

    # Resolve @require tags so tests inside dependencies are discovered
    content = resolve_require_tags(content)

    tests = []

    # Parse reusable setup definitions first
    setup_defs = extract_setup_definitions(content)
    if setup_defs:
        print(
            f"Found {len(setup_defs)} setup definition(s): {', '.join(setup_defs.keys())}"
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

        tests.append(test)

    return tests


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
        if result.stdout:
            print(f"STDOUT (last 500 chars):\n{result.stdout[-500:]}")
        if result.stderr:
            print(f"STDERR (last 500 chars):\n{result.stderr[-500:]}")

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


def run_playbook_tests(playbook_id: str, platform: str, device: Optional[str] = None) -> bool:
    """Run all tests for a playbook."""
    print(f"\n{'#'*60}")
    print(f"# Testing Playbook: {playbook_id}")
    print(f"# Platform: {platform}")
    if device:
        print(f"# Device: {device}")
    print(f"{'#'*60}\n")

    # Find playbook
    playbook_path = find_playbook_path(playbook_id)
    if not playbook_path:
        print(f"Error: Playbook '{playbook_id}' not found")
        return False

    readme_path = playbook_path / "README.md"
    print(f"Playbook path: {playbook_path}")
    print(f"README path: {readme_path}")

    # Create results directory (use absolute path so it works from any workdir)
    results_dir = Path.cwd() / "test-results" / playbook_id
    results_dir.mkdir(parents=True, exist_ok=True)

    # Extract tests
    tests = extract_tests(readme_path, platform, device)

    if not tests:
        print(f"\nNo tests found for platform '{platform}' in {playbook_id}")
        # Write empty results
        (results_dir / "no_tests.txt").write_text(
            f"No tests found for platform '{platform}' in playbook '{playbook_id}'",
            encoding="utf-8",
        )
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
    args = parser.parse_args()

    success = run_playbook_tests(args.playbook, args.platform, args.device)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
