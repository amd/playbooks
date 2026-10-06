<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安装 Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是 OpenHands 的浏览器 UI/CLI，以 npm 包 `@openhands/agent-canvas` 的形式分发。它需要 **Node.js 24 或更高版本**。全局安装方法如下：

```bash
npm install -g @openhands/agent-canvas
```

`agent-canvas` 可执行文件会被放置在 npm 的全局 bin 目录中（例如 `~/.npm-global/bin`）；请确保该目录已添加到你的 `PATH` 中。

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->