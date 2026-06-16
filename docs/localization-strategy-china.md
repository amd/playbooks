# Localization Strategy: China

Two options for localizing `amd/playbooks` into Simplified Chinese (`zh-CN`) for the China market.
## What "localizing a playbook" involves

A playbook is more than prose. Each part is affected differently:

| Component | What it is | Localization impact |
|---|---|---|
| `README.md` | English instructions | Translate prose, keep tags exactly as-is |
| Tags (`@os`, `@device`, `@require`, `@test`, ...) | Drive rendering and CI | Do not translate or reorder |
| `@test` blocks | Scripts run by CI | Keep code identical |
| `playbook.json` | Metadata | Translate `title` and `description` only |
| `assets/` | Screenshots, often with English UI text | May need re-capture in a localized setup |
| CI/CD | Tests run on self-hosted AMD machines (`halo`, `stx`, `krk`) | Localized playbooks still need real hardware to validate |

Takeaway: localizing means translating prose while preserving tags and test code, possibly re-capturing screenshots, then serving and validating the result on real hardware.

## Option 1: Fork the repository (China-owned)

The China team forks `amd/playbooks` into a repo they fully own.

How it works:

- The China team owns the fork end to end: content, testing, and release.
- Translation is manual, so wording and terminology can be hand-tuned for the market.
- The team can create their own China-only playbooks.
- The team runs their own CI/CD and their own machines.
- The team runs their own website deployment for the China audience.

The hard part (staying in sync):

- When AMD ships a bug fix to a playbook, the China team must notice it and re-apply the equivalent fix on their side.

Pros:

- Highest translation quality.
- Full autonomy: China-only playbooks, China-preferred models, local branding.
- In-region infrastructure for hosting, runners, and compliance.

Cons:

- Drift: upstream fixes are not automatic and must be tracked manually.
- Duplicated infrastructure (CI/CD, runners, website).


## Option 2: Same repository (automated translation)

The China team works inside the one `amd/playbooks` repo. English stays the source of truth and localized content is fully auto-generated.

Three kinds of playbooks exist in this model:

| Type | Authored by | Language | Tested on |
|---|---|---|---|
| Global | AMD US Team | English | AMD machines |
| Auto-translated | AMD China Team (generated) | `zh-CN` | AMD China Machines |
| China-native | China China Team | `zh-CN` | AMD China Machines |

How it works:

- A pipeline auto-generates the `zh-CN` (auto-translated) content from the global English source.
- Because it is fully automated, auto-translated files are overwritten on every run. The team cannot manually fix a translation, since any edit is deleted on the next run.
- The team influences output through config, not edits.
- The China team can add China-native playbooks, but they must maintain their own machines to test them. AMD US machines cover only the global and auto-translated playbooks. 

Pros:

- Zero drift: upstream fixes flow to the localized version automatically.
- Low maintenance: no fork to keep in sync.

Cons:

- No manual translation fixes; quality depends entirely on the pipeline.
- Less autonomy over content and model choices.

## Side-by-side

| Dimension | Option 1: Fork | Option 2: Same repo |
|---|---|---|
| Ownership | China team owns fork | Shared; English is source of truth |
| Translation | Manual (human) | Automated (no manual fixes) |
| Upstream sync | Manual, ongoing | Automatic, zero drift |
| China-native playbooks | Yes, unrestricted | Yes, China team maintains their own test machines |
| Model selection | Fully flexible | Via model-override tags |
| CI/CD and runners | China-owned | AMD machines for global + auto-translated; China machines for China-native |
| Maintenance cost | High | Low |
| Autonomy | High | Low |
