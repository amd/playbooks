<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Contributing to AMD Playbooks

We accept playbook proposals from the community, from AMD partners and ISVs, and
from AMD employees. Every proposal goes through the same AMD review before any
code is written.

The review exists because a playbook is a supported artifact, not a blog post.
Each published playbook runs in CI on real AMD hardware across Windows and Linux,
gets translated into 29 locales, and is maintained as the underlying tools change.
AMD decides which topics carry that cost, and we would rather tell you no on an
issue than on a pull request you already finished.

## Reporting a bug in a playbook

[Open a bug report](https://github.com/amd/playbooks/issues/new?template=bug_report.yml)
if a step does not work, a command fails, output does not match what the playbook
says to expect, a link is broken, or content is out of date. Tell us which
playbook, which step, and which device and OS you were on.

If the tool the playbook uses fails the same way outside the playbook steps, the
bug is probably in that tool. Please report it to that project's own tracker so
its maintainers see it.

## Proposing a new playbook

**Do not open a pull request for a new playbook first.** Start with an abstract.

1. **Submit a proposal.** Open a
   [playbook proposal](https://github.com/amd/playbooks/issues/new?template=playbook_proposal.yml).
   It is a short form: a title, a three-to-five sentence abstract, what the
   reader will learn, and the target hardware, operating systems, difficulty,
   and time. Keep the abstract to three to five sentences: reviewers want a
   pitch, not a draft.
2. **We review it.** Playbook maintainers read the proposal and label the issue:

   | Label | Meaning |
   |-------|---------|
   | `status::approved` | Go ahead and write it. Open a pull request that links back to the issue. |
   | `status::needs-info` | We have questions. Answer in a comment and we will look again. |
   | `status::declined` | Not one we will publish. The issue is closed with a reason. |

3. **Write it, tests included.** Follow the
   [Playbook Creation Guide](playbooks/README.md) for structure, metadata, and
   platform tags, and the [AMD Branding Guide](playbooks/AMD_BRANDING_GUIDE.md)
   for product naming. Link the pull request to the approved proposal issue.

   **The author writes the tests**, in the same pull request. See the
   [Playbook Testing Guide](playbooks/TESTING.md): wrap the commands in `@test`
   tags, and list the device and OS combinations CI should run under
   `tested_platforms` in `playbook.json`. There is no separate test suite to
   write, because the tests are the playbook's own steps. Run them locally
   before you push:

   ```bash
   python .github/scripts/run_playbook_tests.py --playbook <your-playbook-id> --platform linux
   ```

   If you cannot test on a device you want to target, say so in the pull request
   rather than leaving the device out.
4. **We test it.** CI runs your tests on the AMD self-hosted runners for the
   devices the playbook targets. Expect review comments, and expect to iterate
   on the hardware combinations you could not test yourself.

A pull request that adds a playbook without an approved proposal will be closed
with a pointer back to this page.

## What reviewers look for

- **A payoff, not a setup guide.** The reader should see something happen: an
  image appears, a model answers, a server comes alive. If the playbook ends at
  "installation complete," it is not a playbook.
- **It teaches.** Explain why the steps work, not only which buttons to click.
- **It does not duplicate what we have.** Check the
  [published playbooks](README.md#available-playbooks) first. Overlap is fine if
  you can say what this adds.
- **It runs on AMD hardware we can test.** Name the devices from
  `playbook.json` that the playbook targets, and tell us which of them you can
  test on yourself. A gap is something we plan around, not a reason to leave the
  device out.
- **Its dependencies are reachable.** Gated models, click-through licenses, and
  paid services are not disqualifying, but they change how we test and how far
  the playbook reaches, so say so up front.
- **It is licensable.** Content must be yours or properly attributed, free of
  anything confidential or under NDA, and publishable under this repository's
  [MIT license](LICENSE).

## Other contributions

Fixes to existing playbooks, corrections, and improvements to repository tooling
do not need a proposal. Open a pull request directly, or file a bug first if you
want to discuss the fix before writing it.

## Questions

For anything that is not a bug report or a proposal, join the
[AMD Developer Discord](https://discord.com/invite/amd-dev).
