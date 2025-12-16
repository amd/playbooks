# Halo Playbooks

<p align="center">
  <img src="src/app/assets/halo.png" alt="Halo Logo" width="240"/>
</p>

This repository hosts all playbooks that will be part of the upcoming AMD Developer Platform launch.

## Overview

We will maintain a curated set of 15 playbooks, organized into two tiers:

- **Core Playbooks (5)**: Mission-critical experiences that represent the highest-value workflows.
- **Supplemental Playbooks (10)**: Additional experiences that broaden capability but are not required for out-of-box (OOB) readiness.

These playbooks serve as the authoritative source for determining all required software assets (frameworks, foundational software, models, and apps).

Only assets required to deliver the Core Playbooks will be preinstalled on the device. The preinstalled software set will be the minimal union of all dependencies across the five core playbooks.

## Playbook Proposal and Definition

To define the 15 playbooks, we need contributors to create issues for each playbook. Each issue should follow a specific format to ensure consistency and proper categorization.

### How to Create a Playbook Proposal

Create an issue at [github.com/amd/halo_playbooks](https://github.com/amd/halo_playbooks) with the following format.

1. **Title Format**: Use the format `[Playbook] <Descriptive Title>`
   - Example: `[Playbook] Local LLM coding with GitHub Copilot and Qwen3-Next-80B`

2. **Required Labels**: Add relevant labels to categorize the playbook:
   - `framework::<name>` - Framework used (e.g., `framework::llamacpp`, `framework::docker`, `framework::vllm`)
   - `model::<name>` - Model used (e.g., `model::qwen3-next-80b`, `model::gpt-oss-120b`)
   - `app::<name>` - Application used (e.g., `app::vscode`, `app::openwebui`, `app::openhands`)
   - `os::<name>` - Operating system(s) supported (e.g., `os::linux`, `os::windows`)
   - `track::<type>` - **REQUIRED**: Either `track::core` or `track::supplemental`

3. **Milestone**: Assign the issue to the **`playbooks`** milestone

### Example Issues

Here are examples of properly formatted playbook issues:

#### Playbook Example
```
[Playbook] Local LLM coding with GitHub Copilot and Qwen3-Next-80B

Labels:
- app::vscode
- framework::llamacpp
- model::qwen3-next-80b
- os::linux
- os::windows
- track::core

Milestone: playbooks
```

### Next Steps

Once all 15 playbooks have been defined through issues, contributors will be invited to create playbooks based on an initial template.
