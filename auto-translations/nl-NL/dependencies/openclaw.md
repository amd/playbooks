<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### OpenClaw installeren

Installeer OpenClaw met het officiële installatieprogramma:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

De `--no-prompt --no-onboard` vlaggen slaan de interactieve installatiewizard over, wat vereist is voor onbeheerde installaties; de model-backend wordt apart geconfigureerd.

> **Tip:** Als je na de installatie `command not found` ziet, voeg dan de globale bin-directory van npm toe aan je PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Om dit permanent te maken, voeg je de bovenstaande regel toe aan je `~/.bashrc`- of `~/.zshrc`-bestand.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->