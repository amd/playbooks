<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת Agent Canvas

[Agent Canvas](https://github.com/OpenHands/agent-canvas) הוא ה-UI/CLI מבוסס הדפדפן עבור OpenHands, המופץ כחבילת ה-npm‏ `@openhands/agent-canvas`. נדרש **Node.js 24 ומעלה**. התקינו אותו באופן גלובלי:

```bash
npm install -g @openhands/agent-canvas
```

הקובץ הבינארי `agent-canvas` ממוקם ב-bin הגלובלי של npm (לדוגמה: `~/.npm-global/bin`); ודאו שהתיקייה הזו נמצאת ב-`PATH` שלכם.

<!-- @os:linux -->
<!-- @test:id=agent-canvas-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
agent-canvas --version
```
<!-- @test:end -->
<!-- @os:end -->