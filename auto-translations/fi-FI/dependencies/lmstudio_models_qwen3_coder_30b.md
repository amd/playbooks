<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3-Coder 30B:n lataaminen LM Studiolla

Lataa Qwen3-Coder 30B -malli seuraavasti:

1. Paina näppäimistöltä "Ctrl" + "Shift" + "M" tai napsauta vasemman sivupalkin "Discover"-välilehteä (suurennuslasin kuvake)
2. Hae `Qwen3-Coder-30B-A3B`
3. Valitse kvantisointi (suositeltu `Q4_K_M` tarjoaa hyvän tasapainon koon ja laadun välillä) ja napsauta Download

LM Studio lataa mallin automaattisesti ja sijoittaa sen oikeaan hakemistoon.

Jos haluat ladata lisää malleja, voit hakea niitä Discover-välilehdeltä, ja LM Studio hoitaa loput.

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