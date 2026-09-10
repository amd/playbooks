<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installing Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is the browser UI/CLI for OpenHands, distributed as the npm package `@openhands/agent-canvas`. It requires **Node.js 24 or later**. Install it globally:

```bash
npm install -g @openhands/agent-canvas
```

The `agent-canvas` binary lands in npm's global bin (e.g. `~/.npm-global/bin`); make sure that directory is on your `PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->
