<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM은 ROCm 지원이 포함된 사전 빌드된 컨테이너 이미지를 통해 제공됩니다. 호스트에 vLLM 또는 PyTorch를 직접 설치하는 대신 런처 명령을 사용하십시오:

```bash
vllm-launch
```

런처는 컨테이너를 시작하고, 통합 GPU를 대상으로 하며, `http://localhost:8001`에서 OpenAI 호환 vLLM API를 노출합니다.