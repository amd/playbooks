<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalarea OpenClaw

Instalați OpenClaw cu instalatorul oficial:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flagurile `--no-prompt --no-onboard` omit asistentul interactiv de configurare, acest lucru fiind necesar pentru instalările neasistate; backendul modelului se configurează separat.

> **Sfat:** Dacă vedeți `command not found` după instalare, adăugați directorul global bin al npm la PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Pentru a face această schimbare permanentă, adăugați linia de mai sus în fișierul `~/.bashrc` sau `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->