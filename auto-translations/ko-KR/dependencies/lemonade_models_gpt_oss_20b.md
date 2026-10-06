<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade용 GPT-OSS 20B 다운로드

Lemonade 서버는 GPT-OSS 20B MXFP4 GGUF 모델(`gpt-oss-20b-mxfp4-GGUF`)을 제공합니다. 미리 다운로드하려면 다음을 수행하세요:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF`는 모델이 아직 없는 경우 처음 사용할 때 자동으로 다운로드한 후 추론을 위해 로드합니다.

다운로드가 완료되면 Lemonade 서버의 다운로드된 모델 목록에 해당 모델이 나타나며, 아래의 확인 절차를 통해 머신에 모델이 존재하는지 확인할 수 있습니다.

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