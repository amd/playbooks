<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Downloading Qwen3 4B Hybrid for Lemonade

The Lemonade server serves the Qwen3 4B Hybrid model (`Qwen3-4B-Hybrid`), which runs on the NPU and GPU of Ryzen AI processors. To download it ahead of time:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

The model appears in the Lemonade server's downloaded-model list once the pull completes; the check below confirms it is present on the machine.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->
