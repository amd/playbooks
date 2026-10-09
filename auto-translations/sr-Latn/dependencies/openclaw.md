<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instaliranje OpenClaw-a

Instalirajte OpenClaw pomoću zvaničnog instalera:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Oznake `--no-prompt --no-onboard` preskaču interaktivni čarobnjak za podešavanje, što je neophodno za nenadgledane instalacije; pozadinski model se konfiguriše posebno.

> **Savet:** Ako nakon instalacije vidite poruku `command not found`, dodajte npm-ov globalni bin direktorijum u vašu PATH promenljivu:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Da biste ovo učinili trajnim, dodajte gornju liniju u vašu `~/.bashrc` ili `~/.zshrc` datoteku.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->