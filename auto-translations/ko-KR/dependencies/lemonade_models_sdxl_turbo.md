<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 SDXL-Turbo 다운로드

Lemonade 서버는 SDXL-Turbo 모델(`SDXL-Turbo`)을 제공합니다. 미리 다운로드하려면 다음과 같이 합니다:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` 명령도 모델이 아직 없는 경우 처음 사용할 때 모델을 다운로드한 다음 추론을 위해 로드합니다.

풀(pull)이 완료되면 해당 모델이 Lemonade 서버의 다운로드된 모델 목록에 나타나며, 아래의 확인 절차를 통해 머신에 모델이 존재하는지 확인할 수 있습니다.

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