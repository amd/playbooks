<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3-Coder 30B A3B עבור Lemonade

שרת Lemonade מגיש את המודל Qwen3-Coder 30B A3B (‏`Qwen3-Coder-30B-A3B-Instruct-GGUF`). כדי להוריד אותו מראש:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

‏`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` גם מוריד את המודל בשימוש הראשון אם הוא עדיין לא קיים, ולאחר מכן טוען אותו לצורך הסקה (inference).

המודל מופיע ברשימת המודלים שהורדו בשרת Lemonade לאחר השלמת ה-pull; הבדיקות שלהלן מאשרות שהוא קיים במחשב.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->