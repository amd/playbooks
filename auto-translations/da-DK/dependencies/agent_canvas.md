<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation af Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er browser-UI'et/CLI'et til OpenHands, som distribueres som npm-pakken `@openhands/agent-canvas`. Det kræver **Node.js 24 eller nyere**. Installer det globalt:

```bash
npm install -g @openhands/agent-canvas
```

Binærfilen `agent-canvas` havner i npm's globale bin (f.eks. `~/.npm-global/bin`); sørg for, at denne mappe er en del af din `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->