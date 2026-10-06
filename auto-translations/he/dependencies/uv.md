<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת uv

[uv](https://docs.astral.sh/uv/) הוא מנהל החבילות/הסביבות של Python שבו משתמש Agent Canvas כדי לבנות את סביבת שרת הסוכן שלו. התקינו אותו באמצעות הסקריפט הרשמי:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` מותקן לתוך `~/.local/bin`; ודאו שהתיקייה הזו נמצאת ב-`PATH` שלכם.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->