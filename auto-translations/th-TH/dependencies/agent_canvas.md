<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) คือ UI/CLI บนเบราว์เซอร์สำหรับ OpenHands ซึ่งเผยแพร่เป็นแพ็กเกจ npm `@openhands/agent-canvas` โดยต้องใช้ **Node.js 24 ขึ้นไป** ติดตั้งแบบ global ด้วยคำสั่งนี้:

```bash
npm install -g @openhands/agent-canvas
```

ไบนารี `agent-canvas` จะถูกวางไว้ใน global bin ของ npm (เช่น `~/.npm-global/bin`) อย่าลืมตรวจสอบให้แน่ใจว่าไดเรกทอรีดังกล่าวอยู่ใน `PATH` ของคุณ

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->