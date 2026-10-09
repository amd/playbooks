<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Az Agent Canvas telepítése

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az OpenHands böngészős UI/CLI-je, amelyet `@openhands/agent-canvas` néven npm csomagként terjesztenek. Ehhez **Node.js 24 vagy újabb verzió** szükséges. Telepítse globálisan:

```bash
npm install -g @openhands/agent-canvas
```

Az `agent-canvas` bináris az npm globális bin könyvtárába kerül (pl. `~/.npm-global/bin`); győződjön meg róla, hogy ez a könyvtár szerepel a `PATH` változóban.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->