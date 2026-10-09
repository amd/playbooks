<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4-cockpit 설치하기

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox)은 툴박스 컨테이너 생성, 모델 가중치 다운로드, 서버 시작을 처리하는 가벼운 터미널 UI입니다. `pipx`로 설치하세요:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx`는 진입점을 `~/.local/bin`에 설치합니다. 해당 디렉터리가 `PATH`에 포함되어 있는지 확인하세요.

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->