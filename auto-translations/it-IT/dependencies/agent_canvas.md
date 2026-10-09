<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installazione di Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) è l'interfaccia utente/CLI del browser per OpenHands, distribuita come pacchetto npm `@openhands/agent-canvas`. Richiede **Node.js 24 o versione successiva**. Installalo globalmente:

```bash
npm install -g @openhands/agent-canvas
```

Il binario `agent-canvas` viene posizionato nel bin globale di npm (ad es. `~/.npm-global/bin`); assicurati che quella directory sia nel tuo `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->