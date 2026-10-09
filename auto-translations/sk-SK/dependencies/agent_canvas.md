<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Inštalácia Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je prehliadačové UI/CLI pre OpenHands, distribuované ako npm balík `@openhands/agent-canvas`. Vyžaduje **Node.js 24 alebo novší**. Nainštalujte ho globálne:

```bash
npm install -g @openhands/agent-canvas
```

Binárny súbor `agent-canvas` sa umiestni do globálneho bin adresára npm (napr. `~/.npm-global/bin`); uistite sa, že tento adresár je zahrnutý vo vašej `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->