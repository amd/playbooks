<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת GPT-OSS 120B עבור Lemonade

שרת Lemonade מגיש את מודל GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). כדי להוריד אותו מראש:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` גם מוריד את המודל בשימוש הראשון אם הוא עדיין לא קיים, ולאחר מכן טוען אותו להסקה (inference).

המודל מופיע ברשימת המודלים שהורדו של שרת Lemonade לאחר שהמשיכה (pull) מסתיימת; הבדיקות שלהלן מאשרות שהוא נמצא במכונה.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->