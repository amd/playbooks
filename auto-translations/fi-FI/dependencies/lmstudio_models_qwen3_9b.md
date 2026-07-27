<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3.5 9B:n lataaminen LM Studioon

Qwen3.5 9B -mallin lataaminen:

1. Paina näppäimistöltä "Ctrl" + "Shift" + "M" tai napsauta vasemman sivupalkin "Discover"-välilehteä (suurennuslasin kuvake)
2. Hae `Qwen3.5 9B`
3. Valitse kvantisointi (suositeltu `Q4_K_M` tarjoaa hyvän tasapainon koon ja laadun välillä) ja napsauta Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio lataa mallin automaattisesti ja sijoittaa sen oikeaan hakemistoon.

Jos haluat ladata lisää malleja, voit hakea niitä Discover-välilehdeltä, ja LM Studio hoitaa loput.

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