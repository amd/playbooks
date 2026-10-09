<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת GPT-OSS 20B עבור Lemonade

שרת ה-Lemonade מגיש את המודל GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). כדי להוריד אותו מראש:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` גם מוריד את המודל בשימוש הראשון אם הוא עדיין לא קיים, ולאחר מכן טוען אותו להסקה.

המודל מופיע ברשימת המודלים שהורדו בשרת ה-Lemonade לאחר השלמת ההורדה; הבדיקות שלהלן מאשרות שהוא נמצא במכונה.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->