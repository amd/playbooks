<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalacja OpenClaw

Zainstaluj OpenClaw za pomocą oficjalnego instalatora:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flagi `--no-prompt --no-onboard` pomijają interaktywnego kreatora konfiguracji, co jest wymagane w przypadku instalacji bez nadzoru; backend modelu jest konfigurowany oddzielnie.

> **Wskazówka:** Jeśli po instalacji pojawi się komunikat `command not found`, dodaj globalny katalog bin npm do zmiennej PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby ustawienie to było trwałe, dodaj powyższą linię do pliku `~/.bashrc` lub `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->