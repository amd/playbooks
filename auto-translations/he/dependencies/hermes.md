<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת Hermes

יש להתקין את ה-CLI של סוכן Hermes באמצעות ההתקנה הרשמית. הדגל `--skip-setup` שומר על ההתקנה ללא צורך באינטראקציה:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes מותקן לתוך `~/.local/bin`; יש לוודא שהתיקייה הזו נמצאת ב-`PATH` שלכם.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->