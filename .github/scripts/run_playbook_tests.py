#!/usr/bin/env python3
"""
Playbook Test Runner
====================

Extracts and executes test blocks from playbook README.md files.

Test blocks wrap existing code blocks using HTML comments that are invisible
to the website but can be parsed and executed by CI:

    <!-- @test:id=unique-test-name platform=windows -->
    ```bash
    pip install transformers
    ```
    <!-- @test:end -->

Tests can be chained using the `depends_on` attribute to create test sequences
where later tests only run if their dependencies pass:

    <!-- @test:id=install-deps platform=all -->
    ```bash
    pip install transformers
    ```
    <!-- @test:end -->

    <!-- @test:id=run-script platform=all depends_on=install-deps -->
    ```bash
    python run_llm.py --help
    ```
    <!-- @test:end -->

Supported test attributes:
    - id: Unique identifier for the test (required)
    - platform: windows, linux, or all (default: all)
    - timeout: Maximum execution time in seconds (default: 300)
    - workdir: Working directory relative to playbook assets folder
    - continue_on_error: true/false - whether to continue if this test fails (default: false)
    - depends_on: Comma-separated list of test IDs that must pass before this test runs
    - hidden: true/false - if true, hides the code block from the website (default: false)
    - setup: Shell commands to run before the test script (e.g. venv activation).
             For Python tests, wraps execution in a shell that runs the setup first:
                 setup="source llm-env/bin/activate"  →  bash -c "source llm-env/bin/activate && python <script>"
             For shell tests, the setup commands are prepended to the script body.

Setup attribute:
    The `setup` attribute lets you specify shell commands (e.g. venv activation)
    that run before the test script. This is especially useful for Python code
    blocks which are otherwise executed directly with `python <script>`:

        <!-- @test:id=verify-imports platform=all setup="source llm-env/bin/activate" -->
        ```python
        import torch
        print(f"PyTorch version: {torch.__version__}")
        ```
        <!-- @test:end -->

    The runner expands this to: `bash -c "source llm-env/bin/activate && python test_verify-imports.py"`
    On Windows, it uses PowerShell instead of bash.

    For shell-based tests, the setup commands are prepended to the script body.

Inline #hide marker:
    Lines ending with `#hide` inside a code block are executed by the test runner
    but should be stripped from the rendered website view. This lets you add
    prerequisite commands (e.g. venv activation) that the reader doesn't need to see
    repeated, without hiding the entire block:

        <!-- @test:id=install-deps platform=all depends_on=create-venv -->
        ```bash
        source llm-env/bin/activate #hide
        pip install transformers
        ```
        <!-- @test:end -->

    In the coverage/CI log output, #hide lines are prefixed with [hidden] so
    reviewers can see what runs invisibly on the website.

Usage:
    python run_playbook_tests.py --playbook pytorch-rocm-llms --platform windows
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


@dataclass
class TestBlock:
    """Represents a single test block extracted from a playbook."""

    id: str
    platform: str = "all"
    timeout: int = 300
    workdir: Optional[str] = None
    continue_on_error: bool = False
    depends_on: list[str] = field(default_factory=list)
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
        elif key == "depends_on":
            # Parse comma-separated list of dependencies
            value = [dep.strip() for dep in value.split(",") if dep.strip()]

        attrs[key] = value

    return attrs


def extract_tests(readme_path: Path, target_platform: str) -> list[TestBlock]:
    """Extract test blocks from a README.md file."""
    content = readme_path.read_text(encoding="utf-8")
    tests = []

    # Pattern to match test blocks:
    # <!-- @test:id=name platform=windows ... -->
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

        test = TestBlock(
            id=attrs["id"],
            platform=attrs.get("platform", "all"),
            timeout=attrs.get("timeout", 300),
            workdir=attrs.get("workdir"),
            continue_on_error=attrs.get("continue_on_error", False),
            depends_on=attrs.get("depends_on", []),
            hidden=attrs.get("hidden", False),
            setup=attrs.get("setup"),
            language=language,
            code=code,
            line_number=line_number,
        )

        # Filter by platform
        if test.platform == "all" or test.platform == target_platform:
            tests.append(test)
        else:
            print(
                f"Skipping test '{test.id}' (platform={test.platform}, running on {target_platform})"
            )

    return tests


def topological_sort_tests(tests: list[TestBlock]) -> list[TestBlock]:
    """
    Sort tests based on their dependencies using topological sort.
    Tests with no dependencies come first, then tests that depend on them, etc.
    Preserves original order for tests at the same dependency level.
    """
    # Build a map of test ID to test
    test_map = {t.id: t for t in tests}

    # Track visited and result
    visited = set()
    temp_visited = set()
    result = []

    def visit(test_id: str):
        if test_id in temp_visited:
            raise ValueError(f"Circular dependency detected involving test '{test_id}'")
        if test_id in visited:
            return
        if test_id not in test_map:
            # Dependency not found (might be filtered out by platform)
            print(f"Warning: Dependency '{test_id}' not found, ignoring")
            return

        temp_visited.add(test_id)
        test = test_map[test_id]

        # Visit dependencies first
        for dep_id in test.depends_on:
            visit(dep_id)

        temp_visited.remove(test_id)
        visited.add(test_id)
        result.append(test)

    # Visit all tests in their original order
    for test in tests:
        visit(test.id)

    return result


def run_test(
    test: TestBlock,
    playbook_path: Path,
    results_dir: Path,
    results_map: dict[str, TestResult],
) -> TestResult:
    """Execute a single test block."""
    print(f"\n{'='*60}")
    print(f"Running test: {test.id}")
    print(f"Language: {test.language}")
    print(f"Timeout: {test.timeout}s")
    if test.depends_on:
        print(f"Dependencies: {', '.join(test.depends_on)}")
    if test.setup:
        print(f"Setup: {test.setup}")
    print(f"{'='*60}")

    # Check dependencies
    for dep_id in test.depends_on:
        if dep_id in results_map:
            dep_result = results_map[dep_id]
            if not dep_result.success:
                skip_msg = f"Skipped: dependency '{dep_id}' failed"
                print(f"SKIPPED: {skip_msg}")
                return TestResult(
                    test_id=test.id,
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="",
                    duration=0,
                    error_message=skip_msg,
                    skipped=True,
                )
            if dep_result.skipped:
                skip_msg = f"Skipped: dependency '{dep_id}' was skipped"
                print(f"SKIPPED: {skip_msg}")
                return TestResult(
                    test_id=test.id,
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr="",
                    duration=0,
                    error_message=skip_msg,
                    skipped=True,
                )
        else:
            # Dependency not found - might have been filtered by platform
            print(
                f"Warning: Dependency '{dep_id}' not found in results, proceeding anyway"
            )

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
            shell_cmd = ["powershell", "-Command"]
            script_content = effective_code
        else:
            shell_cmd = ["bash", "-c"]
            script_content = effective_code
        # Prepend setup commands to the shell script body
        if setup_prefix:
            script_content = f"{setup_prefix}\n{script_content}"
    elif test.language in ["cmd", "batch"]:
        shell_cmd = ["cmd", "/c"]
        script_content = effective_code
        if setup_prefix:
            script_content = f"{setup_prefix}\n{script_content}"
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
                shell_cmd = ["powershell", "-Command"]
                script_content = f'{setup_prefix}; python "{script_file}"'
            else:
                shell_cmd = ["bash", "-c"]
                script_content = f'{setup_prefix} && python "{script_file}"'
        else:
            shell_cmd = ["python", str(script_file)]
            script_content = None
    else:
        # Default to shell execution
        if is_windows:
            shell_cmd = ["powershell", "-Command"]
        else:
            shell_cmd = ["bash", "-c"]
        script_content = effective_code
        if setup_prefix:
            script_content = f"{setup_prefix}\n{script_content}"

    # Build the command
    if script_content is not None:
        cmd = shell_cmd + [script_content]
    else:
        cmd = shell_cmd

    print(f"Working directory: {workdir}")
    print(f"Command: {' '.join(cmd[:2])}...")

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


def run_playbook_tests(playbook_id: str, platform: str) -> bool:
    """Run all tests for a playbook."""
    print(f"\n{'#'*60}")
    print(f"# Testing Playbook: {playbook_id}")
    print(f"# Platform: {platform}")
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
    tests = extract_tests(readme_path, platform)

    if not tests:
        print(f"\nNo tests found for platform '{platform}' in {playbook_id}")
        # Write empty results
        (results_dir / "no_tests.txt").write_text(
            f"No tests found for platform '{platform}' in playbook '{playbook_id}'",
            encoding="utf-8",
        )
        return True

    # Sort tests by dependencies
    try:
        tests = topological_sort_tests(tests)
    except ValueError as e:
        print(f"Error: {e}")
        return False

    print(f"\nFound {len(tests)} test(s) to run (in dependency order):")
    for test in tests:
        deps = f" (depends on: {', '.join(test.depends_on)})" if test.depends_on else ""
        print(
            f"  - {test.id} (platform={test.platform}, timeout={test.timeout}s){deps}"
        )

    # Run tests
    suite = PlaybookTestSuite(playbook_id=playbook_id, tests=tests)
    results_map: dict[str, TestResult] = {}
    all_passed = True

    for test in tests:
        result = run_test(test, playbook_path, results_dir, results_map)
        suite.results.append(result)
        results_map[test.id] = result

        if not result.success and not result.skipped:
            if test.continue_on_error:
                print(
                    f"\nTest '{test.id}' failed but continue_on_error=true, continuing..."
                )
            else:
                all_passed = False

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
    args = parser.parse_args()

    success = run_playbook_tests(args.playbook, args.platform)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
