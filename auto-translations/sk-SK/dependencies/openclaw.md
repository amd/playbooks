<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Inštalácia OpenClaw

Nainštalujte OpenClaw pomocou oficiálneho inštalátora:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Príznaky `--no-prompt --no-onboard` preskočia interaktívneho sprievodcu nastavením, čo je potrebné pri neinteraktívnych inštaláciách; backend modelu sa konfiguruje samostatne.

> **Tip:** Ak sa po inštalácii zobrazí `command not found`, pridajte globálny bin adresár npm do PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby bola táto zmena trvalá, pridajte uvedený riadok do súboru `~/.bashrc` alebo `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->