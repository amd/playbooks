<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instaliranje Agent Canvas-a

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je UI/CLI za pregledač za OpenHands, distribuiran kao npm paket `@openhands/agent-canvas`. Zahteva **Node.js 24 ili noviji**. Instalirajte ga globalno:

```bash
npm install -g @openhands/agent-canvas
```

Binarni fajl `agent-canvas` se smešta u npm-ov globalni bin direktorijum (npr. `~/.npm-global/bin`); proverite da se taj direktorijum nalazi u vašoj `PATH` promenljivoj.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->