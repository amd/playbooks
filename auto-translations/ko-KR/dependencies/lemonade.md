<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonade 설치하기

<!-- @os:windows -->
[lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi)에서 최신 설치 프로그램을 다운로드하고 `.msi` 파일을 실행합니다.

설치 후:
- `lemonade` CLI가 시스템 PATH에 자동으로 추가됩니다
- Lemonade 서버가 백그라운드에서 자동으로 실행됩니다

명령줄에서 자동으로(무인) 설치할 수도 있습니다:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

다른 배포판을 사용하거나 소스에서 설치하려면 [전체 설치 옵션](https://lemonade-server.ai/docs/guide/install/)을 참조하세요.
<!-- @os:end -->


#### Lemonade 설치 확인하기

터미널을 열고 다음을 실행합니다:
```bash
lemonade --version
```

다음과 같은 출력이 표시됩니다:
```
lemonade version x.y.z
```

버전 번호가 표시되면 Lemonade가 올바르게 설치되어 사용할 준비가 된 것입니다.

빠른 참조를 위해 자주 사용하는 Lemonade CLI 명령어는 다음과 같습니다:

| 명령어 | 기능 |
| --- | --- |
| `lemonade --help` | 사용 가능한 모든 명령과 플래그를 표시합니다. |
| `lemonade --version` | 설치된 Lemonade 버전을 출력합니다. |
| `lemonade status` | Lemonade 서버가 실행 중이며 접근 가능한지 확인합니다. 기본 OpenAI 호환 API 기본 URL은 `http://localhost:13305/api/v1`입니다. |
| `lemonade list` | 현재 Lemonade 설정에서 사용 가능한 모델을 나열합니다. |
| `lemonade pull <MODEL_NAME>` | 모델을 실행하지 않고 다운로드합니다. |
| `lemonade run <MODEL_NAME>` | 필요한 경우 모델을 다운로드한 후 추론/채팅을 위해 시작합니다. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | ROCm 백엔드로 llama.cpp 모델을 시작합니다. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Vulkan 백엔드로 llama.cpp 모델을 시작합니다. |
| `lemonade config` | 현재 Lemonade 구성 값을 표시합니다. |
| `lemonade config set llamacpp.backend=rocm` | 기본 llama.cpp 백엔드를 ROCm으로 설정합니다. |

최신 Lemonade 서버 옵션이나 문제 해결에 대해서는 [공식 Lemonade 문서](https://lemonade-server.ai/docs/lemonade-cli/)를 참조하세요.