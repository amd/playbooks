<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama용 GPT-OSS 20B 다운로드

GPT-OSS 20B 모델을 Ollama로 가져옵니다:

```bash
ollama pull gpt-oss:20b
```

가져오기가 성공하려면 Ollama 서버가 실행 중이어야 합니다. 아직 실행 중이 아니라면 `ollama serve`로 서버를 시작할 수 있습니다.

모델이 있는지 확인합니다:

```bash
ollama list
```

출력에서 `gpt-oss:20b`가 크기 및 마지막 수정 날짜와 함께 표시되어야 합니다.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->