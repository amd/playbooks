<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Gemma-4 E2B עבור Lemonade

שרת Lemonade מגיש את מודל Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). כדי להוריד אותו מראש:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

הפקודה `lemonade run Gemma-4-E2B-it-GGUF` גם מורידה את המודל בשימוש הראשון אם הוא עדיין לא קיים, ולאחר מכן טוענת אותו להסקה (inference).

המודל מופיע ברשימת המודלים שהורדו בשרת Lemonade לאחר השלמת ההורדה; הבדיקות שלהלן מאשרות שהוא נמצא במחשב.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->