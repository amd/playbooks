#!/usr/bin/env python3
"""
Playbook Validation Script

This script validates that all playbooks:
1. Have the expected file structure (README.md, playbook.json, optional platform.md, optional assets/)
2. Follow the contract defined in website/src/types/playbook.ts
3. Have valid JSON in playbook.json
4. Have consistent IDs (folder name should match id in playbook.json)
5. Have asset files within size limits (max 500 KB per file)
"""

import json
import os
import sys
import io
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
PLAYBOOKS_ROOT = SCRIPT_DIR.parent.parent / "playbooks"
CATEGORIES = ["core", "supplemental", "backup"]

# Allowed files/folders in a playbook directory
ALLOWED_ITEMS = {"README.md", "playbook.json", "platform.md", "assets"}

# Required fields in playbook.json (based on PlaybookMeta interface)
REQUIRED_FIELDS = ["id", "title", "description", "time", "platforms", "published"]

# Valid values for enum fields
VALID_PLATFORMS = ["windows", "linux"]
VALID_DIFFICULTIES = ["beginner", "intermediate", "advanced"]

# Asset constraints
MAX_ASSET_SIZE_KB = 500
MAX_ASSET_SIZE_BYTES = MAX_ASSET_SIZE_KB * 1024

# ============================================================================
# Styling
# ============================================================================


class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


def styled(text: str, *styles: str) -> str:
    return "".join(styles) + text + Colors.RESET


def print_header(title: str) -> None:
    print()
    print(styled("═" * 70, Colors.CYAN))
    print(styled(f"  {title}", Colors.BOLD, Colors.CYAN))
    print(styled("═" * 70, Colors.CYAN))
    print()


def print_section(title: str) -> None:
    print(styled(f"\n▶ {title}", Colors.BOLD, Colors.BLUE))
    print(styled("─" * 50, Colors.DIM))


def print_success(message: str) -> None:
    print(styled("  ✓ ", Colors.GREEN) + message)


def print_error(message: str) -> None:
    print(styled("  ✗ ", Colors.RED, Colors.BOLD) + styled(message, Colors.RED))


def print_warning(message: str) -> None:
    print(styled("  ⚠ ", Colors.YELLOW) + styled(message, Colors.YELLOW))


def print_info(message: str) -> None:
    print(styled("  ℹ ", Colors.BLUE) + message)


# ============================================================================
# Validation Logic
# ============================================================================


@dataclass
class ValidationIssue:
    playbook_path: str
    message: str


@dataclass
class ValidationResult:
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    playbooks_checked: int = 0

    def add_error(self, playbook_path: str, message: str) -> None:
        self.errors.append(ValidationIssue(playbook_path, message))

    def add_warning(self, playbook_path: str, message: str) -> None:
        self.warnings.append(ValidationIssue(playbook_path, message))

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


def validate_file_structure(
    playbook_path: Path, playbook_name: str, result: ValidationResult
) -> None:
    """Validates the file structure of a playbook directory."""
    items = [item.name for item in playbook_path.iterdir()]

    # Check for required files
    if "README.md" not in items:
        result.add_error(playbook_name, "Missing required file: README.md")

    if "playbook.json" not in items:
        result.add_error(playbook_name, "Missing required file: playbook.json")

    # Check for unexpected files/folders
    for item in items:
        if item not in ALLOWED_ITEMS:
            result.add_error(
                playbook_name,
                f'Unexpected item in playbook directory: "{item}"\n'
                f"       Allowed items: {', '.join(sorted(ALLOWED_ITEMS))}",
            )

    # If assets folder exists, make sure it contains files
    assets_path = playbook_path / "assets"
    if assets_path.exists():
        assets_items = list(assets_path.iterdir())
        if len(assets_items) == 0:
            result.add_warning(playbook_name, "Assets folder exists but is empty")


def validate_asset_sizes(
    playbook_path: Path, playbook_name: str, result: ValidationResult
) -> None:
    """Validates that all assets are within the size limit."""
    assets_path = playbook_path / "assets"

    if not assets_path.exists():
        return

    for asset in assets_path.iterdir():
        if not asset.is_file():
            continue

        file_size = asset.stat().st_size
        if file_size > MAX_ASSET_SIZE_BYTES:
            size_kb = file_size / 1024
            result.add_error(
                playbook_name,
                f'Asset file too large: "{asset.name}"\n'
                f"       Size: {size_kb:.1f} KB\n"
                f"       Maximum allowed: {MAX_ASSET_SIZE_KB} KB\n"
                "       Please compress or resize the image.",
            )


