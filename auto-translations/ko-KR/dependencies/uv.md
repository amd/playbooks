<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### uv 설치하기

[uv](https://docs.astral.sh/uv/)는 Agent Canvas가 에이전트 서버 환경을 구축하는 데 사용하는 Python 패키지/환경 관리자입니다. 공식 스크립트로 설치하세요:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv`는 `~/.local/bin`에 설치되므로, 해당 디렉터리가 `PATH`에 포함되어 있는지 확인하세요.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->