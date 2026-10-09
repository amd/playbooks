<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת OpenClaw

התקינו את OpenClaw באמצעות מתקין ההתקנה הרשמי:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

הדגלים `--no-prompt --no-onboard` מדלגים על אשף ההתקנה האינטראקטיבי, מה שנדרש עבור התקנות ללא השגחה; ה-backend של המודל מוגדר בנפרד.

> **טיפ:** אם מופיעה ההודעה `command not found` לאחר ההתקנה, הוסיפו את תיקיית ה-bin הגלובלית של npm ל-PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> כדי להפוך זאת לקבוע, הוסיפו את השורה שלמעלה לקובץ `~/.bashrc` או `~/.zshrc` שלכם.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->