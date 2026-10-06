<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hermes 설치하기

공식 설치 프로그램을 사용하여 Hermes 에이전트 CLI를 설치합니다. `--skip-setup` 플래그를 사용하면 설치를 무인(unattended) 방식으로 진행할 수 있습니다:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes는 `~/.local/bin`에 설치되므로, 해당 디렉터리가 `PATH`에 포함되어 있는지 확인하세요.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->