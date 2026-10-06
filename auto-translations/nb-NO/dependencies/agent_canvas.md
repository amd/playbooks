<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installere Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) er brukergrensesnittet/CLI-en i nettleseren for OpenHands, distribuert som npm-pakken `@openhands/agent-canvas`. Den krever **Node.js 24 eller nyere**. Installer den globalt:

```bash
npm install -g @openhands/agent-canvas
```

Binærfilen `agent-canvas` havner i npms globale bin-mappe (f.eks. `~/.npm-global/bin`); sørg for at den mappen er inkludert i `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->