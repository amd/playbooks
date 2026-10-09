<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Встановлення Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — це браузерний UI/CLI для OpenHands, що розповсюджується як пакет npm `@openhands/agent-canvas`. Для нього потрібен **Node.js 24 або новіша версія**. Встановіть його глобально:

```bash
npm install -g @openhands/agent-canvas
```

Виконуваний файл `agent-canvas` розміщується у глобальній папці bin npm (наприклад, `~/.npm-global/bin`); переконайтеся, що цей каталог є у вашому `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->