def validate_playbook_json(
    playbook_path: Path, playbook_name: str, folder_name: str, result: ValidationResult
) -> None:
    """Validates playbook.json against the contract."""
    json_path = playbook_path / "playbook.json"

    if not json_path.exists():
        return  # Already reported in structure validation

    # Read and parse JSON
    try:
        content = json_path.read_text(encoding="utf-8")
    except Exception as e:
        result.add_error(playbook_name, f"Cannot read playbook.json: {e}")
        return

    try:
        meta = json.loads(content)
    except json.JSONDecodeError as e:
        result.add_error(
            playbook_name,
            f"Invalid JSON in playbook.json: {e}\n"
            "       This will cause the website to fail loading this playbook.",
        )
        return

    # Check required fields
    for field_name in REQUIRED_FIELDS:
        if field_name not in meta:
            result.add_error(
                playbook_name,
                f'Missing required field in playbook.json: "{field_name}"\n'
                f"       Required fields: {', '.join(REQUIRED_FIELDS)}",
            )

    # Validate ID matches folder name
    if "id" in meta and meta["id"] != folder_name:
        result.add_error(
            playbook_name,
            f"Playbook ID mismatch:\n"
            f'       Folder name: "{folder_name}"\n'
            f'       ID in playbook.json: "{meta["id"]}"\n'
            "       These must match for the website routing to work correctly.",
        )

    # Validate field types
    if "title" in meta and not isinstance(meta["title"], str):
        result.add_error(
            playbook_name,
            f'Field "title" must be a string, got: {type(meta["title"]).__name__}',
        )

    if "description" in meta and not isinstance(meta["description"], str):
        result.add_error(
            playbook_name,
            f'Field "description" must be a string, got: {type(meta["description"]).__name__}',
        )

    if "time" in meta and not isinstance(meta["time"], (int, float)):
        result.add_error(
            playbook_name,
            f'Field "time" must be a number (minutes), got: {type(meta["time"]).__name__}',
        )

    if "published" in meta and not isinstance(meta["published"], bool):
        result.add_error(
            playbook_name,
            f'Field "published" must be a boolean, got: {type(meta["published"]).__name__}',
        )

    # Validate platforms array
    if "platforms" in meta:
        if not isinstance(meta["platforms"], list):
            result.add_error(
                playbook_name,
                f'Field "platforms" must be an array, got: {type(meta["platforms"]).__name__}',
            )
        else:
            if len(meta["platforms"]) == 0:
                result.add_error(
                    playbook_name,
                    'Field "platforms" cannot be empty - at least one platform is required',
                )
            for platform in meta["platforms"]:
                if platform not in VALID_PLATFORMS:
                    result.add_error(
                        playbook_name,
                        f'Invalid platform: "{platform}"\n'
                        f"       Valid platforms: {', '.join(VALID_PLATFORMS)}",
                    )

    # Validate difficulty
    if "difficulty" in meta and meta["difficulty"] not in VALID_DIFFICULTIES:
        result.add_error(
            playbook_name,
            f'Invalid difficulty: "{meta["difficulty"]}"\n'
            f"       Valid difficulties: {', '.join(VALID_DIFFICULTIES)}",
        )

    # Validate optional boolean fields
    if "isNew" in meta and not isinstance(meta["isNew"], bool):
        result.add_error(
            playbook_name,
            f'Field "isNew" must be a boolean, got: {type(meta["isNew"]).__name__}',
        )

    if "isFeatured" in meta and not isinstance(meta["isFeatured"], bool):
        result.add_error(
            playbook_name,
            f'Field "isFeatured" must be a boolean, got: {type(meta["isFeatured"]).__name__}',
        )

    # Validate tags array
    if "tags" in meta:
        if not isinstance(meta["tags"], list):
            result.add_error(
                playbook_name,
                f'Field "tags" must be an array, got: {type(meta["tags"]).__name__}',
            )
        else:
            for tag in meta["tags"]:
                if not isinstance(tag, str):
                    result.add_error(
                        playbook_name,
                        f"All tags must be strings, got: {type(tag).__name__}",
                    )

    # Validate coverImage exists if specified
    if "coverImage" in meta and meta["coverImage"]:
        cover_path = playbook_path / meta["coverImage"]
        if not cover_path.exists():
            result.add_error(
                playbook_name,
                f'Cover image not found: "{meta["coverImage"]}"\n'
                f"       Expected location: {cover_path}",
            )

    # Validate prerequisites array
    if "prerequisites" in meta:
        if not isinstance(meta["prerequisites"], list):
            result.add_error(
                playbook_name,
                f'Field "prerequisites" must be an array, got: {type(meta["prerequisites"]).__name__}',
            )
        else:
            for prereq in meta["prerequisites"]:
                if not isinstance(prereq, str):
                    result.add_error(
                        playbook_name,
                        f"All prerequisites must be strings (playbook IDs), got: {type(prereq).__name__}",
                    )


