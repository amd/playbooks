<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) הוא ממשק טרמינל קליל שמטפל ביצירת מכולות toolbox, בהורדת משקלי מודלים, ובהפעלת שרתים. יש להתקין אותו באמצעות `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` מתקין את נקודת הכניסה לתוך `~/.local/bin`; יש לוודא שהתיקייה הזו נמצאת ב-`PATH` שלכם.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->