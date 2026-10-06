<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation af OpenClaw

Installer OpenClaw med det officielle installationsprogram:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flagene `--no-prompt --no-onboard` springer den interaktive opsætningsguide over, hvilket er nødvendigt ved uovervågede installationer; modelbackenden konfigureres separat.

> **Tip:** Hvis du ser `command not found` efter installationen, skal du tilføje npm's globale bin-mappe til din PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> For at gøre dette permanent skal du tilføje linjen ovenfor til din `~/.bashrc`- eller `~/.zshrc`-fil.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->