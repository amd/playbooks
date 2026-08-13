#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Localized adapter for the canonical OrchestrAI PR-comment report."""

import argparse
import contextlib
import io
import sys

import orchestrai_report as canonical


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--locale", required=True)
    args, canonical_args = parser.parse_known_args()
    sys.argv = [sys.argv[0], *canonical_args]

    canonical.MARKER = "<!-- orchestrai-localized-orc-report -->"
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        canonical.main()
    print(output.getvalue().replace(
        "### OrchestrAI results",
        f"### Localized OrchestrAI results ({args.locale})",
        1,
    ), end="")


if __name__ == "__main__":
    main()