def validate_playbook(
    playbook_path: Path, folder_name: str, category: str, result: ValidationResult
) -> None:
    """Validates a single playbook."""
    playbook_name = f"{category}/{folder_name}"

    validate_file_structure(playbook_path, playbook_name, result)
    validate_asset_sizes(playbook_path, playbook_name, result)
    validate_playbook_json(playbook_path, playbook_name, folder_name, result)

    result.playbooks_checked += 1


def validate_all_playbooks() -> None:
    """Main validation function."""
    result = ValidationResult()

    print_header("PLAYBOOK VALIDATION")

    if not PLAYBOOKS_ROOT.exists():
        print_error(f"Playbooks directory not found: {PLAYBOOKS_ROOT}")
        sys.exit(1)

    for category in CATEGORIES:
        category_path = PLAYBOOKS_ROOT / category

        if not category_path.exists():
            print_info(f'Category "{category}" not found, skipping...')
            continue

        print_section(f"Category: {category}")

        playbook_folders = [f for f in category_path.iterdir() if f.is_dir()]

        if len(playbook_folders) == 0:
            print_info(f"No playbooks found in {category}/")
            continue

        for folder in sorted(playbook_folders, key=lambda f: f.name):
            print_info(f"Checking {folder.name}...")
            validate_playbook(folder, folder.name, category, result)

    # Print results
    print_header("VALIDATION RESULTS")

    if result.has_warnings:
        print(
            styled(
                f"\n⚠ Warnings ({len(result.warnings)}):", Colors.BOLD, Colors.YELLOW
            )
        )
        print(styled("─" * 50, Colors.DIM))
        for warning in result.warnings:
            print(styled(f"\n  {warning.playbook_path}:", Colors.YELLOW, Colors.BOLD))
            print(f"    {warning.message}")

    if result.has_errors:
        print(styled(f"\n✗ Errors ({len(result.errors)}):", Colors.BOLD, Colors.RED))
        print(styled("─" * 50, Colors.DIM))
        for error in result.errors:
            print(styled(f"\n  {error.playbook_path}:", Colors.RED, Colors.BOLD))
            print(f"    {error.message}")

    # Summary
    print()
    print(styled("═" * 70, Colors.CYAN))
    print(styled("  SUMMARY", Colors.BOLD, Colors.CYAN))
    print(styled("═" * 70, Colors.CYAN))

    print(
        f"\n  Playbooks checked: {styled(str(result.playbooks_checked), Colors.BOLD)}"
    )
    warning_color = Colors.YELLOW if result.has_warnings else Colors.GREEN
    error_color = Colors.RED if result.has_errors else Colors.GREEN
    print(f"  Warnings:          {styled(str(len(result.warnings)), warning_color)}")
    print(f"  Errors:            {styled(str(len(result.errors)), error_color)}")

    if result.has_errors:
        print(
            styled(
                "\n\n  ╔══════════════════════════════════════════════════════════════════╗",
                Colors.RED,
            )
        )
        print(
            styled(
                "  ║                    VALIDATION FAILED                              ║",
                Colors.RED,
                Colors.BOLD,
            )
        )
        print(
            styled(
                "  ║                                                                  ║",
                Colors.RED,
            )
        )
        print(
            styled(
                "  ║  Please fix the errors above before merging.                    ║",
                Colors.RED,
            )
        )
        print(
            styled(
                "  ║                                                                  ║",
                Colors.RED,
            )
        )
        print(
            styled(
                "  ║  Playbook Contract Reference:                                   ║",
                Colors.RED,
            )
        )
        print(
            styled(
                "  ║  → website/src/types/playbook.ts                                ║",
                Colors.RED,
            )
        )
        print(
            styled(
                "  ╚══════════════════════════════════════════════════════════════════╝",
                Colors.RED,
            )
        )
        print()
        sys.exit(1)
    else:
        print(
            styled(
                "\n\n  ╔══════════════════════════════════════════════════════════════════╗",
                Colors.GREEN,
            )
        )
        print(
            styled(
                "  ║                    VALIDATION PASSED                              ║",
                Colors.GREEN,
                Colors.BOLD,
            )
        )
        print(
            styled(
                "  ║                                                                  ║",
                Colors.GREEN,
            )
        )
        print(
            styled(
                "  ║  All playbooks follow the expected structure and contract.      ║",
                Colors.GREEN,
            )
        )
        print(
            styled(
                "  ╚══════════════════════════════════════════════════════════════════╝",
                Colors.GREEN,
            )
        )
        print()


if __name__ == "__main__":
    validate_all_playbooks()
