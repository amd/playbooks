<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM은 ROCm을 지원하는 사전 빌드된 컨테이너 이미지 형태로 제공됩니다. 호스트에 vLLM이나 PyTorch를 직접 설치하는 대신 런처 명령을 사용하세요:

```bash
vllm-launch
```

이 런처는 컨테이너를 시작하고 내장 GPU를 대상으로 지정하여, `http://localhost:8001`에서 OpenAI 호환 vLLM API를 노출합니다.