<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 SDXL-Turbo 다운로드

Lemonade server는 SDXL-Turbo 모델(`SDXL-Turbo`)을 제공합니다. 미리 다운로드하려면 다음과 같이 하세요:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo`를 실행하면 모델이 아직 존재하지 않을 경우 처음 사용 시 자동으로 다운로드한 뒤, 추론을 위해 로드합니다.

다운로드가 완료되면 모델이 Lemonade server의 다운로드된 모델 목록에 나타나며, 아래의 확인 절차를 통해 해당 머신에 모델이 존재하는지 확인할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->