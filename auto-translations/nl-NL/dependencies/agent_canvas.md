<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Agent Canvas installeren

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is de browser-UI/CLI voor OpenHands, gedistribueerd als het npm-pakket `@openhands/agent-canvas`. Het vereist **Node.js 24 of hoger**. Installeer het globaal:

```bash
npm install -g @openhands/agent-canvas
```

Het `agent-canvas`-binaire bestand komt terecht in de globale bin van npm (bijv. `~/.npm-global/bin`); zorg ervoor dat die map zich in je `PATH` bevindt.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->