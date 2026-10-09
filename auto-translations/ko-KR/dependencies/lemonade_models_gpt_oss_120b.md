<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 GPT-OSS 120B 다운로드

Lemonade 서버는 GPT-OSS 120B MXFP4 GGUF 모델(`gpt-oss-120b-mxfp-GGUF`)을 제공합니다. 미리 다운로드하려면:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF`도 모델이 아직 없는 경우 처음 사용할 때 모델을 다운로드한 다음 추론을 위해 로드합니다.

가져오기(pull)가 완료되면 모델이 Lemonade 서버의 다운로드된 모델 목록에 나타납니다. 아래의 확인 절차는 모델이 해당 머신에 존재하는지 확인합니다.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->