<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 GPT-OSS 20B 다운로드

Lemonade 서버는 GPT-OSS 20B MXFP4 GGUF 모델(`gpt-oss-20b-mxfp4-GGUF`)을 제공합니다. 미리 다운로드하려면:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF`는 모델이 아직 존재하지 않는 경우 처음 사용할 때 모델을 다운로드한 다음 추론을 위해 로드합니다.

모델은 가져오기(pull)가 완료되면 Lemonade 서버의 다운로드된 모델 목록에 나타나며, 아래의 확인 절차는 해당 모델이 머신에 존재하는지를 확인합니다.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->