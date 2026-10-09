<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 Qwen3 4B Hybrid 다운로드

Lemonade 서버는 Ryzen AI 프로세서의 NPU와 GPU에서 실행되는 Qwen3 4B Hybrid 모델(`Qwen3-4B-Hybrid`)을 제공합니다. 미리 다운로드하려면:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

다운로드가 완료되면 Lemonade 서버의 다운로드된 모델 목록에 해당 모델이 나타나며, 아래 확인 절차를 통해 머신에 해당 모델이 있는지 확인할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->