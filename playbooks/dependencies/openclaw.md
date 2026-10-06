<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installing OpenClaw

Install OpenClaw with the official installer:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

The `--no-prompt --no-onboard` flags skip the interactive setup wizard, which is required for unattended installs; the model backend is configured separately.

> **Tip:** If you see `command not found` after installation, add npm's global bin directory to your PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> To make this permanent, add the line above to your `~/.bashrc` or `~/.zshrc` file.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->
