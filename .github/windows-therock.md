# Windows TheRock provisioning for Radeon ML playbooks

The AMD graphics driver is installed first and the machine reboots. For batches
containing one of the four single-GPU ML playbooks on RX7900, RX9070 or R9700,
configure one Windows TheRock source to append
`InstallationScripts/gfx/windows-therock-tarball.ps1` before actor deployment.
This step does not require another reboot and does not install Torch.

## Configure a source

Use repository variables, not committed internal URLs. Choose exactly one mode.

| Mode | Variables |
| --- | --- |
| Windows distribution tarball | `ORCHESTRAI_WINDOWS_THEROCK_URL`: HTTPS URL to a Windows TheRock distribution |
| Windows CI artifacts | `ORCHESTRAI_WINDOWS_THEROCK_RUN_ID`: pinned CI run ID; `ORCHESTRAI_WINDOWS_THEROCK_RUN_REPO`: owner/repository |

Artifact mode also accepts `ORCHESTRAI_WINDOWS_THEROCK_REF` to select the
TheRock artifact-installer branch. The controller derives the artifact family
from `device_to_gfx`: RX7900 uses `gfx110X-all`; RX9070 and R9700 use
`gfx120X-all`. The configured run must actually publish Windows artifacts for
that family. Use a build compatible with the test's Torch wheels.

Never reuse `ORCHESTRAI_THEROCK_URL`: it remains the Linux distribution.
Clear artifact-only variables when switching to tarball mode. An unset Windows
source leaves existing provisioning unchanged; an invalid configured source
fails validation before hardware acquisition.

For authenticated artifact access, arrange a securely bound read-only
`GITHUB_TOKEN` in the pipeline's provisioning environment. Do not put a token
in a repository variable, URL or `BUILDS_JSON`. The controller deliberately
never forwards the Actions token. Without authentication the existing installer
can encounter GitHub API rate limits on the farm's shared egress address.

## Verify on one Radeon before rollout

1. Select a Windows Radeon batch containing Llama Factory, PyTorch finetuning,
   PyTorch ROCm LLMs or Unsloth. Point the test-library ref at PR #4492's branch,
   `saman/playbook-gpu-isolation` (or its reviewed commit).
2. Check the dry-run provisioning payload: driver script with
   `reboot_after: true`, followed by Windows TheRock with
   `reboot_after: false`. Confirm no Linux distribution URL was passed.
3. TheRock provisioning must verify `hipInfo.exe`, publish the installation's
   `ROCM_HOME`/`ROCM_PATH`/`HIP_PATH`/`ROCM_BIN` and machine PATH, and finish
   before the actor starts. Leave `THEROCK_SET_RUNTIME_ENV` unset: additional
   OpenCL/compiler runtime overrides are not needed for GPU discovery.
4. In the playbook log, require the physical inventory, one selected expected
   Radeon family, and successful filtered re-enumeration. Check the playbook's
   own Torch output shows one visible GPU, one training rank and no iGPU/model
   sharding. Then rerun all four workloads on the same hardware.

These changes do not reserve GPU memory, alter model names/context lengths,
change playbook READMEs, or guarantee that a model fits the selected adapter.
