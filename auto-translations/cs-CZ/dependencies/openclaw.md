<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalace OpenClaw

Nainstalujte OpenClaw pomocí oficiálního instalátoru:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Příznaky `--no-prompt --no-onboard` přeskočí interaktivního průvodce nastavením, což je nutné pro neobslužné instalace; backend modelu se konfiguruje samostatně.

> **Tip:** Pokud se po instalaci zobrazí `command not found`, přidejte globální bin adresář npm do PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Aby bylo toto nastavení trvalé, přidejte výše uvedený řádek do souboru `~/.bashrc` nebo `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->