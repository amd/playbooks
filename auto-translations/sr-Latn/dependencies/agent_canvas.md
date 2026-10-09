<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instaliranje Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je UI/CLI u pregledaču za OpenHands, distribuiran kao npm paket `@openhands/agent-canvas`. Zahteva **Node.js 24 ili noviji**. Instalirajte ga globalno:

```bash
npm install -g @openhands/agent-canvas
```

Izvršna datoteka `agent-canvas` se nalazi u npm-ovom globalnom bin direktorijumu (npr. `~/.npm-global/bin`); uverite se da je taj direktorijum uključen u vašu `PATH` promenljivu.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->