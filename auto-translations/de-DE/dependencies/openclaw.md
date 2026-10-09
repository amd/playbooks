<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation von OpenClaw

Installieren Sie OpenClaw mit dem offiziellen Installer:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Die Flags `--no-prompt --no-onboard` überspringen den interaktiven Einrichtungsassistenten, was für unbeaufsichtigte Installationen erforderlich ist; das Modell-Backend wird separat konfiguriert.

> **Tipp:** Wenn nach der Installation `command not found` angezeigt wird, fügen Sie das globale bin-Verzeichnis von npm zu Ihrem PATH hinzu:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Um dies dauerhaft zu machen, fügen Sie die obige Zeile zu Ihrer Datei `~/.bashrc` oder `~/.zshrc` hinzu.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->