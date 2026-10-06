<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 Qwen3.5 4B 다운로드

Lemonade 서버는 Qwen3.5 4B 모델(`Qwen3.5-4B-GGUF`)을 제공합니다. 이를 미리 다운로드하려면:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF`는 모델이 아직 없는 경우 처음 사용할 때 모델을 다운로드한 다음 추론을 위해 로드합니다.

가져오기(pull)가 완료되면 모델이 Lemonade 서버의 다운로드된 모델 목록에 나타나며, 아래 확인 절차를 통해 해당 머신에 존재하는지 확인할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->