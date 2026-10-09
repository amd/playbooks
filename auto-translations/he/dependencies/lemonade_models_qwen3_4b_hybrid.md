<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3 4B Hybrid עבור Lemonade

שרת Lemonade מספק את המודל Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), שפועל על ה-NPU וה-GPU של מעבדי Ryzen AI. כדי להוריד אותו מראש:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

המודל מופיע ברשימת המודלים שהורדו בשרת Lemonade לאחר שההורדה (pull) הושלמה; הבדיקה שלהלן מאשרת שהוא קיים במכונה.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->