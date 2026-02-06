#!/usr/bin/env python3
"""
Playbook Test Runner
====================

Extracts and executes test blocks from playbook README.md files.

Test blocks are defined using HTML comments that are invisible to the website
but can be parsed and executed by CI:

    <!-- @test:id=unique-test-name platform=windows -->
    ```bash
    pip install transformers
    ```
    <!-- @test:end -->

Supported test attributes:
    - id: Unique identifier for the test (required)
    - platform: windows, linux, or all (default: all)
    - timeout: Maximum execution time in seconds (default: 300)
    - workdir: Working directory relative to playbook assets folder
    - continue_on_error: true/false - whether to continue if this test fails (default: false)

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


def run_test(test: TestBlock, playbook_path: Path, results_dir: Path) -> TestResult:
    """Execute a single test block."""
    print(f"\n{'='*60}")
    print(f"Running test: {test.id}")
    print(f"Language: {test.language}")
    print(f"Timeout: {test.timeout}s")
    print(f"{'='*60}")

    # Determine working directory
    if test.workdir:
        workdir = playbook_path / "assets" / test.workdir
    else:
        workdir = playbook_path / "assets"

    # Ensure working directory exists
    workdir.mkdir(parents=True, exist_ok=True)

    # Determine shell and script extension based on language and platform
    is_windows = sys.platform == "win32"

    if test.language in ["bash", "sh", "shell"]:
        if is_windows:
            # Use PowerShell on Windows for bash-like commands
            shell_cmd = ["powershell", "-Command"]
            script_content = test.code
        else:
            shell_cmd = ["bash", "-c"]
            script_content = test.code
    elif test.language in ["cmd", "batch"]:
        shell_cmd = ["cmd", "/c"]
        script_content = test.code
    elif test.language in ["powershell", "pwsh", "ps1"]:
        shell_cmd = ["powershell", "-Command"]
        script_content = test.code
    elif test.language == "python":
        # For Python code blocks, write to temp file and execute
        script_file = results_dir / f"test_{test.id}.py"
        script_file.write_text(test.code, encoding="utf-8")
        shell_cmd = ["python", str(script_file)]
        script_content = None
    else:
        # Default to shell execution
        if is_windows:
            shell_cmd = ["powershell", "-Command"]
        else:
            shell_cmd = ["bash", "-c"]
        script_content = test.code

    # Build the command
    if script_content is not None:
        cmd = shell_cmd + [script_content]
    else:
        cmd = shell_cmd

    print(f"Working directory: {workdir}")
    print(f"Command: {' '.join(cmd[:2])}...")
    print(f"\nCode:\n{test.code[:500]}{'...' if len(test.code) > 500 else ''}\n")

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

    # Create results directory
    results_dir = Path("test-results") / playbook_id
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

    print(f"\nFound {len(tests)} test(s) to run:")
    for test in tests:
        print(f"  - {test.id} (platform={test.platform}, timeout={test.timeout}s)")

    # Run tests
    suite = PlaybookTestSuite(playbook_id=playbook_id, tests=tests)
    all_passed = True

    for test in tests:
        result = run_test(test, playbook_path, results_dir)
        suite.results.append(result)

        if not result.success:
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
        "failed": sum(1 for r in suite.results if not r.success),
        "results": [
            {
                "test_id": r.test_id,
                "success": r.success,
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
    print(f"{'='*60}\n")

    for result in suite.results:
        status = "✓ PASS" if result.success else "✗ FAIL"
        print(f"  {status}: {result.test_id} ({result.duration:.2f}s)")
        if result.error_message:
            print(f"         Error: {result.error_message}")

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
