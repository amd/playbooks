<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安裝 Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是 OpenHands 的瀏覽器 UI/CLI，以 npm 套件 `@openhands/agent-canvas` 的形式發布。它需要 **Node.js 24 或更新版本**。請全域安裝：

```bash
npm install -g @openhands/agent-canvas
```

`agent-canvas` 執行檔會安裝在 npm 的全域 bin 目錄中（例如 `~/.npm-global/bin`）；請確認該目錄已加入你的 `PATH`。

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->