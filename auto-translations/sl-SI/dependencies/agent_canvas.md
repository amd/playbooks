<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Namestitev Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) je uporabniški vmesnik v brskalniku/CLI za OpenHands, ki je distribuiran kot npm paket `@openhands/agent-canvas`. Zahteva **Node.js 24 ali novejši**. Namestite ga globalno:

```bash
npm install -g @openhands/agent-canvas
```

Binarna datoteka `agent-canvas` se znajde v npm-jevem globalnem bin direktoriju (npr. `~/.npm-global/bin`); poskrbite, da je ta direktorij vključen v vašo `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->