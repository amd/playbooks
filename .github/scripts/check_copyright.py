#!/usr/bin/env python3

"""
Copyright Notice Checker

This script validates that files contain the required AMD copyright notice.
It checks only files that typically require copyright notices and skips
files in excluded directories and file types.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# File extensions that require copyright notices
COPYRIGHT_REQUIRED_EXTENSIONS = {
    '.py': {
        'format': 'hash',
        'header': '# Copyright Advanced Micro Devices, Inc.\n#\n# SPDX-License-Identifier: MIT\n'
    },
    '.sh': {
        'format': 'hash',
        'header': '# Copyright Advanced Micro Devices, Inc.\n#\n# SPDX-License-Identifier: MIT\n'
    },
    '.ts': {
        'format': 'slash',
        'header': '// Copyright Advanced Micro Devices, Inc.\n//\n// SPDX-License-Identifier: MIT\n'
    },
    '.tsx': {
        'format': 'slash',
        'header': '// Copyright Advanced Micro Devices, Inc.\n//\n// SPDX-License-Identifier: MIT\n'
    },
    '.js': {
        'format': 'slash',
        'header': '// Copyright Advanced Micro Devices, Inc.\n//\n// SPDX-License-Identifier: MIT\n'
    },
    '.mjs': {
        'format': 'slash',
        'header': '// Copyright Advanced Micro Devices, Inc.\n//\n// SPDX-License-Identifier: MIT\n'
    }
}

# File extensions to skip (don't need copyright)
SKIP_EXTENSIONS = {
    '.json', '.yml', '.yaml', '.md', '.txt', '.csv',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot',
    '.lock', '.log', '.gitignore', '.gitkeep'
}

# Directories to skip
SKIP_DIRECTORIES = {
    'website',
    'node_modules',
    '.git',
    '.github/workflows',  # Skip workflow files
    'assets'  # Skip asset directories
}

def should_skip_file(file_path: str) -> bool:
    """Check if a file should be skipped based on path or extension."""
    path = Path(file_path)
    
    # Skip files in excluded directories
    for part in path.parts:
        if part in SKIP_DIRECTORIES:
            return True
    
    # Skip files with excluded extensions
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    
    # Skip files without extensions unless they're known script files
    if not path.suffix:
        # Check if it's a shell script without extension
        try:
            with open(path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if not first_line.startswith('#!'):
                    return True
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            return True
    
    return False

def check_copyright(file_path: str, require_amd: bool = False) -> Optional[str]:
    """
    Check if file has proper copyright notice.
    
    Args:
        file_path: Path to the file to check
        require_amd: If True, requires AMD copyright. If False, accepts any valid copyright.
    
    Returns:
        None if copyright is present, error message if missing
    """
    path = Path(file_path)
    
    if not path.exists() or path.is_dir():
        return None
    
    extension = path.suffix.lower()
    
    # Handle files without extensions (potential shell scripts)
    if not extension:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!/bin/bash') or first_line.startswith('#!/bin/sh'):
                    extension = '.sh'
                else:
                    return None
        except (UnicodeDecodeError, FileNotFoundError):
            return None
    
    if extension not in COPYRIGHT_REQUIRED_EXTENSIONS:
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return f"Could not read file: {file_path}"
    
    # Check for AMD copyright specifically
    amd_copyright_patterns = [
        'Copyright Advanced Micro Devices, Inc.',
        'Copyright (C) Advanced Micro Devices, Inc.',
        'Copyright(C) Advanced Micro Devices, Inc.',
        'Copyright © Advanced Micro Devices, Inc.',
    ]
    
    # Check for any valid copyright (must be at start of line or after comment char)
    general_copyright_patterns = []
    
    # Check for copyright statements that appear to be actual copyright notices
    lines = content.splitlines()
    for line in lines[:20]:  # Check first 20 lines only
        line_stripped = line.strip()
        # For hash comments
        if (line_stripped.startswith('# Copyright ') or 
            line_stripped.startswith('#Copyright ') or
            line_stripped == '# Copyright' or
            line_stripped == '#Copyright'):
            general_copyright_patterns.append('valid_copyright_found')
            break
        # For slash comments  
        if (line_stripped.startswith('// Copyright ') or 
            line_stripped.startswith('//Copyright ') or
            line_stripped == '// Copyright' or
            line_stripped == '//Copyright'):
            general_copyright_patterns.append('valid_copyright_found')
            break
        # For HTML comments in markdown
        if ('<!--' in line_stripped and 'Copyright' in line_stripped):
            general_copyright_patterns.append('valid_copyright_found')
            break
    
    has_amd_copyright = any(pattern in content for pattern in amd_copyright_patterns)
    has_any_copyright = len(general_copyright_patterns) > 0  # Check if we found any valid copyright
    has_mit_license = 'SPDX-License-Identifier: MIT' in content
    
    config = COPYRIGHT_REQUIRED_EXTENSIONS[extension]
    
    if require_amd:
        # AMD employee - require AMD copyright and MIT license
        if not has_amd_copyright or not has_mit_license:
            return f"Missing AMD copyright notice. Please add at the top of the file:\n\n{config['header']}"
    else:
        # External contributor - require any copyright and MIT license
        if not has_any_copyright or not has_mit_license:
            if config['format'] == 'hash':
                example = "# Copyright Your Name\n#\n# SPDX-License-Identifier: MIT\n"
            else:
                example = "// Copyright Your Name\n//\n// SPDX-License-Identifier: MIT\n"
            
            return f"Missing copyright notice. Please add at the top of the file:\n\n{example}\n\nOr for AMD contributions:\n\n{config['header']}"
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Check copyright notices in files')
    parser.add_argument('--changed-files', help='Newline-separated list of changed files')
    parser.add_argument('--require-amd', action='store_true', help='Require AMD copyright format')
    parser.add_argument('files', nargs='*', help='Specific files to check')
    
    args = parser.parse_args()
    
    files_to_check = []
    
    if args.changed_files:
        files_to_check.extend(args.changed_files.strip().split('\n'))
    
    if args.files:
        files_to_check.extend(args.files)
    
    if not files_to_check:
        print("No files to check")
        return 0
    
    # Filter out files that should be skipped
    eligible_files = [f for f in files_to_check if f.strip() and not should_skip_file(f.strip())]
    
    if not eligible_files:
        print("No eligible files found that require copyright notices")
        return 0
    
    print(f"Checking copyright notices in {len(eligible_files)} files...")
    
    errors = {}
    
    for file_path in eligible_files:
        file_path = file_path.strip()
        if not file_path:
            continue
            
        error = check_copyright(file_path, require_amd=args.require_amd)
        if error:
            errors[file_path] = error
    
    if errors:
        print("\n❌ Copyright Notice Errors Found:")
        print("=" * 50)
        
        for file_path, error in errors.items():
            print(f"\nFile: {file_path}")
            print(f"Error: {error}")
        
        print(f"\n{len(errors)} file(s) missing proper copyright notices.")
        print("\nFor Markdown files, use this format:")
        print("<!--")
        print("Copyright Your Name")
        print("")
        print("SPDX-License-Identifier: MIT")
        print("-->")
        
        return 1
    else:
        print(f"✅ All {len(eligible_files)} files have proper copyright notices!")
        return 0

if __name__ == "__main__":
    sys.exit(main())