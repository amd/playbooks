<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Az Agent Canvas telepítése

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az OpenHands böngészős UI/CLI-je, amely `@openhands/agent-canvas` néven npm csomagként kerül terjesztésre. Ehhez **Node.js 24 vagy újabb verzió** szükséges. Telepítsd globálisan:

```bash
npm install -g @openhands/agent-canvas
```

Az `agent-canvas` futtatható fájl az npm globális bin könyvtárába kerül (pl. `~/.npm-global/bin`); győződj meg róla, hogy ez a könyvtár szerepel a `PATH` változódban.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->