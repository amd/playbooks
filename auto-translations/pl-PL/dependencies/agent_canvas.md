<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalowanie Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) to interfejs przeglądarkowy/CLI dla OpenHands, dystrybuowany jako pakiet npm `@openhands/agent-canvas`. Wymaga **Node.js w wersji 24 lub nowszej**. Zainstaluj go globalnie:

```bash
npm install -g @openhands/agent-canvas
```

Plik binarny `agent-canvas` trafia do globalnego katalogu bin npm (np. `~/.npm-global/bin`); upewnij się, że ten katalog znajduje się w zmiennej `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->