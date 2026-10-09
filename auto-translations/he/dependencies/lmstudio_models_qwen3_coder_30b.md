<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3-Coder 30B ב-LM Studio

כדי להוריד את המודל Qwen3-Coder 30B:

1. לחצו על "Ctrl" + "Shift" + "M" במקלדת או לחצו על לשונית "Discover" (סמל זכוכית מגדלת) בסרגל הצד השמאלי
2. חפשו את `Qwen3-Coder-30B-A3B`
3. בחרו קוונטיזציה (מומלץ `Q4_K_M`, המספק איזון טוב בין גודל לאיכות) ולחצו על Download

LM Studio יוריד את המודל וימקם אותו באופן אוטומטי בתיקייה הנכונה.

אם ברצונכם להוריד מודלים נוספים, תוכלו לחפש אותם בלשונית Discover ו-LM Studio יטפל בשאר.

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