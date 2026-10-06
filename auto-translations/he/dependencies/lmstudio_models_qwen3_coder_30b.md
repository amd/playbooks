<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3-Coder 30B ב-LM Studio

כדי להוריד את המודל Qwen3-Coder 30B:

1. לחצו "Ctrl" + "Shift" + "M" במקלדת או לחצו על הלשונית "Discover" (סמל זכוכית מגדלת) בסרגל הצד השמאלי
2. חפשו `Qwen3-Coder-30B-A3B`
3. בחרו קוונטיזציה (ה-`Q4_K_M` המומלץ מהווה איזון טוב בין גודל לאיכות) ולחצו על Download

LM Studio יוריד את המודל באופן אוטומטי וימקם אותו בתיקייה הנכונה.

במידה ותרצו להוריד מודלים נוספים, תוכלו לחפש אותם בלשונית Discover ו-LM Studio יטפל בשאר.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->