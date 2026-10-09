<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Agent Canvas 설치

[Agent Canvas](https://github.com/OpenHands/agent-canvas)는 OpenHands용 브라우저 UI/CLI로, npm 패키지 `@openhands/agent-canvas`로 배포됩니다. **Node.js 24 이상**이 필요합니다. 전역으로 설치하세요:

```bash
npm install -g @openhands/agent-canvas
```

`agent-canvas` 바이너리는 npm의 전역 bin 디렉터리(예: `~/.npm-global/bin`)에 설치되므로, 해당 디렉터리가 `PATH`에 포함되어 있는지 확인하세요.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->