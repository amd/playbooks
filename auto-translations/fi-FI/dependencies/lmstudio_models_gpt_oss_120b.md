<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 120B:n lataaminen LM Studiossa

GPT-OSS 120B -mallin lataamiseksi:

1. Paina näppäimistöltä "Ctrl" + "Shift" + "M" tai napsauta vasemman sivupalkin "Discover"-välilehteä (suurennuslasi-kuvake)
2. Etsi `ggml-org/gpt-oss-120b-GGUF`
3. Valitse `mxfp4` ja napsauta Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio lataa mallin automaattisesti ja sijoittaa sen oikeaan hakemistoon.

Jos haluat ladata lisää malleja, voit etsiä niitä Discover-välilehdeltä ja LM Studio hoitaa loput.

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