<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Agent Canvasin asentaminen

[Agent Canvas](https://github.com/OpenHands/agent-canvas) on OpenHandsin selainkäyttöliittymä/CLI, joka jaetaan npm-pakettina `@openhands/agent-canvas`. Se vaatii **Node.js 24:n tai uudemman**. Asenna se globaalisti:

```bash
npm install -g @openhands/agent-canvas
```

Binääritiedosto `agent-canvas` päätyy npm:n globaaliin bin-hakemistoon (esim. `~/.npm-global/bin`); varmista, että kyseinen hakemisto löytyy `PATH`-muuttujasta.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->