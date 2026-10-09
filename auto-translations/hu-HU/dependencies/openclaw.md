<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Az OpenClaw telepítése

Telepítse az OpenClaw-ot a hivatalos telepítővel:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A `--no-prompt --no-onboard` kapcsolók kihagyják az interaktív beállítási varázslót, ami a felügyelet nélküli telepítésekhez szükséges; a modell háttérrendszerét külön kell beállítani.

> **Tipp:** Ha a telepítés után a `command not found` üzenetet látja, adja hozzá az npm globális bin könyvtárát a PATH-hoz:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Ahhoz, hogy ez tartósan megmaradjon, adja hozzá a fenti sort a `~/.bashrc` vagy `~/.zshrc` fájljához.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->