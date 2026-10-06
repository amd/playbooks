<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) คือ browser UI/CLI สำหรับ OpenHands ซึ่งเผยแพร่ในรูปแบบแพ็กเกจ npm ชื่อ `@openhands/agent-canvas` โดยต้องใช้ **Node.js 24 ขึ้นไป** ติดตั้งแบบ global ด้วยคำสั่งต่อไปนี้:

```bash
npm install -g @openhands/agent-canvas
```

ไบนารี `agent-canvas` จะถูกติดตั้งไว้ใน global bin ของ npm (เช่น `~/.npm-global/bin`) โปรดตรวจสอบให้แน่ใจว่าไดเรกทอรีดังกล่าวอยู่ใน `PATH` ของคุณ

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->