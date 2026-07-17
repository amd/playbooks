<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3.5 9B ב-LM Studio

להורדת מודל Qwen3.5 9B:

1. לחץ על "Ctrl" + "Shift" + "M" במקלדת או לחץ על לשונית "Discover" (סמל זכוכית מגדלת) בסרגל הצד השמאלי
2. חפש את `Qwen3.5 9B`
3. בחר כמות (ה-`Q4_K_M` המומלץ הוא איזון טוב בין גודל לאיכות) ולחץ על Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio יוריד אוטומטית את המודל וימקם אותו בתיקייה הנכונה.

אם ברצונך להוריד מודלים נוספים, תוכל לחפש אותם בלשונית Discover ו-LM Studio יטפל בשאר.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->