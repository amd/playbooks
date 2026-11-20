# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

import sys

for _stream in (sys.stdout, sys.stderr):  # Windows consoles may not print the lab's emojis
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
