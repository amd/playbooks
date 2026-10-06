<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### OpenClaw 설치하기

공식 설치 프로그램을 사용하여 OpenClaw를 설치합니다:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-prompt --no-onboard` 플래그는 대화형 설정 마법사를 건너뛰며, 이는 무인 설치에 필요합니다. 모델 백엔드는 별도로 구성됩니다.

> **팁:** 설치 후 `command not found`가 표시되면 npm의 전역 bin 디렉터리를 PATH에 추가하세요:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 이를 영구적으로 적용하려면 위 줄을 `~/.bashrc` 또는 `~/.zshrc` 파일에 추가하세요.

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->