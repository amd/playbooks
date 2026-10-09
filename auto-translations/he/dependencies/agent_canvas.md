<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא ממשק המשתמש/CLI בדפדפן עבור OpenHands, המופץ כחבילת ה-npm‏ `@openhands/agent-canvas`. הוא דורש **Node.js 24 ואילך**. יש להתקין אותו באופן גלובלי:

```bash
npm install -g @openhands/agent-canvas
```

הקובץ הבינארי `agent-canvas` ממוקם בתיקיית ה-bin הגלובלית של npm (לדוגמה `~/.npm-global/bin`); יש לוודא שהתיקייה הזו נמצאת בתוך ה-`PATH`.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->