<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת Qwen3.5 9B ב-LM Studio

כדי להוריד את מודל Qwen3.5 9B:

1. לחצו על "Ctrl" + "Shift" + "M" במקלדת או לחצו על הלשונית "Discover" (סמל זכוכית מגדלת) בסרגל הצד השמאלי
2. חפשו את `Qwen3.5 9B`
3. בחרו קוונטיזציה (מומלץ `Q4_K_M` המהווה איזון טוב בין גודל לאיכות) ולחצו על Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio יוריד את המודל באופן אוטומטי וימקם אותו בתיקייה הנכונה.

אם ברצונכם להוריד מודלים נוספים, תוכלו לחפש אותם בלשונית Discover ו-LM Studio יטפל בשאר.

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