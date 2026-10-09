<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installere OpenClaw

Installer OpenClaw med den offisielle installasjonsprogrammet:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaggene `--no-prompt --no-onboard` hopper over den interaktive oppsettveiviseren, noe som er nødvendig for ubetjente installasjoner; modellbakenden konfigureres separat.

> **Tips:** Hvis du ser `command not found` etter installasjonen, legg til npms globale bin-mappe i PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> For å gjøre dette permanent, legg til linjen over i `~/.bashrc`- eller `~/.zshrc`-filen din.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->