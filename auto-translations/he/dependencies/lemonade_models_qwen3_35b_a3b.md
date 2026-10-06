<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3.6 35B A3B עבור Lemonade

שרת Lemonade מגיש את מודל Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). כדי להוריד אותו מראש:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

הפקודה `lemonade run Qwen3.6-35B-A3B-GGUF` גם מורידה את המודל בשימוש הראשון אם הוא לא כבר קיים, ולאחר מכן טוענת אותו להסקה.

המודל מופיע ברשימת המודלים שהורדו בשרת Lemonade לאחר שההורדה הושלמה; הבדיקות שבהמשך מאשרות שהוא קיים במכונה.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->