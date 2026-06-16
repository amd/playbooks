<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Localization Strategy: China

Two options for localizing `amd/playbooks` into Simplified Chinese (`zh-CN`) for the China market. Each option is a full operating model with its own ownership, workflow, and infrastructure. This doc presents both neutrally so stakeholders can decide.

## What "localizing a playbook" involves

A playbook is more than prose. Each part is affected differently:

| Component | What it is | Localization impact |
|---|---|---|
| `README.md` | English instructions | Translate prose, keep tags exactly as-is |
| Tags (`@os`, `@device`, `@require`, `@test`, ...) | Drive rendering and CI | Do not translate or reorder |
| `@test` blocks | Scripts run by CI | Keep code identical |
| `playbook.json` | Metadata | Translate `title` and `description` only |
| `assets/` | Screenshots, often with English UI text | May need re-capture in a localized setup |
| Website (`website/`) | Renders to amd.com/playbooks | Must serve the `zh-CN` content |
| CI/CD | Tests run on self-hosted AMD machines (`halo`, `stx`, `krk`) | Localized playbooks still need real hardware to validate |

Takeaway: localizing means translating prose while preserving tags and test code, possibly re-capturing screenshots, then serving and validating the result on real hardware.

## Option 1: Fork the repository (China-owned)

The China team forks `amd/playbooks` into a repo they fully own.

How it works:

- The China team owns the fork end to end: content, branding, and release.
- Translation is manual, so wording and terminology can be hand-tuned for the market.
- The team can create their own China-only playbooks.
- The team runs their own CI/CD and their own machines.
- The team runs their own website deployment for the China audience.

The hard part (staying in sync):

- When AMD ships a bug fix to a playbook, the China team must notice it and re-apply the equivalent fix on their side.
- New upstream playbooks must be manually pulled in and translated.
- The more the fork diverges, the harder future merges get.

Pros:

- Highest translation quality (humans can fix awkward wording).
- Full autonomy: China-only playbooks, China-preferred models, local branding.
- In-region infrastructure for hosting, runners, and compliance.

Cons:

- Drift: upstream fixes are not automatic and must be tracked manually.
- Duplicated infrastructure (CI/CD, runners, website).
- Maintenance cost grows with every new playbook and upstream change.

## Option 2: Same repository (automated translation)

The China team works inside the one `amd/playbooks` repo. English stays the source of truth and localized content is fully auto-generated.

How it works:

- A pipeline auto-generates the `zh-CN` content from the English source.
- Because it is fully automated, localized files are overwritten on every run. The team cannot manually fix a translation, since any edit is deleted on the next run.
- The team influences output through config, not edits. The main lever is special tags that let them point specific steps to China-preferred models instead of the default models.
- China-only playbooks can be added, but they would be tested on AMD's existing machines, which are hard to update for China-specific needs.

Pros:

- Zero drift: upstream fixes flow to the localized version automatically.
- Low maintenance: no fork to keep in sync.
- Shared infrastructure and consistent branding.

Cons:

- No manual translation fixes; quality depends entirely on the pipeline.
- China-specific content depends on US machines that are hard to update.
- Less autonomy over content and model choices.

## Side-by-side

| Dimension | Option 1: Fork | Option 2: Same repo |
|---|---|---|
| Ownership | China team owns fork | Shared; English is source of truth |
| Translation | Manual (human) | Automated (no manual fixes) |
| Quality | Highest | Pipeline-dependent |
| Upstream sync | Manual, ongoing | Automatic, zero drift |
| China-only playbooks | Yes, unrestricted | Possible, tested on US machines |
| Model selection | Fully flexible | Via model-override tags |
| CI/CD and runners | China-owned | Shared US machines |
| Maintenance cost | High | Low |
| Autonomy | High | Low |

## Open questions

- Website hosting: there is no China deployment yet, so one must be stood up for either option (firewall, latency, ICP licensing).
- Translation pipeline (Option 2): does one exist, or must it be built? Which engine and quality bar?
- Screenshots: are English-UI screenshots acceptable, or must localized ones be re-captured?
- Hardware: does the China team have AMD machines to run as self-hosted runners (Option 1)?
- Governance: who reviews and approves localized content before publish?
