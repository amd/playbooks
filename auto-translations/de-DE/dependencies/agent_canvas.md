<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation von Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) ist die Browser-UI/CLI für OpenHands, verteilt als npm-Paket `@openhands/agent-canvas`. Es erfordert **Node.js 24 oder höher**. Installieren Sie es global:

```bash
npm install -g @openhands/agent-canvas
```

Die Binärdatei `agent-canvas` landet im globalen Bin-Verzeichnis von npm (z. B. `~/.npm-global/bin`); stellen Sie sicher, dass sich dieses Verzeichnis in Ihrem `PATH` befindet.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->