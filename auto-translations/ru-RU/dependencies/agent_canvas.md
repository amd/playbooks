<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — это браузерный интерфейс/CLI для OpenHands, распространяемый в виде npm-пакета `@openhands/agent-canvas`. Для его работы требуется **Node.js 24 или новее**. Установите его глобально:

```bash
npm install -g @openhands/agent-canvas
```

Бинарный файл `agent-canvas` появится в глобальной папке bin npm (например, `~/.npm-global/bin`); убедитесь, что этот каталог указан в переменной `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->