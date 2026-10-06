<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalace Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je uživatelské rozhraní prohlížeče / CLI pro OpenHands, distribuované jako npm balíček `@openhands/agent-canvas`. Vyžaduje **Node.js 24 nebo novější**. Nainstalujte jej globálně:

```bash
npm install -g @openhands/agent-canvas
```

Binární soubor `agent-canvas` se umístí do globálního bin adresáře npm (např. `~/.npm-global/bin`); ujistěte se, že je tento adresář zahrnut v proměnné `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->