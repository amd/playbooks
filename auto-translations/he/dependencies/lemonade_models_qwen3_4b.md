<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3.5 4B עבור Lemonade

שרת Lemonade מספק את המודל Qwen3.5 4B (`Qwen3.5-4B-GGUF`). כדי להוריד אותו מראש:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` גם מוריד את המודל בשימוש הראשון אם הוא עדיין לא קיים, ולאחר מכן טוען אותו להסקה.

המודל מופיע ברשימת המודלים שהורדו בשרת Lemonade לאחר השלמת ההורדה; הבדיקות שלהלן מאמתות שהוא קיים במכונה.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->