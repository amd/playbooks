<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installera Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) är webbläsargränssnittet/CLI:n för OpenHands, distribuerad som npm-paketet `@openhands/agent-canvas`. Det kräver **Node.js 24 eller senare**. Installera det globalt:

```bash
npm install -g @openhands/agent-canvas
```

Binärfilen `agent-canvas` hamnar i npm:s globala bin (t.ex. `~/.npm-global/bin`); se till att den katalogen finns i din `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->