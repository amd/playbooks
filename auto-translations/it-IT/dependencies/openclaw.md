<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installazione di OpenClaw

Installa OpenClaw con l'installer ufficiale:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

I flag `--no-prompt --no-onboard` saltano la procedura guidata di configurazione interattiva, necessaria per le installazioni non presidiate; il backend del modello viene configurato separatamente.

> **Suggerimento:** Se dopo l'installazione viene visualizzato `command not found`, aggiungi la directory bin globale di npm al PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Per rendere questa modifica permanente, aggiungi la riga precedente al tuo file `~/.bashrc` o `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->