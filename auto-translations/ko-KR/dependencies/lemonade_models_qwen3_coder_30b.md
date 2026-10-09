<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 Qwen3-Coder 30B A3B 다운로드

Lemonade 서버는 Qwen3-Coder 30B A3B 모델(`Qwen3-Coder-30B-A3B-Instruct-GGUF`)을 제공합니다. 미리 다운로드하려면:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF`를 실행하면 모델이 아직 없는 경우 처음 사용할 때 다운로드한 다음 추론을 위해 로드합니다.

다운로드가 완료되면 Lemonade 서버의 다운로드된 모델 목록에 모델이 표시되며, 아래 확인 과정을 통해 해당 모델이 머신에 존재하는지 확인할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->