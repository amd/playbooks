<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio는 **AMD Ryzen™ AI 개발자 센터**에서 설치할 수 있습니다. **업데이트** 탭으로 이동하여 LM Studio가 설치되어 있지 않은 경우 설치하십시오.

LM Studio에서 사전 설치된 모델을 볼 수 있도록 하려면 설정 > 일반 > 모델 디렉터리로 이동하십시오. 그런 다음 경로를 `C:\Users\Public\models`로 변경하십시오.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. 여기에서 설치 프로그램을 다운로드하십시오: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. 설치하십시오.
<!-- @device:end -->

> 팁: 설치 후 LM Studio를 한 번 실행하여 CLI(`lms`)를 초기화하십시오.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> 참고: .deb 또는 AppImage 중 하나를 선택하여 설치할 수 있습니다.
1. 여기에서 AppImage를 다운로드하십시오: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. `sudo apt install libfuse2` 실행
3. `cd ~/Downloads` 실행
4. `chmod +x LM-Studio-*.AppImage` 실행
5. `./LM-Studio-*.AppImage` 실행
> 팁: 설치 후 LM Studio를 한 번 실행하여 CLI(`lms`)를 초기화하십시오.

<!-- @device:halo_box -->
LM Studio에서 사전 설치된 모델을 볼 수 있도록 하려면 설정 > 일반 > 모델 디렉터리로 이동하십시오. 그런 다음 경로를 `/var/cache/models`로 변경하십시오.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end -->
<!-- @os:end -->