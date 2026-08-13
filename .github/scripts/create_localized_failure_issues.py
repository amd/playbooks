#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Create GitHub issues for failed localized playbook tests."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import create_failure_issues as canonical


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--playbook", required=True)
    parser.add_argument("--locale", required=True)
    parser.add_argument(
        "--localized-only",
        required=True,
        choices=["true", "false"],
    )
    parser.add_argument("--results-dir", default="test-results")
    parser.add_argument(
        "--workflow-file",
        default="test-localized-playbooks.yml",
    )
    parser.add_argument("--runner-name", default=os.environ.get("RUNNER_NAME", ""))
    parser.add_argument("--runner-labels", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--sha", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    canonical_build_title = canonical.build_title
    canonical_render_body = canonical.render_body

    def build_localized_title(playbook: str, test_id: str, device: str, platform: str) -> str:
        return canonical_build_title(f"{args.locale}/{playbook}", test_id, device, platform)

    def render_localized_body(**kwargs) -> str:
        body = canonical_render_body(**kwargs)
        failure = kwargs["failure"]
        playbook = failure["playbook_id"]
        platform = failure["platform"]
        device = failure.get("device") or "all"

        body = body.replace(
            "**Test Playbooks** workflow",
            "**Test Localized Playbooks** workflow",
            1,
        )
        body = body.replace(
            f"- **Playbook:** `{playbook}`",
            f"- **Playbook:** `{playbook}`\n- **Locale:** `{args.locale}`",
            1,
        )
        body = body.replace(
            f"-f playbook_id={playbook}",
            f"-f playbook_id={playbook} -f locale={args.locale}",
            1,
        )
        body = body.replace(
            f"python .github/scripts/run_playbook_tests.py --playbook {playbook} "
            f"--platform {platform} --device {device}",
            f"python .github/scripts/run_localized_playbook_tests.py "
            f"--locale {args.locale} --playbook {playbook} "
            f"--platform {platform} --device {device} "
            f"--localized-only {args.localized_only}",
            1,
        )
        body = body.replace(
            f"`playbooks/*/{playbook}/README.md`",
            f"`localized-playbooks/{args.locale}/*/{playbook}/README.md`",
            1,
        )
        return body

    canonical.build_title = build_localized_title
    canonical.render_body = render_localized_body

    runner_labels = [
        label.strip()
        for label in args.runner_labels.split(",")
        if label.strip()
    ]
    token = os.environ.get("GITHUB_TOKEN", "")

    created = canonical.process_failures(
        repo=args.repo,
        token=token,
        workflow_file=args.workflow_file,
        results_root=Path(args.results_dir),
        playbook=args.playbook,
        runner_labels=runner_labels,
        runner_name=args.runner_name,
        run_url=args.run_url,
        sha=args.sha,
        dry_run=args.dry_run,
    )

    print(f"\nDone. Issues created: {created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
