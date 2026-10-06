<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת Hermes

יש להתקין את ממשק שורת הפקודה של סוכן Hermes באמצעות התקין הרשמי. הדגל `--skip-setup` שומר על ההתקנה ללא צורך באינטראקציה:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes מותקן בתוך `~/.local/bin`; יש לוודא שהתיקייה הזו נמצאת ב-`PATH` שלך.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->