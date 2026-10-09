<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת SDXL-Turbo עבור Lemonade

שרת ה-Lemonade מגיש את המודל SDXL-Turbo (`SDXL-Turbo`). כדי להוריד אותו מראש:

```bash
lemonade pull SDXL-Turbo
```

‏`lemonade run SDXL-Turbo` גם מוריד את המודל בשימוש הראשון אם הוא עדיין לא קיים, ולאחר מכן טוען אותו לצורך הסקה (inference).

המודל מופיע ברשימת המודלים שהורדו בשרת ה-Lemonade לאחר שההורדה (pull) מסתיימת; הבדיקות שלהלן מאשרות שהוא קיים במכונה.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->