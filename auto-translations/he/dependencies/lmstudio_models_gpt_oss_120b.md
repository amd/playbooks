<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת GPT-OSS 120B ב-LM Studio

כדי להוריד את המודל GPT-OSS 120B:

1. לחצו על "Ctrl" + "Shift" + "M" במקלדת שלכם או לחצו על לשונית "Discover" (סמל זכוכית מגדלת) בסרגל הצד השמאלי
2. חפשו את `ggml-org/gpt-oss-120b-GGUF`
3. בחרו `mxfp4` ולחצו על Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio יוריד באופן אוטומטי את המודל וימקם אותו בתיקייה הנכונה.

אם ברצונכם להוריד מודלים נוספים, תוכלו לחפש אותם בלשונית Discover ו-LM Studio יטפל בשאר.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->